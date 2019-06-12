from aiohttp.web import WebSocketResponse
from asyncio import iscoroutine, isfuture, ensure_future, gather
from inspect import iscoroutinefunction, isfunction, ismethod, isclass
from collections import defaultdict, OrderedDict, Sequence
from enum import Enum
import traceback
import json


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


class JSONEncoder(json.JSONEncoder):

    def default(self, data):
        if isinstance(data, Exception):

            return {
                'class': type(data).__name__,
                'message': str(data),
                'traceback': traceback.format_tb(data.__traceback__),
            }
        return data


def dumps(data):
    return json.dumps(data, cls=JSONEncoder)


class MsgDirection(Enum):
    OUTBOUND = 1
    INCOMING = 2
