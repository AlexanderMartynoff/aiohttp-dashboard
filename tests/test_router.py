from asyncio import sleep
from aiohttp_dashboard.core import DEBUGGER_KEY
from aiohttp_dashboard.router import Router, route, RouteNotFoundError
import pytest


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

    assert controller.router('/404', 'default') is 'default'


def test_route_without_default():

    class Controller(Router):
        pass

    controller = Controller()

    with pytest.raises(RouteNotFoundError):
        controller.router('/not-found')


def test_routes_length():

    class Controller(Router):

        @route('/1')
        def _1(self):
            pass

        @route('/2')
        def _2(self):
            pass

        @route('/3')
        def _3(self):
            pass

        def _0(self):
            pass

    assert len(Controller().routes) == 3


def test_route_error():

    class CatchError(Exception):
        pass

    class UncatchError(Exception):
        pass

    class Controller(Router):

        @route('/catch')
        def catch(self):
            raise CatchError

        @route('/uncatch')
        def uncatch(self):
            raise UncatchError

        @route.error(CatchError)
        def error(self, _error):
            return 'catch'

    controller = Controller()

    assert controller.router('/catch') == 'catch'

    with pytest.raises(UncatchError):
        controller.router('/uncatch')
