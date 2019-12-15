import aiohttp_jinja2
from jinja2 import FileSystemLoader
from aiohttp.web import WebSocketResponse, Response, RouteTableDef
from functools import partial
from os.path import join, normpath, isabs, dirname, abspath
import time


from ._state import DEBUGGER_KEY, JINJA_KEY, State
from ._event_emitter import EventEmitter
from ._misc import MsgDirection, QueueDict, timestamp


DEBUGGER_PREFIX_KEY = DEBUGGER_KEY + '-prefix'


def normalize_prefix(prefix):
    assert isabs(prefix), \
        ValueError('Prefix must be absoluste path')
    return normpath(prefix)


def setup(prefix, application, routes,
          static_routes, resource_paths, state):

    application[DEBUGGER_PREFIX_KEY] = prefix
    application[DEBUGGER_KEY] = State()

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
    return not request.path.startswith(request.app[DEBUGGER_PREFIX_KEY])


def _dump_request(request):
    _id = id(request)
    peername, _ = request.transport.get_extra_info('peername')

    return {
        'id': _id,
        'scheme': request.scheme,
        'host': request.host,
        'path': request.raw_path,
        'method': request.method,
        'starttime': timestamp(),
        'requestheaders': dict(request.headers),
        'peername': peername,
    }


def _dump_response(request, response):
    _id = id(request)
    body = response.text if isinstance(
        response, Response) else None
    websocket = True if isinstance(
        response, WebSocketResponse) else False

    return {
        'id': _id,
        'stoptime': timestamp(),
        'responseheaders': dict(response.headers),
        'status': response.status,
        'reason': response.reason,
        'body': body,
        'websocket': websocket,
    }


def _dump_request_error(message):
    return {}


def _dump_message(message):
    return {}


async def _on_request(request, handler):
    if _is_sutable_request(request):
        state = request.app[DEBUGGER_KEY]
        record = _dump_request(request)

        state.add_request(record)

        state.emitter.fire('http.request', {
            'request': record['id'],
        })

        state.emitter.fire('http', {
            'request': record['id'],
        })

        try:
            return await handler(request)
        except Exception as exception:
            request.app[DEBUGGER_KEY].add_request_error(
                request, exception)
            raise exception

    return await handler(request)


async def _on_response(request, response):
    if _is_sutable_request(request):
        state = request.app[DEBUGGER_KEY]
        record = _dump_response(request, response)

        state.add_response(record)

        state.emitter.fire('http.response', {
            'request': record['id'],
        })

        state.emitter.fire('http', {
            'request': record['id'],
        })

        if isinstance(response, WebSocketResponse):
            _ws_resposne_decorate(request, response)


def _on_websocket_msg(direction, request, message):
    if _is_sutable_request(request):
        request.app[DEBUGGER_KEY].add_message(
            direction, request, message)


def _ws_resposne_decorate(request, response):
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

    send_bytes, response.send_bytes = response.send_bytes, send_bytes_decorator

    async def receive_decorator(timeout=None):
        message = await receive(timeout)
        _on_websocket_msg(MsgDirection.INCOMING, request, message.data)

        return message

    receive, response.receive = response.receive, receive_decorator
