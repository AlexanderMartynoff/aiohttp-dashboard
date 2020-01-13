""" Application for demonstration how `aiohttp_dashboard` work.
"""

from aiohttp.web import (
    RouteTableDef,
    Application,
    Response,
    WebSocketResponse,
    run_app,
)
from asyncio import sleep
import aiohttp_jinja2
import jinja2
import aiohttp_dashboard
from os.path import dirname, abspath


app = Application()
route = RouteTableDef()


@route.get('/')
@aiohttp_jinja2.template('index.html')
async def index(request):
    return {}


@route.get('/demo-html')
@route.post('/demo-html')
@route.delete('/demo-html')
async def html(request):
    return Response(body=b'Hello, World!')


@route.get('/demo-websocket')
async def websocket(request):
    websocket = WebSocketResponse()

    await websocket.prepare(request)

    async for message in websocket:
        await websocket.send_str(message.data)

    return websocket


app.add_routes(route)

aiohttp_dashboard.setup(
    '/dashboard',
    app,
    {
        'mongo': {
            'database': 'aiohttp-dashboard-sandbox',
        }
    }
)

aiohttp_jinja2.setup(
    app,
    loader=jinja2.FileSystemLoader(dirname(abspath(__file__))),
)

if __name__ == '__main__':
    run_app(app, port=8080)
