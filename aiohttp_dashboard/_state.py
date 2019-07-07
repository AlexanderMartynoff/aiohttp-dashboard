from datetime import datetime
from asyncio import ensure_future
from aiohttp.web import WebSocketResponse, Response
from queue import Queue
from collections import deque, defaultdict
from functools import partial
from os.path import join
import logging
from inspect import isfunction


from ._misc import MsgDirection, QueueDict
from ._event_emitter import EventEmitter

logger = logging.getLogger(__name__)


DEBUGGER_KEY = __name__
JINJA_KEY = __name__ + '-jinja'
_LIMIT = 50000


def _slice(sequence, start=0, limit=None):
    if limit is None:
        stop = None
    else:
        stop = start + limit

    return sequence[start:stop]


_Deque = partial(deque, maxlen=_LIMIT)
_QueueDict = partial(QueueDict, _LIMIT)


class Debugger:

    def __init__(self, time):
        self._time = time
        self._emitter = EventEmitter()

        self._requests = _QueueDict(dict)
        self._requests_errors = _QueueDict(dict)
        self._messages = _QueueDict(_Deque)
        self._messages_errors = _QueueDict(_Deque)

    def register_request(self, request):
        request_id = id(request)
        ip, _ = request.transport.get_extra_info('peername')

        self._requests[request_id] = {
            'id': request_id,
            'scheme': request.scheme,
            'host': request.host,
            'path': request.raw_path,
            'method': request.method,
            'starttime': self._datetime,
            'requestheaders': dict(request.headers),
            'ip': ip,
        }

        self.emitter.fire('http.request', {
            'request': request_id,
        })

        self.emitter.fire('http', {
            'request': request_id,
        })

    def register_response(self, request, response):
        request_id = id(request)
        stored_request = self.find_request(request_id)

        body = response.text if isinstance(response, Response) else None
        websocket = True if isinstance(response, WebSocketResponse) else False

        if stored_request:
            stored_request.update({
                'stoptime': self._datetime,
                'responseheaders': dict(response.headers),
                'status': response.status,
                'reason': response.reason,
                'body': body,
                'websocket': websocket,
            })

        self.emitter.fire('http.response', {
            'request': request_id,
        })

        self.emitter.fire('http', {
            'request': request_id,
        })

    def find_request(self, request_id):
        return self._requests[request_id]

    def find_requests(self, time_start=None, time_stop=None,
                      status_code=None, slice_start=None,
                      slice_limit=None):

        http_requests = []

        for request in self._requests.values():

            if status_code and request['status'] != status_code:
                continue

            if time_start and request['time'] < time_start:
                continue

            if time_stop and request['time'] > time_stop:
                continue

            http_requests.append(request)

        return _slice(http_requests, slice_start, slice_limit)

    def count_requests(self, *args, **kwargs):
        return len(self.find_requests(*args, **kwargs))

    def register_request_error(self, request, exception):
        request_id = id(request)
        self._requests_errors[request_id] = exception

    def find_request_error(self, request_id):
        return self._requests_errors[request_id]

    def register_message(self, direction, request, message):
        request_id, message_id = id(request), id(message)

        self._messages[request_id].appendleft({
            'id': message_id,
            'requestid': request_id,
            'body': message,
            'time': self._datetime,
            'direction': direction.name
        })

        if direction is MsgDirection.OUTBOUND:
            event = 'websocket.outcoming'
        else:
            event = 'websocket.incoming'

        self.emitter.fire(event, {
            'request': request_id,
        })

        self.emitter.fire('websocket', {
            'request': request_id,
            'direction': MsgDirection.OUTBOUND,
        })

    def find_messages(self, request_id=None, direction=None,
                      slice_start=None, slice_limit=None):
        messages = []

        for queue in self._messages.values():

            for message in queue:

                if request_id and request_id != message['requestid']:
                    continue

                if direction and direction.name != message['direction']:
                    continue

                messages.append(message)

        return _slice(messages, slice_start, slice_limit)

    def count_messages(self, *args, **kwargs):
        return len(self.find_messages(*args, **kwargs))

    @property
    def _datetime(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def status(self):
        return {
            'startup': self._time
        }

    @property
    def emitter(self):
        return self._emitter
