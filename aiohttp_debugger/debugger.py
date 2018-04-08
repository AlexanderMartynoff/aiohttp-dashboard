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

from .tool import Bus, LimitedDict
from .event import (HttpRequest, HttpResponse,
                    WsMsgIncoming, WsMsgOutbound, MsgDirection)


logger = logging.getLogger("aiohttp_debugger.debugger")


DEBUGGER_KEY = __name__
JINJA_KEY = '{}.jinja2'.format(__name__)


class Debugger(Bus):
    """ Facade API """

    # NOTE: remove application from debugger
    # NOTE: application in debugger need just for return route list
    # NOTE: move this functional in endpoint.py
    def __init__(self):
        Bus.__init__(self)

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

        self.fire(HttpResponse(id(request)))

    def register_websocket_message(self, direction, request, msg, msg_mapper, event):
        requst_id, message_id = id(request), id(msg)
        event.rid = requst_id

        self.state.put_ws_message(requst_id, {
            'id': message_id,
            'msg': msg_mapper(msg),
            'time': self.state.now,
            'direction': direction.name
        })

        self.fire(event)

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
            'debugger': __version__
        }

    def requests(self, *args, **kwargs):
        return list(self._state.requests.values())

    def request(self, rid):
        return next((request for request in self.requests() if request['id'] == rid), None)

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
    def __init__(self, maxlen=50_000):
        self._maxlen = maxlen
        self._requests = LimitedDict(maxlen=self._maxlen)
        self._messages = LimitedDict(maxlen=self._maxlen)
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
            self._messages[rid] = deque(maxlen=self._maxlen)

        self._messages[rid] += message,

        if self._outbound_msg_counter[rid] + self._incoming_msg_counter[rid] >= self._maxlen:
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
