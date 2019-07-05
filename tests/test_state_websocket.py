import json
from aiohttp_dashboard._state import DEBUGGER_KEY, MsgDirection


async def test_websocket_messages_count_incoming(aiohttp_client, aihttp_application):
    client = await aiohttp_client(aihttp_application)
    websocket = await client.ws_connect('/test-websocket', receive_timeout=5)

    messages = ['Hello, World!']

    for message in messages:
        await websocket.send_json(message)
        await websocket.receive()

    http_response, *_ = \
        aihttp_application[DEBUGGER_KEY]._http_requests.values()
    length = aihttp_application[DEBUGGER_KEY].count_ws_messages(
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

    response, *_ = debugger._http_requests.values()

    assert len(messages) == debugger.count_ws_messages(response['id'], MsgDirection.OUTBOUND)
    await websocket.close()


async def test_websocket_request_status(aiohttp_client, aihttp_application):
    client = await aiohttp_client(aihttp_application)
    websocket = await client.ws_connect('/test-websocket')

    payload = 'Hello, World!'

    await websocket.send_json(payload)
    await websocket.close()

    http_response, *_ = \
        aihttp_application[DEBUGGER_KEY]._http_requests.values()

    # I don't know how extract status code from ClientWebSocketResponse
    assert http_response['status'] == 101
