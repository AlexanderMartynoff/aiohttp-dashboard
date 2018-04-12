import pytest
import aiohttp.web
from aiohttp_debugger.debugger import DEBUGGER_KEY
from aiohttp_debugger.router import Router, route, RouteNotFoundError


def test_routing():

    class Controller(Router):
        
        @route('/hello-world')
        def hello_world(self):
            return 'Hello, World!'

        @route('/self')
        def self(self):
            return self
            
    controller = Controller()

    assert controller.router('/self') == controller
    assert controller.router('/hello-world') == 'Hello, World!'


def test_argsuments_transfer():

    class Controller(Router):
        
        @route('/number')
        def hello_world(self, first=None, second=None):
            return (first, second)

    controller = Controller()

    assert controller.router('/number', 0) == (0, None)
    assert controller.router('/number', second=0) == (None, 0)
    assert controller.router('/number') == (None, None)


def test_route_not_found():

    class Controller(Router):
        pass

    controller = Controller()

    with pytest.raises(RouteNotFoundError):
        controller.router('/not-found')

