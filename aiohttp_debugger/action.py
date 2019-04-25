from aiohttp import hdrs
from aiohttp_jinja2 import template
from aiohttp.web import Response, WebSocketResponse
from asyncio import ensure_future, sleep
from functools import wraps
from uuid import uuid4
import os
import logging

from .endpoint import WsMsgDispatcherProxy
from .helper import WsResponseHelper
from .debugger import DEBUGGER_KEY, JINJA_KEY


logger = logging.getLogger("aiohttp_debugger.debugger")
debugger_dir = os.path.dirname(os.path.abspath(__file__))


@template('index.html', app_key=JINJA_KEY)
async def dashboard(request):
    return {'id': hash(uuid4())}


async def websocket(request):
    debugger = request.app[DEBUGGER_KEY]

    socket = await WsResponseHelper.instance(request)
    proxy = WsMsgDispatcherProxy(socket, debugger, request)

    try:
        async for message in socket:
            proxy.recive(message)
    except Exception:
        logger.exception('An error occurred during execution')
    finally:
        proxy.close()

    return socket


routes = (
    (hdrs.METH_GET, '/_debugger/ws/api', websocket),
    (hdrs.METH_GET, '/_debugger/dashboard', dashboard)
)

static_routes = (
    ('/_debugger/static', f'{debugger_dir}/static'),
)
