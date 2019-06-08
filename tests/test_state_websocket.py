import json
from aiohttp_dashboard._state import DEBUGGER_KEY, MsgDirection


async def test_websocket_messages_count_incoming(aiohttp_client, aihttp_application):
    client = await aiohttp_client(aihttp_application)
    websocket = await client.ws_connect('/test-websocket', receive_timeout=5)

    messages = ['Hello, World!'] * 30

    for message in messages:
        await websocket.send_json(message)
        await websocket.receive()

    await websocket.close()

    http_response, *_ = aihttp_application[DEBUGGER_KEY]._http_requests
    messages_count = aihttp_application[DEBUGGER_KEY].count_ws_messages(
        http_response['id'], MsgDirection.INCOMING)

    assert messages_count == len(messages)


async def test_websocket_messages_count_outbound(aiohttp_client, aihttp_application):
    messages = ['Hello, World!'] * 20

    debugger = aihttp_application[DEBUGGER_KEY]
    client = await aiohttp_client(aihttp_application)
    websocket = await client.ws_connect('/test-websocket')

    for message in messages:
        await websocket.send_json(message)

    await websocket.close()

    response, *_ = debugger._http_requests

    # When counting the number of messages, we must take into account the message with the code 1001,
    # which is sent when the connection is closed - `await websocket.close()`
    assert len(messages) + 1 == debugger.count_ws_messages(response['id'], MsgDirection.OUTBOUND)


async def test_websocket_messages_strucutre(aiohttp_client, aihttp_application):
    client = await aiohttp_client(aihttp_application)
    websocket = await client.ws_connect('/test-websocket')

    message = 'Hello, World!'

    await websocket.send_json(message)
    await websocket.close()

    debugger = aihttp_application[DEBUGGER_KEY]

    http_response, *_ = debugger._http_requests

    websocket_message = next(_ for _ in debugger.find_ws_messages(
        http_response['id']) if json.loads(str(_['message'])) == message)

    for key in 'id', 'message', 'time', 'direction':
        assert key in websocket_message.keys()


async def test_websocket_request_status(aiohttp_client, aihttp_application):
    client = await aiohttp_client(aihttp_application)
    websocket = await client.ws_connect('/test-websocket')

    payload = 'Hello, World!'

    await websocket.send_json(payload)
    await websocket.close()

    http_response, *_ = aihttp_application[DEBUGGER_KEY]._http_requests

    # I don't know how extract status code from ClientWebSocketResponse
    assert http_response['status'] == 101
