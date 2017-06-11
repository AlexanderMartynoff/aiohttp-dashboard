from aiohttp import web
from aiohttp_debugger import Debugger
from pytest import fixture
from aiohttp_debugger.helper import WsResponseHelper
import asyncio


@fixture
def application():

    async def index(request):
        return web.Response(text='Hello, world!')

    async def socket(request):
        response = await WsResponseHelper.instance(request)
        for message in response: pass
        return response

    application = web.Application()
    application.router.add_get('/index', index)
    application.router.add_get('/socket', socket)

    Debugger.setup(application)

    return application
