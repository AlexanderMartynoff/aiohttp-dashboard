from aiohttp_jinja2 import template
import logging
import time

from .endpoint import WsMsgDispatcherProxy
from .helper import WsResponseHelper
from .core import DEBUGGER_KEY, JINJA_KEY
from .embedding import endpoint_for_request


logger = logging.getLogger(__name__)


@template('index.html', app_key=JINJA_KEY)
async def index(request):
    debugger = request.app[DEBUGGER_KEY]

    return {
        'timestamp': time.time(),
        'name': debugger.name,
        'endpoint': endpoint_for_request(request),
    }


async def endpoint(request):
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
