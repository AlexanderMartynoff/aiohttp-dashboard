import aiohttp_jinja2
from jinja2 import FileSystemLoader
from aiohttp.web import WebSocketResponse, Response
from functools import partial

from .debugger import Debugger, DEBUGGER_KEY, JINJA_KEY
from .event import (HttpRequest, HttpResponse,
                    WsMsgIncoming, WsMsgOutbound, MsgDirection)


def setup(prefix, application, routes, static_routes, debugger_dir):
    application[DEBUGGER_KEY] = Debugger()
    
    _register_routes(application, routes)
    _register_static_routes(application, static_routes)

    application.middlewares.append(_factory_on_request)
    application.on_response_prepare.append(_on_response)

    aiohttp_jinja2.setup(application,
        loader=FileSystemLoader(f"{debugger_dir}/static"),
        app_key=JINJA_KEY)

    return application


def _register_routes(application, routes):
    for method, path, handler in routes:
        application.router.add_route(method, path, handler)


def _register_static_routes(application, routes):
    for url, path in routes:
        application.router.add_static(url, path)


async def _factory_on_request(application, handler):
    return partial(_on_request, handler=handler)


def _is_sutable_request(request):
    return not request.path.startswith("/_debugger")


async def _on_request(request, handler):
    if _is_sutable_request(request):
        request.app[DEBUGGER_KEY].register_request(request)

    return await handler(request)


async def _on_response(request, response):
    if _is_sutable_request(request):
        request.app[DEBUGGER_KEY].register_response(request, response)

        if isinstance(response, WebSocketResponse):
            _ws_resposne_do_monkey_patching(request, response)


def _on_websocket_msg(direction, request, message, event):
    if _is_sutable_request(request):
        request.app[DEBUGGER_KEY].register_websocket_message(direction, request, message, event)


def _ws_resposne_do_monkey_patching(request, response):

    INCOMING, OUTBOUND = MsgDirection.INCOMING, MsgDirection.OUTBOUND

    async def ping_overload(message):
        _on_websocket_msg(INCOMING, request, message, WsMsgOutbound())
        return await response.__aiohttp_debugger_ping__(message)

    # NOTE: не сохранять оригинальные версии как поля response
    # просто за счет замыкания можно сделать
    response.__aiohttp_debugger_ping__ = response.ping
    response.ping = ping_overload

    async def pong_overload(message):
        _on_websocket_msg(INCOMING, request, message, WsMsgOutbound())
        return await response.__aiohttp_debugger_pong__(message)

    response.__aiohttp_debugger_pong__ = response.pong
    response.pong = pong_overload

    async def send_str_overload(data, compress=None):
        _on_websocket_msg(INCOMING, request, data, WsMsgOutbound())
        return await response.__aiohttp_debugger_send_str__(data, compress)

    response.__aiohttp_debugger_send_str__ = response.send_str
    response.send_str = send_str_overload

    async def send_bytes_overload(data, compress=None):
        _on_websocket_msg(INCOMING, request, data, WsMsgOutbound())
        return await response.__aiohttp_debugger_send_str__(data, compress)

    response.__aiohttp_debugger_send_bytes__ = response.send_bytes
    response.send_bytes = send_bytes_overload

    async def receive_overload(timeout=None):
        message = await response.__aiohttp_debugger_receive__(timeout)
        _on_websocket_msg(OUTBOUND, request, message.data, WsMsgIncoming())
        return message

    response.__aiohttp_debugger_receive__ = response.receive
    response.receive = receive_overload
