from datetime import datetime
from asyncio import ensure_future
from aiohttp.web import WebSocketResponse, Response
from queue import Queue
from collections import deque, defaultdict
from functools import partial
from os.path import join
import logging
from inspect import isfunction

from ._misc import MsgDirection
from ._pubsub import PubSub

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


class Debugger(PubSub):

    def __init__(self, time):
        PubSub.__init__(self)

        self._time = time

        self._http_requests = deque(maxlen=_LIMIT)
        self._http_exceptions = deque(maxlen=_LIMIT)
        self._ws_messages = deque(maxlen=_LIMIT)
        self._ws_exceptions = deque(maxlen=_LIMIT)

    def register_http_request(self, request):
        request_id = id(request)
        ip, _ = request.transport.get_extra_info('peername')

        self._http_requests.appendleft({
            'id': request_id,
            'scheme': request.scheme,
            'host': request.host,
            'path': request.raw_path,
            'method': request.method,
            'starttime': self._now,
            'requestheaders': dict(request.headers),
            'ip': ip,
        })

        self.fire('http.request', {
            'request': request_id,
        })

    def register_http_response(self, request, response):
        request_id = id(request)
        stored_request = self.find_http_request(request_id)

        if isinstance(response, Response):
            body = response.text
        else:
            body = None

        if stored_request:
            stored_request.update({
                'stoptime': self._now,
                'responseheaders': dict(response.headers),
                'status': response.status,
                'reason': response.reason,
                'body': body,
            })

        self.fire('http.response', {
            'request': request_id,
        })

    def find_http_request(self, request_id):
        for request in self._http_requests:
            if request_id == request['id']:
                return request

    def find_http_requests(self, time_start=None, time_stop=None,
                           status_code=None, slice_start=None,
                           slice_limit=None):

        http_requests = []

        for request in self._http_requests:

            if status_code and request['status'] != status_code:
                continue

            if time_start and request['time'] < time_start:
                continue

            if time_stop and request['time'] > time_stop:
                continue

            http_requests.append(request)

        return _slice(http_requests, slice_start, slice_limit)

    def count_http_requests(self):
        return len(self._http_requests)

    def register_http_exception(self, request, exception):
        self._http_exceptions.appendleft({
            'excepton': exception,
            'requestid': id(request),
        })

    def register_ws_message(self, direction, request, message):
        request_id, message_id = id(request), id(message)

        self._ws_messages.appendleft({
            'id': message_id,
            'requestid': request_id,
            'message': message,
            'time': self._now,
            'direction': direction.name
        })

        if direction is MsgDirection.OUTBOUND:
            event = 'websocket.outcoming'
        else:
            event = 'websocket.incoming'

        self.fire(event, {
            'request': request_id,
        })

    def find_http_exception(self, request_id):
        for exception in self._http_exceptions:
            if request_id == exception['requestid']:
                return exception

    def find_ws_messages(self, request_id=None, direction=None,
                         slice_start=None, slice_limit=None):
        messages = []

        for message in self._ws_messages:

            if request_id and request_id != message['requestid']:
                continue

            if direction and direction.name != message['direction']:
                continue

            messages.append(message)

        return _slice(messages, slice_start, slice_limit)

    def count_ws_messages(self, request_id=None, direction=None):
        return len(self.find_ws_messages(request_id, direction))

    @property
    def _now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def times(self):
        return {
            'startup': self._time
        }
