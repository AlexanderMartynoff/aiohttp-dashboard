import aiohttp_jinja2
from jinja2 import FileSystemLoader
from aiohttp.web import WebSocketResponse, Response
from functools import partial
from os.path import join, normpath, isabs

from .debugger import Debugger, DEBUGGER_KEY, JINJA_KEY
from .event import HttpRequest, HttpResponse, WsMsgIncoming, WsMsgOutbound, MsgDirection


def setup(name, application, routes, static_routes, static_path):
    application[DEBUGGER_KEY] = Debugger(name)

    _register_routes(application, routes)
    _register_static_routes(application, static_routes)

    application.middlewares.append(_factory_on_request)
    application.on_response_prepare.append(_on_response)

    aiohttp_jinja2.setup(
        application,
        loader=FileSystemLoader(static_path),
        app_key=JINJA_KEY)

    return application


def _register_routes(application, routes):
    for method, path, handler in routes:

        if isabs(path):
            raise RuntimeError('Path must be relative, not absolute')

        application.router.add_route(
            method, join(application[DEBUGGER_KEY].path, path), handler)


def _register_static_routes(application, routes):
    for url, path in routes:
        application.router.add_static(
            join(application[DEBUGGER_KEY].path, url), path)


async def _factory_on_request(application, handler):
    return partial(_on_request, handler=handler)


def _is_sutable_request(request):
    return not request.path.startswith(request.app[DEBUGGER_KEY].path)


async def _on_request(request, handler):
    if _is_sutable_request(request):
        request.app[DEBUGGER_KEY].register_request(request)

        try:
            return await handler(request)
        except Exception as exception:
            request.app[DEBUGGER_KEY].register_http_exception(request, exception)
            raise exception

    return await handler(request)


async def _on_response(request, response):
    if _is_sutable_request(request):
        request.app[DEBUGGER_KEY].register_response(request, response)

        if isinstance(response, WebSocketResponse):
            _ws_resposne_do_monkey_patch(request, response)


def _on_websocket_msg(direction, request, message):
    if _is_sutable_request(request):
        request.app[DEBUGGER_KEY].register_websocket_message(direction, request, message)


def _ws_resposne_do_monkey_patch(request, response):

    async def ping_monkey_patch(message):
        _on_websocket_msg(MsgDirection.INCOMING, request, message)
        return await original_ping(message)

    original_ping, response.ping = response.ping, ping_monkey_patch

    async def pong_monkey_patch(message):
        _on_websocket_msg(MsgDirection.INCOMING, request, message)
        return await original_pong(message)

    original_pong, response.pong = response.pong, pong_monkey_patch

    async def send_str_monkey_patch(data, compress=None):
        _on_websocket_msg(MsgDirection.INCOMING, request, data)
        return await original_send_str(data, compress)

    original_send_str, response.send_str = response.send_str, send_str_monkey_patch

    async def send_bytes_monkey_patch(data, compress=None):
        _on_websocket_msg(MsgDirection.INCOMING, request, data)
        return await original_send_bytes(data, compress)

    original_send_bytes, response.send_bytes = response.send_bytes, send_bytes_monkey_patch

    async def receive_monkey_patch(timeout=None):
        message = await original_receive(timeout)
        _on_websocket_msg(MsgDirection.OUTBOUND, request, message.data)

        return message

    original_receive, response.receive = response.receive, receive_monkey_patch
