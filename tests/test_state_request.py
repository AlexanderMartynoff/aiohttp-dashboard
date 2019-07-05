from aiohttp_dashboard._state import DEBUGGER_KEY


async def test_statistics_requests_structure(aiohttp_client, aihttp_application):
    structure = ['id', 'scheme', 'stoptime', 'ip',
                 'responseheaders', 'status',
                 'reason', 'body', 'host', 'method', 'starttime']
    client = await aiohttp_client(aihttp_application)
    _response = await client.get('/test-http')

    requests, *_ = aihttp_application[DEBUGGER_KEY]._http_requests.values()

    for key in structure:
        assert key in requests.keys()


async def test_statistics_requests_number(aiohttp_client, aihttp_application):
    paths = ('/test-http-404', '/test-http') * 5
    client = await aiohttp_client(aihttp_application)

    for path in paths:
        await client.get(path)

    assert len(aihttp_application[DEBUGGER_KEY]._http_requests) == len(paths)


async def test_statistics_requests_status(aiohttp_client, aihttp_application):
    client = await aiohttp_client(aihttp_application)

    response_200 = await client.get('/test-http')
    response_404 = await client.get('/test-http-404')

    # just check for response status
    assert response_200.status == 200
    assert response_404.status == 404

    requests = aihttp_application[DEBUGGER_KEY]._http_requests.values()

    request_200 = next(_ for _ in requests if _['path'] == '/test-http')
    request_404 = next(_ for _ in requests if _['path'] == '/test-http-404')

    assert response_200.status == request_200['status']
    assert response_404.status == request_404['status']


# NOTE: do more complex equals case in separate function
async def test_statistics_requests_simple_equals(aiohttp_client, aihttp_application):
    client = await aiohttp_client(aihttp_application)

    response = await client.get('/test-http')
    response_statistics, *_ = aihttp_application[DEBUGGER_KEY]._http_requests.values()

    assert await response.text() == response_statistics['body']
    assert response.status == response_statistics['status']
    assert response.reason == response_statistics['reason']
