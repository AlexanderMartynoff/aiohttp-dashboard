from aiohttp.test_utils import make_mocked_request
from aiohttp_dashboard._state import _slice, State, MsgDirection
from aiohttp_dashboard._setup import _factory_on_request, _on_response


def test_slice_offset():
    assert _slice([1, 2, 3, 4], 1, 2) == [2, 3]


def test_count_messages():
    state = State()
    request = make_mocked_request('GET', '/ws-connector')

    state.append_message(MsgDirection.INCOMING, request, b'message-1')
    state.append_message(MsgDirection.OUTBOUND, request, b'message-2')

    state.count_messages() == 2


def test_find_messages():
    state = State()
    request = make_mocked_request('GET', '/ws-connector')

    state.append_message(MsgDirection.INCOMING, request, b'message-1')
    state.append_message(MsgDirection.OUTBOUND, request, b'message-2')

    state.count_messages() == 2
