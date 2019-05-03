from aiohttp.web import WebSocketResponse
from asyncio import iscoroutine, isfuture, ensure_future, gather
from inspect import iscoroutinefunction, isfunction, ismethod, isclass
from collections import defaultdict, OrderedDict, Sequence
from enum import Enum


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
        return self._Message(await super().__anext__())

    @property
    def id(self):
        return id(self)

    class _Message:
        def __init__(self, message):
            self._message = message
            self._json = self._message.json()

        @property
        def data(self):
            return self._json.get('data', defaultdict(lambda: None))

        @property
        def uid(self):
            return self._json.get('uid', None)

        @property
        def endpoint(self):
            return self._json.get('endpoint', None)

        def __repr__(self):
            return f"<{self.endpoint}>"


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


class MsgDirection(Enum):
    OUTBOUND = 1
    INCOMING = 2
