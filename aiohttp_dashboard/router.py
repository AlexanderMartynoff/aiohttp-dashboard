"""
Used for websocket message dispatching
======================================

*Examples*
**********

.. code-block:: python
    
    >>> class Controller(Router):
    >>>    @route('/')
    >>>    def index(self, argument):
    >>>        return argument

    >>> controller = Controller()

    >>> assert controller.router('/', 'Hello, World!') == 'Hello, World!'
"""


from functools import update_wrapper
from inspect import iscoroutinefunction, iscoroutine
from asyncio import ensure_future, Future

from .helper import to_list


class Router:

    def router(self, name, *args, **kwargs):
        try:
            return self._router(name, *args, **kwargs)
        except RouteNotFoundError:
            return self.default_route(*args, **kwargs)
        except Exception as error:
            return self.error_route(error)

    def _router(self, name, *args, **kwargs):
        for route in self.routes:
            if route._name == name:
                return route(self, *args, **kwargs)

        raise RouteNotFoundError

    @property
    def routes(self):
        """
        Return all routes registering on this class
        """

        IGNORED = ['routes']

        # NOTE: reFUCKt!
        # NOTE: for fix RecursionError - ignore routes methods
        return [member for member in [getattr(self, name) for name in dir(self) if name not in IGNORED] if isinstance(member, _Route)]

    def default_route(self, *args, **kwargs):
        for route in self.routes:
            if isinstance(route, _DefaultRoute):
                return route(self, *args, **kwargs)

        raise RouteNotFoundError

    def error_route(self, error):
        for route in self.routes:
            if isinstance(route, _ErrorRoute) and type(error) in route._error_types:
                return route(self, error)

        raise error


class AsyncRouter(Router):
    async def router(self, name, *args, **kwargs):

        try:
            return await self._ensure_coroutine(self._router(name, *args, **kwargs))
        except RouteNotFoundError:
            return await self._ensure_coroutine(self.default_route(*args, **kwargs))
        except Exception as error:
            return await self._ensure_coroutine(self.error_route(error))

    def _ensure_coroutine(self, coroutine):

        async def ensure_coroutine(coroutine):
            return await coroutine if iscoroutine(coroutine) else coroutine

        return ensure_coroutine(coroutine)


def route(name):
    def decorator(handler):
        return update_wrapper(_Route(name, handler), handler)
    return decorator


def default(handler):
    return update_wrapper(_DefaultRoute(handler), handler)


def error(*types):
    def decorator(handler):
        return update_wrapper(_ErrorRoute(to_list(types), handler), handler)
    return decorator


# shortcuts
route.default = default
route.error = error
Router.Async = AsyncRouter


class _Route:
    _name = None
    _handler = None

    def __init__(self, name, handler):
        self._name = name
        self._handler = handler

    def __call__(self, *args, **kwargs):
        return self._handler(*args, **kwargs)


class _DefaultRoute(_Route):
    def __init__(self, handler):
        super().__init__(None, handler)


class _ErrorRoute(_Route):
    _error_types = None

    def __init__(self, error_types, handler):
        super().__init__(None, handler)
        self._error_types = error_types


class RouterError(Exception):
    pass


class RouteNotFoundError(RouterError):
    pass
