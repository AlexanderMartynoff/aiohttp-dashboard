from aiohttp import hdrs
from aiohttp_jinja2 import template
from aiohttp.web import Response, WebSocketResponse
from asyncio import ensure_future, sleep
from functools import wraps
from uuid import uuid4
import os
import logging
from urllib.parse import urlparse
import yarl
import time

from .endpoint import WsMsgDispatcherProxy
from .helper import WsResponseHelper
from .debugger import DEBUGGER_KEY, JINJA_KEY


logger = logging.getLogger(__name__)
application_path = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(application_path, 'static')


@template('index.html', app_key=JINJA_KEY)
async def index(request):
    debugger = request.app[DEBUGGER_KEY]

    endpoint_scheme = 'wss' if request.secure else 'ws'
    endpoint_path = os.path.join(debugger.path, 'api')

    return {
        'timestamp': time.time(),
        'name': debugger.name,
        'endpoint': yarl.URL.build(
            scheme=endpoint_scheme,
            host=request.url.host,
            port=request.url.port,
            path=endpoint_path,
        ),
    }


async def api(request):
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

# thus routes must be relative
# because they will join with dashboard name
routes = (
    (hdrs.METH_GET, 'api', api),
    (hdrs.METH_GET, 'index', index),
)

static_routes = (
    ('static', static_path),
)
