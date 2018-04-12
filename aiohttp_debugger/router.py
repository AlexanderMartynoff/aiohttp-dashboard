"""
Used for websocket message dispatching
======================================

*Examples*
**********

.. code-block:: python
    
    class Controller(Router):

        @route('/')
        def index(self, argument):
            return argument

    controller = Controller()

    assert controller.router('/', 'Hello, World!') == 'Hello, World!'
"""


from functools import update_wrapper


class Router:
    
    def router(self, name, *args, **kwargs):
        
        for attribute_name in dir(self):
            attribute = getattr(self, attribute_name)

            if isinstance(attribute, _Handler) and attribute._name == name:
                return attribute(self, *args, **kwargs)

        raise RouteNotFoundError(f'Route by name {name} was not found')

    @property
    def _routes(self):
        return [attribute for attribute in dir(self) if isinstance(attribute, _Handler)]

def route(name):
    
    def decorator(handler):
        return update_wrapper(_Handler(name, handler), handler)

    return decorator


class _Handler:
    _name = None
    _handler = None

    def __init__(self, name, handler):
        self._name = name
        self._handler = handler

    def __call__(self, *args, **kwargs):
        return self._handler(*args, **kwargs)


class RouterError(Exception):
    pass

class RouteNotFoundError(RouterError):
    pass
