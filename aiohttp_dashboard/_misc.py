from aiohttp.web import WebSocketResponse
from asyncio import iscoroutine, isfuture, ensure_future, gather
from inspect import iscoroutinefunction, isfunction, ismethod, isclass
from collections import defaultdict, OrderedDict, Sequence
from enum import Enum
from time import time


def timestamp():
    return time() * 1000


def to_list(value):
    return list(value) if isinstance(value, Sequence) else [value]


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
