import aiohttp_jinja2
from aiohttp.web import Response


@aiohttp_jinja2.template("index.html")
async def index(request):
    return {}
