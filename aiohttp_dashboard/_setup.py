import aiohttp_jinja2
from jinja2 import FileSystemLoader
from aiohttp.web import WebSocketResponse, Response, RouteTableDef, Request
from functools import partial
from os.path import join, normpath, isabs, dirname, abspath
from asyncio import ensure_future, wait_for

from ._state import DEBUGGER_KEY, JINJA_KEY, State
from ._misc import MsgDirection, uuid_


DEBUGGER_PREFIX_KEY = DEBUGGER_KEY + '-prefix'


def normalize_prefix(prefix):
    assert isabs(prefix), \
        ValueError('Prefix must be absoluste path')
    return normpath(prefix)


def setup(prefix, application, routes,
          static_routes, resource_paths, config):

    application[DEBUGGER_PREFIX_KEY] = prefix
    application[DEBUGGER_KEY] = State(config)

    _setup_routes(application, routes)
    _setup_static_routes(application, static_routes)

    application.middlewares.append(_factory_on_request)
    application.on_response_prepare.append(_on_response)

    aiohttp_jinja2.setup(
        application,
        loader=FileSystemLoader(resource_paths),
        app_key=JINJA_KEY
    )

    return application


def _setup_routes(application, routes):
    for method, fragment_path, handler in routes:
        application.router.add_route(method, fragment_path, handler)


def _setup_static_routes(application, routes):
    for path, location in routes:
        application.router.add_static(path, location)


async def _factory_on_request(application, handler):
    return partial(_on_request, handler=handler)


def _is_sutable_request(request):
    return not request.path.startswith(
        request.app[DEBUGGER_PREFIX_KEY])


async def _add_request_error(request, error):
    state = request.app[DEBUGGER_KEY]
    _error_id = await state.api_error.add(  # noqa
        request, error)


async def _on_request(request, handler):
    if _is_sutable_request(request):
        state = request.app[DEBUGGER_KEY]
        ensure_future(
            state.api_request.add(request))

        try:
            return await handler(request)
        except Exception as error:
            ensure_future(
                _add_request_error(request, error))
            raise error

    return await handler(request)


async def _add_response(request, response):
    state = request.app[DEBUGGER_KEY]
    await state.api_request.put_response(request, response)

    if isinstance(response, WebSocketResponse):
        _ws_resposne_decorate(request, response)


async def _on_response(request, response):
    if _is_sutable_request(request):
        ensure_future(
            _add_response(request, response))


async def _add_websocket_msg(direction, request, message):
    state = request.app[DEBUGGER_KEY]
    ensure_future(
        state.api_message.add(direction, request, message))


def _on_websocket_msg(direction, request, message):
    if _is_sutable_request(request):
        ensure_future(
            _add_websocket_msg(direction, request, message))


def _ws_resposne_decorate(request, response):
    """ Apply monkey patching for some methods of `response` object
        for call `_on_websocket_msg` hook when message will received
        or sended.
    """

    async def ping_decorator(message):
        _on_websocket_msg(MsgDirection.OUTBOUND, request, message)
        return await ping(message)

    ping, response.ping = response.ping, ping_decorator

    async def pong_decorator(message):
        _on_websocket_msg(MsgDirection.OUTBOUND, request, message)
        return await pong(message)

    pong, response.pong = response.pong, pong_decorator

    async def send_str_decorator(data, compress=None):
        _on_websocket_msg(MsgDirection.OUTBOUND, request, data)
        return await send_str(data, compress)

    send_str, response.send_str = response.send_str, send_str_decorator

    async def send_bytes_decorator(data, compress=None):
        _on_websocket_msg(MsgDirection.OUTBOUND, request, data)
        return await send_bytes(data, compress)

    send_bytes, response.send_bytes = \
        response.send_bytes, send_bytes_decorator

    async def receive_decorator(timeout=None):
        message = await receive(timeout)
        _on_websocket_msg(
            MsgDirection.INCOMING, request, message.data)

        return message

    receive, response.receive = response.receive, receive_decorator
