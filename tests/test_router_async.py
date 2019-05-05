import pytest
from aiohttp_dashboard._router import Router, route, RouteNotFoundError


async def test_route_async():
    class Controller(Router.Async):

        @route('/async')
        async def async_hello_world(self, true):
            return true

        @route('/sync')
        def sync_hello_world(self, true):
            return true

    controller = Controller()

    assert await controller.router('/async', True) is True
    assert await controller.router('/sync', True) is True


async def test_route_async_error():

    class CatchError(Exception):
        pass

    class NotCatchError(Exception):
        pass

    class Controller(Router.Async):

        @route('/catch')
        async def catch(self):
            raise CatchError

        @route('/not-catch')
        async def not_catch(self):
            raise NotCatchError

        @route.error(CatchError)
        async def error(self, _error):
            return 'catch'

    controller = Controller()

    assert await controller.router('/catch') == 'catch'

    with pytest.raises(NotCatchError):
        await controller.router('/not-catch')

    with pytest.raises(RouteNotFoundError):
        await controller.router('/not-found')
