import logging
import time
from aiohttp_jinja2 import template

from ._endpoint import MessageRouter
from ._misc import WsResponseHelper
from ._state import DEBUGGER_KEY, JINJA_KEY
from ._setup import endpoint_for_request


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
    socket = await WsResponseHelper.instance(request)
    router = MessageRouter(socket, request)

    try:
        async for message in socket:
            router.router(message.endpoint, message)
    except Exception:
        logger.exception('An error occurred during execution')
    finally:
        router.off()

    return socket
