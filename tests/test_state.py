from aiohttp_dashboard._state import _slice
from aiohttp_dashboard._setup import _factory_on_request, _on_response


def test_slice_offset():
    assert _slice([1, 2, 3, 4], 1, 2) == [2, 3]


def test_state_http_requests():
    pass
