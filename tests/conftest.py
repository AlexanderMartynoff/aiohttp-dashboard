import pytest
import aiohttp
import aiohttp_dashboard


@pytest.fixture
def prefix():
    return '_debugger'


@pytest.fixture
def aihttp_application(prefix):

    async def http_handler(request):
        return aiohttp.web.Response(text='Hello, World!')

    async def websocket_handler(request):
        websocket = aiohttp.web.WebSocketResponse()

        await websocket.prepare(request)

        async for message in websocket:
            await websocket.send_json(message)

        return websocket

    application = aiohttp.web.Application()

    application.router.add_get('/test-http', http_handler)
    application.router.add_get('/test-websocket', websocket_handler)
    application.router.add_get(
        '/test-websocket/return/{return}', websocket_handler)

    aiohttp_dashboard.setup(prefix, application)

    return application
