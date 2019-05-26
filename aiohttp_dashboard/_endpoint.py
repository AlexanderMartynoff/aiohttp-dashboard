from operator import itemgetter
from asyncio import sleep, ensure_future, get_event_loop
from time import time
from collections import defaultdict
import logging
from collections import namedtuple
import inspect
import json
import traceback

from ._pubsub import WsMsgIncoming, WsMsgOutbound, HttpRequest, HttpResponse
from ._router import Router, route
from ._misc import MsgDirection
from ._state import DEBUGGER_KEY
from ._timeguard import TimeGuardFactory


logger = logging.getLogger(__name__)

timeguard = TimeGuardFactory(5)


class MessageRouter(Router):
    def __init__(self, socket, request):
        self._id = id(request)
        self._request = request
        self._state = request.app[DEBUGGER_KEY]
        self._socket = socket

    @route('request.one')
    def request_one(self, message):
        rid = message.data['id']

        @timeguard
        def send():
            self._send(message, self._state.find_http_request(rid))

        def on_event(event):
            if event.rid == rid:
                send()

        self._state.on([
            HttpRequest,
            HttpResponse
        ], on_event, gid=self._id, hid=message.id)

        send()

    @route('request.all')
    def request_all(self, message):

        @timeguard
        def send(event):
            self._send(message, self._state.find_http_requests())

        self._state.on([
            HttpRequest,
            HttpResponse
        ], send, gid=self._id, hid=message.id)

        send(None)

    @route('request.all.count')
    def requests_all_count(self, message):
        print(message)

    @route('request.exception.one')
    def request_exception_one(self, message):
        print(message)

    @route('message.one')
    def message_one(self, message):
        print(message)

    @route('message.all.count')
    def messages_all_count(self, message):
        print(message)

    def _send(self, context, data):
        message = {
            'id': context.id,
            'endpoint': context.endpoint,
            'data': data,
        }
        return ensure_future(self._socket.send_json(message))

    def off(self):
        self._state.off(gid=self._id)
