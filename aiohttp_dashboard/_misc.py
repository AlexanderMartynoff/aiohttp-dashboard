from aiohttp.web import WebSocketResponse
from asyncio import iscoroutine, isfuture, ensure_future, gather
from inspect import iscoroutinefunction, isfunction, ismethod, isclass
from collections import defaultdict, OrderedDict, Sequence
from enum import Enum
from time import time


def timestamp():
    return time() * 1000


def to_list(_):
    return list(_) if isinstance(_, Sequence) else [_]


def is_subset_dict(subset_dict, superset_dict):
    for key, value in subset_dict.items():
        if key in superset_dict.keys():
            if value != superset_dict[key]:
                return False
        else:
            return False
    return True


class MsgDirection(Enum):
    OUTBOUND = 1
    INCOMING = 2


class QueueDict(OrderedDict):

    def __init__(self, maxlen, default, **kwargs):
        self._maxlen = maxlen
        self._default = default

        super().__init__(**kwargs)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)

        while len(self) > self._maxlen:
            self.popitem(last=False)

    def __getitem__(self, key):
        if key not in self:
            self.__setitem__(key, self._default())

        return super().__getitem__(key)
