from datetime import datetime
from asyncio import ensure_future
from aiohttp.web import WebSocketResponse, Response
from queue import Queue
from collections import deque, defaultdict
import sys
import logging
import platform
import aiohttp
from functools import partial
from os.path import join

from .helper import LimitedDict
from .event import (
    EventDriven,
    HttpRequest,
    HttpResponse,
    WsMsgIncoming,
    WsMsgOutbound,
    MsgDirection
)


logger = logging.getLogger(__name__)


DEBUGGER_KEY = __name__
JINJA_KEY = __name__ + '-jinja'


class Debugger(EventDriven):

    def __init__(self, name):
        EventDriven.__init__(self)

        self._name = name
        self._state = State()
        self._api = Api(self._state)

    def register_request(self, request):
        self.state.put_request(request)
        self.fire(HttpRequest(id(request)))

    def register_response(self, request, response):
        requst_id = id(request)

        if requst_id in self.state.requests.keys():
            self.state.requests[requst_id].update({
                'donetime': self.state.now,
                'done': True,
                'resheaders': dict(response.headers),
                'status': response.status,
                'reason': response.reason,
                'iswebsocket': isinstance(response, WebSocketResponse),
                'body': response.text if isinstance(response, Response) else None})

        self.fire(HttpResponse(requst_id))

    # NOTE: maybe split in and out messages store?
    def register_websocket_message(self, direction, request, message):
        request_id, message_id = id(request), id(message)

        self.state.put_ws_message(request_id, {
            'id': message_id,
            'msg': message,
            'time': self.state.now,
            'direction': direction.name
        })

        assert direction in (MsgDirection.INCOMING, MsgDirection.OUTBOUND), \
            RuntimeError(f'Unknown websoket message direction {direction}')

        if direction is MsgDirection.OUTBOUND:
            Event = WsMsgOutbound
        else:
            Event = WsMsgIncoming

        self.fire(Event(request_id))

    def register_http_exception(self, request, exception):
        self.state.put_http_exception(id(request), exception)

    @property
    def api(self):
        return self._api

    @property
    def state(self):
        return self._state

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return join('/', self._name)


class Api:
    def __init__(self, state):
        self._state = state

    def platform_info(self):
        return {
            'platform': platform.platform(),
            'python': sys.version,
            'aiohttp': aiohttp.__version__,
        }

    def requests(self, *args, **kwargs):
        return sorted(self._state.requests.values(), key=lambda _: _['begintime'], reverse=True)

    def request(self, id):
        return self._state.requests.get(id, None)

    def messages(self, id, page=1, perpage=-1):

        if id not in self._state.messages:
            return None

        messages = list(self._state.messages[id])

        if perpage == -1:
            return messages

        start = (page - 1) * perpage
        end = start + perpage

        return messages[start:end]

    def http_exception(self, rid):
        if rid not in self._state.http_exceptions:
            return None

        return self._state.http_exceptions[rid]

    def count_messages(self, rid, direction=None):

        if rid not in self._state._messages:
            return

        if direction is not None:
            return len([_ for _ in self._state._messages[rid] if _['direction'] == direction.name])

        return len(self._state._messages[rid])


class State:
    def __init__(self, limit=50_000):
        self._limit = limit
        self._requests = LimitedDict(limit=self._limit)
        self._messages = LimitedDict(limit=self._limit)
        self._http_exceptions = LimitedDict(limit=self._limit)

    def put_request(self, request):
        rid = id(request)
        ip, _ = request.transport.get_extra_info('peername')
        self._requests[rid] = {
            'id': rid,
            'scheme': request.scheme,
            'host': request.host,
            'path': request.raw_path,
            'method': request.method,
            'begintime': self.now,
            'done': False,
            'reqheaders': dict(request.headers),
            'ip': ip
        }

    def put_ws_message(self, rid, message):
        """
        :param req: request id
        """

        if rid not in self._messages:
            self._messages[rid] = deque(maxlen=self._limit)

        self._messages[rid].appendleft(message)

    def put_http_exception(self, rid, exception):
        self._http_exceptions[rid] = exception

    @property
    def now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def requests(self) -> dict:
        return self._requests

    @property
    def messages(self) -> dict:
        return self._messages

    @property
    def http_exceptions(self) -> dict:
        return self._http_exceptions
