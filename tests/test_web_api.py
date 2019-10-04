from aiohttp_dashboard._state import DEBUGGER_KEY, MsgDirection


async def test_statistics_requests_structure(aiohttp_client, aihttp_application):
    structure = ['id', 'scheme', 'stoptime', 'ip',
                 'responseheaders', 'status',
                 'reason', 'body', 'host', 'method', 'starttime']
    client = await aiohttp_client(aihttp_application)
    _response = await client.get('/test-http')

    request, *_ = aihttp_application[DEBUGGER_KEY]._requests.values()

    for key in structure:
        assert key in request.keys()


async def test_statistics_requests_number(aiohttp_client, aihttp_application):
    paths = ('/test-http-404', '/test-http') * 5
    client = await aiohttp_client(aihttp_application)

    for path in paths:
        await client.get(path)

    assert len(aihttp_application[DEBUGGER_KEY]._requests) == len(paths)


async def test_statistics_requests_status(aiohttp_client, aihttp_application):
    client = await aiohttp_client(aihttp_application)

    response_200 = await client.get('/test-http')
    response_404 = await client.get('/test-http-404')

    # just check for response status
    assert response_200.status == 200
    assert response_404.status == 404

    requests = aihttp_application[DEBUGGER_KEY]._requests.values()

    request_200 = next(_ for _ in requests if _['path'] == '/test-http')
    request_404 = next(_ for _ in requests if _['path'] == '/test-http-404')

    assert response_200.status == request_200['status']
    assert response_404.status == request_404['status']


# NOTE: do more complex equals case in separate function
async def test_statistics_requests_simple_equals(aiohttp_client, aihttp_application):
    client = await aiohttp_client(aihttp_application)

    response = await client.get('/test-http')
    response_statistics, *_ = aihttp_application[DEBUGGER_KEY]._requests.values()

    assert await response.text() == response_statistics['body']
    assert response.status == response_statistics['status']
    assert response.reason == response_statistics['reason']


async def test_websocket_messages_count_incoming(aiohttp_client, aihttp_application):
    client = await aiohttp_client(aihttp_application)
    websocket = await client.ws_connect('/test-websocket', receive_timeout=5)

    messages = ['Hello, World!']

    for message in messages:
        await websocket.send_json(message)
        await websocket.receive()

    http_response, *_ = \
        aihttp_application[DEBUGGER_KEY]._requests.values()
    length = aihttp_application[DEBUGGER_KEY].count_messages(
        http_response['id'], MsgDirection.INCOMING)

    assert length == len(messages)
    await websocket.close()


async def test_websocket_messages_count_outbound(aiohttp_client, aihttp_application):
    messages = ['Hello, World!'] * 20

    debugger = aihttp_application[DEBUGGER_KEY]
    client = await aiohttp_client(aihttp_application)
    websocket = await client.ws_connect('/test-websocket')

    for message in messages:
        await websocket.send_json(message)
        await websocket.receive()

    response, *_ = debugger._requests.values()

    assert len(messages) == debugger.count_messages(response['id'], MsgDirection.OUTBOUND)
    await websocket.close()


async def test_websocket_request_status(aiohttp_client, aihttp_application):
    client = await aiohttp_client(aihttp_application)
    websocket = await client.ws_connect('/test-websocket')

    payload = 'Hello, World!'

    await websocket.send_json(payload)
    await websocket.close()

    http_response, *_ = \
        aihttp_application[DEBUGGER_KEY]._requests.values()

    # I don't know how extract status code from ClientWebSocketResponse
    assert http_response['status'] == 101
