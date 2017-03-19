from aiohttp.web import Application, Response
from asyncio import get_event_loop, wait_for, ensure_future
import os
import aiohttp_jinja2
import jinja2
from . import controller
from .debugger import Debugger


this_dir = os.path.dirname(os.path.abspath(__file__))
application = Application()

Debugger.instance(application)


aiohttp_jinja2.setup(
    application,
    loader=jinja2.FileSystemLoader(f"{this_dir}/static")
)

application.router.add_get("/", controller.index)
application.router.add_static("/static", f"{this_dir}/static")
