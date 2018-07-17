from aiohttp.web import WebSocketResponse
from collections import defaultdict, OrderedDict
from functools import lru_cache
from asyncio import iscoroutine, isfuture, ensure_future, gather
from inspect import iscoroutinefunction, isfunction, ismethod, isclass
from collections import defaultdict, OrderedDict, Sequence
import logging
import asyncio


def to_list(_):
    return list(_) if isinstance(_, Sequence) else [_]


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
    def id(self):
        return id(self)

    class _Msg:
        def __init__(self, message):
            self._original = message
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
                self._msg = msg

            def __getattr__(self, name):
                return self._Attribute(self._msg.data[name])

            class _Attribute:
                def __init__(self, value):
                    self._value = value

                def __rshift__(self, typemapper):
                    return typemapper(self._value)

                # TODO - deprecated, remove
                def __matmul__(self, typemapper):
                    return typemapper(self._value)


class LimitedDict(OrderedDict):
    _limit = None

    def __init__(self, *args, **kwargs):
        self._limit = kwargs.pop('limit', None)
        super().__init__(*args, **kwargs)
        self._controll_limit()

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._controll_limit()

    def _controll_limit(self):
        if self._limit is not None:
            while len(self) > self._limit:
                self.popitem(last=False)
