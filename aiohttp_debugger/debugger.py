from datetime import datetime
from asyncio import ensure_future
from aiohttp.web import WebSocketResponse, Response
from queue import Queue
from collections import deque, defaultdict
import os
import sys
import logging
import platform
import aiohttp
from functools import partial

from .helper import LimitedDict
from .event import (EventDriven, HttpRequest, HttpResponse,
                    WsMsgIncoming, WsMsgOutbound, MsgDirection)


logger = logging.getLogger("aiohttp_debugger.debugger")


DEBUGGER_KEY = __name__
JINJA_KEY = __name__ + '.jinja2'


class Debugger(EventDriven):

    def __init__(self):
        EventDriven.__init__(self)

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
            RuntimeError(f'Unknown websoket message direction {direction!s}')

        self.fire((WsMsgOutbound if direction is MsgDirection.OUTBOUND else WsMsgIncoming)(request_id))

    @property
    def api(self):
        return self._api

    @property
    def state(self):
        return self._state


# NOTE: merge this class with Debugger
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

    def messages(self, rid, page=1, perpage=-1):

        if rid not in self._state.messages:
            return None

        messages = list(self._state.messages[rid])

        if perpage == -1:
            return messages

        start = (page - 1) * perpage
        end = start + perpage

        return messages[start:end]

    def count_by_direction(self, rid, direction=None):
        if direction is None:
            return self._state.incoming_msg_counter[rid] + self._state.outbound_msg_counter[rid]
        elif direction is MsgDirection.OUTBOUND:
            return self._state.outbound_msg_counter[rid]
        elif MsgDirection.INCOMING:
            return self._state.incoming_msg_counter[rid]


class State:
    def __init__(self, limit=50_000):
        self._limit = limit
        self._requests = LimitedDict(limit=self._limit)
        self._messages = LimitedDict(limit=self._limit)
        self._incoming_msg_counter = defaultdict(int)
        self._outbound_msg_counter = defaultdict(int)

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

        if self._outbound_msg_counter[rid] + self._incoming_msg_counter[rid] >= self._limit:
            return

        if message['direction'] == MsgDirection.OUTBOUND.name:
            self._outbound_msg_counter[rid] += 1
        else:
            self._incoming_msg_counter[rid] += 1

    @property
    def outbound_msg_counter(self):
        return self._outbound_msg_counter

    @property
    def incoming_msg_counter(self):
        return self._incoming_msg_counter

    @property
    def now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")

    @property
    def requests(self) -> dict:
        return self._requests

    @property
    def messages(self) -> dict:
        return self._messages
