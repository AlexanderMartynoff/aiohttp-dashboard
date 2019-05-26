from os.path import join
from aiohttp_dashboard._state import DEBUGGER_KEY
from aiohttp_dashboard._setup import _factory_on_request, _on_response


def test_debugger(aihttp_application):
    assert DEBUGGER_KEY in aihttp_application.keys()


def test_middlewares(aihttp_application):
    assert _factory_on_request in aihttp_application.middlewares


def test_signals(aihttp_application):
    assert _on_response in aihttp_application.on_response_prepare
