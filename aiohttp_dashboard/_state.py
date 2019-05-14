from datetime import datetime
from asyncio import ensure_future
from aiohttp.web import WebSocketResponse, Response
from queue import Queue
from collections import deque, defaultdict
from functools import partial
from os.path import join
import sys
import logging
import platform
import aiohttp

from ._misc import LimitedDict, MsgDirection
from ._pubsub import Pubsub, HttpRequest, HttpResponse, \
    WsMsgIncoming, WsMsgOutbound


logger = logging.getLogger(__name__)


DEBUGGER_KEY = __name__
JINJA_KEY = __name__ + '-jinja'
_LIMIT = 50000


class Debugger(Pubsub):

    def __init__(self, name, time):
        Pubsub.__init__(self)

        self._name = name
        self._time = time

        self._http_requests = LimitedDict(limit=_LIMIT)
        self._http_exceptions = LimitedDict(limit=_LIMIT)
        self._ws_messages = LimitedDict(limit=_LIMIT)
        self._ws_exceptions = LimitedDict(limit=_LIMIT)

    # registration API
    def register_request(self, request):
        requst_id = id(request)
        ip, _ = request.transport.get_extra_info('peername')

        self._http_requests[requst_id] = {
            'id': requst_id,
            'scheme': request.scheme,
            'host': request.host,
            'path': request.raw_path,
            'method': request.method,
            'begintime': self._now,
            'done': False,
            'reqheaders': dict(request.headers),
            'ip': ip
        }

        self.fire(HttpRequest(requst_id))

    def register_response(self, request, response):
        requst_id = id(request)

        if requst_id in self._http_requests.keys():
            self._http_requests[requst_id].update({
                'donetime': self._now,
                'done': True,
                'resheaders': dict(response.headers),
                'status': response.status,
                'reason': response.reason,
                'iswebsocket': isinstance(response, WebSocketResponse),
                'body': response.text if isinstance(response, Response) else None
            })

        self.fire(HttpResponse(requst_id))

    def register_websocket_message(self, direction, request, message):
        request_id, message_id = id(request), id(message)

        if request_id not in self._ws_messages:
            self._ws_messages[request_id] = deque(maxlen=_LIMIT)

        self._ws_messages[request_id].appendleft({
            'id': message_id,
            'msg': message,
            'time': self._now,
            'direction': direction.name
        })

        if direction is MsgDirection.OUTBOUND:
            Event = WsMsgOutbound
        else:
            Event = WsMsgIncoming

        self.fire(Event(request_id))

    def register_http_exception(self, request, exception):
        self._http_exceptions[id(request)] = exception

    # getters API

    def find_http_requests(self):
        return sorted(self._http_requests.values(), key=lambda _: _['begintime'], reverse=True)

    def find_http_request(self, id):
        return self._http_requests.get(id, None)

    def count_http_requests(self):
        return len(self._http_requests)

    @property
    def http_exceptions(self) -> dict:
        return self._http_exceptions

    def find_http_exception(self, rid):
        if rid not in self._http_exceptions:
            return None

    @property
    def ws_messages(self) -> dict:
        return self._ws_messages

    def find_ws_messages(self, id, page=1, perpage=-1):

        if id not in self._ws_messages:
            return None

        messages = list(self._ws_messages[id])

        if perpage == -1:
            return messages

        start = (page - 1) * perpage
        end = start + perpage

        return messages[start:end]

    def count_ws_messages(self, rid=None, direction=None):

        if rid is None:
            return sum(len(_) for _ in self._ws_messages.values())

        if rid not in self._ws_messages:
            return

        if direction is not None:
            return len([_ for _ in self._ws_messages[rid] if _['direction'] == direction.name])

        return len(self._ws_messages[rid])

    @property
    def _now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def times(self):
        return {
            'startup': self._time
        }

    def platform_info(self):
        return {
            'platform': platform.platform(),
            'python': sys.version,
            'aiohttp': aiohttp.__version__,
        }

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return join('/', self._name)
