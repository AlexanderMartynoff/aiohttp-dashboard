from aiohttp_dashboard.core import DEBUGGER_KEY


async def test_statistics_requests_structure(aiohttp_client, aihttp_application):
    structure = ['id', 'scheme', 'donetime', 'ip', 'done',
                 'resheaders', 'status', 'iswebsocket',
                 'reason', 'body', 'host', 'method', 'begintime']
    client = await aiohttp_client(aihttp_application)
    await client.get('/test-http')

    requests, *_ = aihttp_application[DEBUGGER_KEY].state.requests.values()

    for key in structure:
        assert key in requests.keys()


async def test_statistics_requests_number(aiohttp_client, aihttp_application):
    paths = ('/test-http-404', '/test-http') * 5
    client = await aiohttp_client(aihttp_application)

    for path in paths:
        await client.get(path)

    assert len(aihttp_application[DEBUGGER_KEY].state.requests.values()) == len(paths)


async def test_statistics_requests_status(aiohttp_client, aihttp_application):
    client = await aiohttp_client(aihttp_application)

    response_200 = await client.get('/test-http')
    response_404 = await client.get('/test-http-404')

    # just check for response status
    assert response_200.status == 200
    assert response_404.status == 404

    statistics = aihttp_application[DEBUGGER_KEY].state.requests.values()

    statistics_200 = next(statistic for statistic in statistics if statistic['path'] == '/test-http')
    statistics_404 = next(statistic for statistic in statistics if statistic['path'] == '/test-http-404')

    assert response_200.status == statistics_200['status']
    assert response_404.status == statistics_404['status']


# NOTE: do more complex equals case in separate function
async def test_statistics_requests_simple_equals(aiohttp_client, aihttp_application):
    client = await aiohttp_client(aihttp_application)

    response = await client.get('/test-http')
    response_statistics, *_ = aihttp_application[DEBUGGER_KEY].state.requests.values()

    assert await response.text() == response_statistics['body']
    assert response.status == response_statistics['status']
    assert response.reason == response_statistics['reason']
    assert response_statistics['done']
