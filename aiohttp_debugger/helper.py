from aiohttp.web import WebSocketResponse
from collections import defaultdict, OrderedDict
from uuid import uuid4
from functools import lru_cache
import asyncio
from asyncio import iscoroutine, isfuture, ensure_future, gather
from inspect import iscoroutinefunction, isfunction, ismethod, isclass
import logging


elog = logging.getLogger("aiohttp_debugger.helper").exception


def catch(*args):

    def catcher(function):

        if iscoroutinefunction(function):
            async def decorator(*args, **kwargs):
                try:
                    return await function(*args, **kwargs)
                except BaseException as err:
                    if isinstance(err, etypes):
                        return ehandler(str(err))
                    raise err
        else:
            def decorator(*args, **kwargs):
                try:
                    return function(*args, **kwargs)
                except BaseException as err:
                    if isinstance(err, etypes):
                        return ehandler(str(err))
                    raise err

        return decorator

    # if first args is function or method
    # @catch
    # def function():
    #   ...
    function, *_ = args

    if isfunction(function) or ismethod(function):
        etypes, ehandler = Exception, elog
        return catcher(function)

    # if args is exception types and/or handler
    # @catch(Exception):
    # def function():
    #   ...
    *etypes, ehandler = args

    if isclass(ehandler) and issubclass(ehandler, BaseException):
        etypes, handler = args, elog

    etypes = tuple(etypes)
    
    return catcher


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
            self._body = self._Body(self)

        @property
        def body(self):
            return self._body

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

        def __repr__(self):
            return f"<{self.endpoint}>"

        class _Body:
            def __init__(self, msg):
                self.__msg = msg

            def __getattr__(self, name):
                return self._Attribute(self.__msg.data[name])

            class _Attribute:
                def __init__(self, value):
                    self.__value = value

                def __rshift__(self, typemapper):
                    return typemapper(self.__value)

                def __matmul__(self, typemapper):
                    return typemapper(self.__value)

                @property
                def raw(self):
                    return self.__value


class casemethod:
    def __init__(self, unapply):
        self._unapply = unapply
        self._matchers = []
        self._exceptions = []
        self._default_case = self._not_implemented_noop

    def __get__(self, instance, owner):
        # check exception handling in `getter`
        # maybe it not wotk as need

        def getter(*args, **kwargs):
            try:
                result = self._resolve_case(*args, **kwargs)(instance, *args, **kwargs)

                if iscoroutine(result) or isfuture(result):
                    future = ensure_future(result)
                    future.add_done_callback(lambda future:
                        self._handle_future_exception(future, instance, args, kwargs))
                    return future

                return result
            except Exception as error:
                return self._resolve_exception_case(error)(instance, error, *args, **kwargs)

        return getter

    def __set__(self, *args):
        raise self.IllegalOpearationException

    def _handle_future_exception(self, future, instance, args, kwargs):
        err = future.exception()
        if err is not None:
            handler = self._resolve_exception_case(err)(instance, err, *args, **kwargs)
            if iscoroutine(handler):
                ensure_future(handler)

    def _resolve_exception_case(self, error):
        for err_type, catcher in self._exceptions:
            if isinstance(error, err_type):
                return catcher
        raise error

    def _parseunapply(self, *args, **kwargs):
        unapply = self._unapply(*args, **kwargs)
        return unapply if isinstance(unapply, (tuple, list)) else (unapply,)

    def _resolve_case(self, *args, **kwargs):
        """ resolve first match method """
        
        for values, method in self._matchers:
            if values == self._parseunapply(*args, **kwargs):
                return method
        return self._default_case

    def _register_case(self, values, method):
        self._matchers += (values, method),
        return self

    def _register_exception(self, err_type, catcher):
        self._exceptions += (err_type, catcher),
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

    def catch(self, err_type):
        return lambda catcher: self._register_exception(err_type, catcher)

    class IllegalOpearationException(Exception): pass


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

        if group is None and hid is None:
            raise ValueError('group or/and hid must be not None')

        if group:
            try:
                del self.__handlers[group]
            except KeyError:
                pass

        if hid:
            for group_, handlers in self.__handlers.items():
                for etype, handler, hid_ in handlers[:]:
                    if hid_ == hid:
                        self.__handlers[group_].remove((etype, handler, hid_))

    def fire(self, event):
        for handlers in self.__handlers.values():
            for etype, handler, hid in handlers:
                if isinstance(event, etype):
                    handler(event)

    @property
    def subscribers_len(self):
        return sum(len(handlers) for handlers in self.__handlers.values())

    class Event:
        pass


class LimitedDict(OrderedDict):
    def __init__(self, *args, **kwargs):
        self._maxlen = kwargs.pop('maxlen', None)
        super().__init__(*args, **kwargs)
        self._controll_size_limit()

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._controll_size_limit()

    def _controll_size_limit(self):
        if self._maxlen is not None:
            while len(self) > self._maxlen:
                self.popitem(last=False)
