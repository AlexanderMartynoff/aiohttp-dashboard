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


def test_arguments():

    class Controller(Router):
        
        @route('/number')
        def hello_world(self, first=None, second=None):
            return first, second

    controller = Controller()

    assert controller.router('/number', 0) == (0, None)
    assert controller.router('/number', second=0) == (None, 0)
    assert controller.router('/number') == (None, None)
    assert controller.router('/number', 0, 0) == (0, 0)


def test_default():

    class Controller(Router):
        
        @route.default
        def default(self):
            return 'default'

    controller = Controller()

    assert controller.router('/404') == 'default'


def test_default_with_arguments():

    class Controller(Router):
        
        @route.default
        def default(self, argument):
            return argument

    controller = Controller()

    assert controller.router('/404', 'default') == 'default'


def test_route_without_default():

    class Controller(Router):
        pass

    controller = Controller()

    with pytest.raises(RouteNotFoundError):
        controller.router('/not-found')


def test_routes_length():

    class Controller(Router):
        
        def hello_world(self):
            pass

        @route('/1')
        def _1(self):
            pass

        @route('/2')
        def _2(self):
            pass

        @route('/3')
        def _3(self):
            pass

    assert len(Controller().routes) == 3


def test_route_error():

    class Controller(Router):
        
        @route('/hello-world')
        def hello_world(self):
            raise Exception

        @route.error(Exception)
        def error(self, error):
            return 'error'

    controller = Controller()
    
    assert controller.router('/hello-world') == 'error'
