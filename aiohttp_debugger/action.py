from aiohttp import hdrs
from aiohttp_jinja2 import template
from aiohttp.web import Response, WebSocketResponse
from asyncio import ensure_future, sleep
from .helper import WsResponseHelper
from . import api
from uuid import uuid4
import os

debugger_dir = os.path.dirname(os.path.abspath(__file__))


@template('index.html')
async def dashboard(request):
    return dict(nocache=hash(uuid4()))


async def websocket(request):
    response = await WsResponseHelper.instance(request)
    sender = api.Sender(response)
    proxy = api.WsMsgDispatcherProxy(api.WsMsgDispatcher(sender), sender)

    async for msg in response:
        ensure_future(proxy.recive(msg))

    proxy.close()
    return response


routes = (
    (hdrs.METH_GET, '/_debugger/ws/api', websocket),
    (hdrs.METH_GET, '/_debugger/dashboard', dashboard)
)

static_routes = (
    ('/_debugger/static', f'{debugger_dir}/static'),
)
