from os.path import join
from aiohttp_dashboard._core import DEBUGGER_KEY
from aiohttp_dashboard._setup import _factory_on_request, _on_response


def test_debugger(aihttp_application):
    """ Test for registration Debugger in application """

    assert DEBUGGER_KEY in aihttp_application.keys()


def test_middlewares(aihttp_application):
    """ Test for registration middlewares in application """

    assert _factory_on_request in aihttp_application.middlewares


def test_signals(aihttp_application):
    """ Test for registration signals in application """

    assert _on_response in aihttp_application.on_response_prepare
