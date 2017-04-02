from aiohttp.web import WebSocketResponse
from collections import defaultdict
from uuid import uuid4
from functools import lru_cache


class WsResponseHelper(WebSocketResponse):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    async def instance(cls, request):
        self = cls()
        await self.prepare(request)
        return self

    async def __anext__(self):
        return self._Msg(await super().__anext__())

    @property
    @lru_cache()
    def id(self):
        return id(self)

    class _Msg:
        def __init__(self, msg):
            self._original = msg
            self._dict = self._original.json()

        @property
        def data(self):
            return self._dict.get('data', defaultdict(lambda: None))

        @property
        def uid(self):
            return self._dict.get('uid', None)

        @property
        def original(self):
            return self._original

        @property
        def endpoint(self):
            return self._dict.get('endpoint', None)


class casemethod:

    def __init__(self, unapply):
        self._unapply = unapply
        self._matchers = []
        self._exceptions = []
        self._default_case = self._not_implemented_noop

    def __get__(self, instance, owner):
        def getter(*args, **kwargs):
            try:
                return self._resolve_method(*args, **kwargs)(instance, *args)
            except Exception as error:
                return self._resolve_exception_case(error)(instance, error)

        return getter

    def __set__(self, *args):
        raise TypeError

    def _resolve_exception_case(self, error):
        for ErrorClass, catcher in self._exceptions:
            if type(error) is ErrorClass:
                return catcher
        raise error

    def _parseunapply(self, *args, **kwargs):
        unapply = self._unapply(*args, **kwargs)
        return unapply if isinstance(unapply, (tuple, list)) else (unapply,)

    def _resolve_method(self, *args, **kwargs):
        for values, method in self._matchers:
            if values == self._parseunapply(*args, **kwargs):
                return method
        return self._default_case

    def _register_case(self, values, method):
        self._matchers += (values, method),
        return self

    def _register_exception(self, ExceptionClass, catcher):
        self._exceptions += (ExceptionClass, catcher),
        return self

    def _not_implemented_noop(self, *args, **kwargs):
        raise NotImplementedError("Default method was not setup")

    @classmethod
    def unapply(cls, unapply):
        return cls(unapply)

    def case(self, *values):
        return lambda method: self._register_case(values, method)

    def default(self, method):
        self._default_case = method
        return self

    def catch(self, ExceptionClass):
        return lambda catcher: self._register_exception(ExceptionClass, catcher)


class PubSubSupport:
    """
    Use as mixin. Example:
    PubSubSupport().on('event', lambda event: ...)
    """

    def __init_subclass__(self):
        self.__handlers = defaultdict(list)

    def on(self, etype, handler, *, group=uuid4(), hid=uuid4()):
        self.__handlers[group] += (etype, handler, hid),
        return self

    def off(self, *, group=None, hid=None):
        if group:
            del self.__handlers[group]

        if hid:
            for _group, handlers in self.__handlers.items():
                for etype, handler, _hid in handlers[:]:
                    if _hid == hid:
                        handlers.remove((etype, handler, _hid))

    def fire(self, event):
        for handlers in self.__handlers.values():
            for etype, handler, hid in handlers:
                if isinstance(event, etype):
                    handler(event)

    class Event:
        def __init__(self, name):
            self.name = name
