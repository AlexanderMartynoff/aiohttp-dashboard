from aiohttp import web
from aiohttp_debugger import Debugger
from pytest import fixture


@fixture
def application():

    async def index(request):
        return web.Response(text='Hello, world')

    application = web.Application()
    application.router.add_get('/index', index)

    Debugger.setup(application)

    return application


async def test_debugger_requests(test_client, application):
    client = await test_client(application)
    response_one = await client.get('/index')
    response_two = await client.get('/404')

    log_records = Debugger.instance.api.requests()

    assert len(log_records) == 2

    index_record, not_found_record = log_records

    assert index_record['path'] == '/index'
    assert not_found_record['path'] == '/404'
