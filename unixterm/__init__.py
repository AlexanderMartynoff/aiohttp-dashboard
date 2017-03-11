from aiohttp.web import Application, Response
from asyncio import get_event_loop, wait_for, ensure_future
import os
import aiohttp_jinja2
import jinja2


dir = os.path.dirname(os.path.abspath(__file__))
application = Application()

aiohttp_jinja2.setup(application, loader=jinja2.FileSystemLoader(f"{dir}/static"))


@aiohttp_jinja2.template("index.html")
def index(request):
    return {}

def grid_data(request):
    return Response(body=str())


application.router.add_get("/", index)
application.router.add_static("/static", f"{dir}/static")
