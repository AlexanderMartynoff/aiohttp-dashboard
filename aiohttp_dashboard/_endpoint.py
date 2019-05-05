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


logger = logging.getLogger(__name__)


class WsMsgDispatcherProxy:
    """ Passing websocket meessage into target method for processing """

    def __init__(self, socket, debugger, request):
        debugger_api = DebuggerApi(debugger, request)

        self._sender = sender = Sender(socket, debugger_api)
        self._dispatcher = WsMsgDispatcher(sender, debugger_api, debugger)

    def recive(self, message):
        self._sender.send_soon(message, self._dispatcher.router(message.endpoint, message))

    def close(self):
        self._dispatcher.close()
        self._sender.close()


class WsMsgDispatcher(Router):
    """ Endpoints for websocket message processing """

    def __init__(self, sender, debugger_api, debugger):
        self._debugger = debugger
        self._sender = sender
        self._debugger_api = debugger_api

    @route('request')
    def sibsribe_request(self, message):
        rid = message.data['id']

        def handler(event):
            if event.rid == rid:
                self._sender.send(message)

        self._debugger.on([
            HttpRequest,
            HttpResponse
        ], handler, group=self._sender.id, hid=message.uid)

        return self._debugger_api.request(rid)

    @route('request.requests.count')
    def sibsribe_request_count(self, message):

        def handler(event):
            self._sender.send(message)

        self._debugger.on([
            HttpRequest,
            HttpResponse
        ], handler, group=self._sender.id, hid=message.uid)

        return self._debugger_api.requests_count()

    @route('request.messages')
    def sibsribe_request_messages(self, message):
        rid = message.data['id']
        limit = message.data['limit']
        page = message.data['page']

        def handler(event):
            if event.rid == rid:
                self._sender.send(message)

        self._debugger.on([
            WsMsgIncoming,
            WsMsgOutbound
        ], handler, group=self._sender.id, hid=message.uid)

        return self._debugger_api.messages(rid, page, limit)

    @route('request.messages.count')
    def sibsribe_request_messages_count(self, message):

        def handler(event):
            self._sender.send(message)

        self._debugger.on([
            WsMsgIncoming,
            WsMsgOutbound
        ], handler, group=self._sender.id, hid=message.uid)

        return self._debugger_api.messages_count()

    @route('requests')
    def sibsribe_requests(self, message):

        def handler(event):
            self._sender.send(message)

        self._debugger.on([
            HttpRequest,
            HttpResponse
        ], handler, group=self._sender.id, hid=message.uid)

        return self._debugger_api.requests()

    @route('request.exception')
    def sibsribe_request_exceptions(self, message):
        rid = message.data['id']

        return self._debugger_api.http_exception(rid)

    @route('unsibscribe')
    def unsibscribe(self, message):
        # NOTE: with this `hid` probably exist multiple handlers

        self._debugger.off(hid=message.data['id'])

    @route('fetch.times')
    def fetch_times(self, _message):
        return self._debugger_api.times()

    @route('fetch.info')
    def fetch_info(self, _message):
        return self._debugger_api.platform_info()

    @route('fetch.routes')
    def fetch_routes(self, _message):
        return self._debugger_api.routes()

    @route.default
    def default(self, _message):
        return {'status': 'endpoint not found'}

    @route.error(Exception)
    def exception(self, exception, message):
        self._sender.send_soon(message, {
            'status': 'error',
            'cause': str(exception)
        })

    def close(self):
        self._debugger.off(group=self._sender.id)
        logger.info(f'After unsibscribe handlers left - ``{self._debugger.size}``')


class Sender(Router):
    """ Use for deferred sending websocket message """

    def __init__(self, socket, debugger_api):
        self._socket = socket
        self._debugger_api = debugger_api
        self._endpoints = defaultdict(lambda: None)

    @route('request')
    def _sibsribe_request(self, message):
        self._send(self._debugger_api.request(message.data['id']), message)

    @route('request.requests.count')
    def sibsribe_request_count(self, message):
        self._send(self._debugger_api.requests_count(), message)

    @route('request.messages.count')
    def sibsribe_request_messages_count(self, message):
        self._send(self._debugger_api.messages_count(), message)

    @route('request.messages')
    def _sibsribe_request_messages(self, message):
        rid = message.data['id']
        limit = message.data['limit']
        page = message.data['page']

        self._send(self._debugger_api.messages(rid, page, limit), message)

    @route('requests')
    def _sibsribe_requests(self, message):
        self._send(self._debugger_api.requests(), message)

    def _take_endpoint(self, name):
        endpoint = self._endpoints[name]

        if endpoint is None:
            endpoint = self._endpoints[name] = self._EndpointState(handler=self.router)

        return endpoint

    # NOTE: refact this!
    def send_soon(self, message, out):
        self._take_endpoint(message.endpoint).handle_soon(message, out, self._send)

    def send(self, message):
        logger.info(f'Try to send data for ``{message.endpoint}``')

        endpoint = self._endpoints[message.endpoint]

        if endpoint is None:
            self._take_endpoint(message.endpoint).handle_soon(message)
        else:
            waiting, free = endpoint.is_free()

            if free:
                endpoint.handle_soon(message)
            else:
                endpoint.handle_later(message)

            logger.info(f'Passed ``{waiting}``, is free - ``{"Yes" if free else "No"}``')

    def close(self):
        for endpoint_state in self._endpoints.values():
            endpoint_state.close()

    def _send(self, out, message):
        logger.info(f'Send to chanel ``{message.endpoint}``')

        return ensure_future(self._socket.send_json(
            self._prepare_ws_response(out, message), dumps=dumps))

    def _prepare_ws_response(self, out, message):
        return {'data': out, 'uid': message.uid, 'endpoint': message.endpoint}

    @property
    def id(self):
        return self._socket.id

    class _EndpointState:
        _delay = 3
        _handler = None
        _last_send_time = None
        _send_waiting_task = None

        def __init__(self, handler):
            self._handler = handler
            self._last_send_time = self.time

        @property
        def time(self):
            return get_event_loop().time()

        def _handler_caller(self, message):
            self._handler(message.endpoint, message)

            self._send_waiting_task = None
            self._last_send_time = self.time

        def handle_soon(self, message, out=None, handler=None):
            if handler is not None:
                return handler(out, message)

            return self._handler_caller(message)

        def handle_later(self, message):
            if self._send_waiting_task:
                self._send_waiting_task.cancel()

                logger.info(f'Cancel deferred task ``{id(self._send_waiting_task)}``')

            when, task = self._do_send_later(message)
            self._send_waiting_task = task

            logger.info(f'Deferred task ``{id(task)}`` will call at ``{when}`` seconds for ``{message.endpoint}``')

        def _do_send_later(self, message):
            when = self._last_send_time + self._delay
            task = get_event_loop().call_at(when, self._handler_caller, message)

            return when, task

        def is_free(self):
            """ Return tuple (pased the time, freedom marker) """

            waiting = self.time - self._last_send_time
            free = waiting >= self._delay

            return waiting, free

        def close(self):
            if self._send_waiting_task:
                self._send_waiting_task.cancel()


class DebuggerApi:
    """ Facade layer for WEB """

    def __init__(self, debugger, request):
        self._debugger = debugger
        self._request = request

    def request(self, rid):
        return {'item': self._debugger.api.request(rid)}

    def times(self):
        return self._debugger.times()

    def requests(self):
        return self._debugger.api.requests()

    def messages_count(self):
        return self._debugger.api.messages_count()

    def requests_count(self):
        return self._debugger.api.requests_count()

    def messages(self, rid, page, perpage):
        return {
            'collection': self._debugger.api.messages(rid, page, perpage),
            'total': self._debugger.api.count_messages(rid),
            'incoming': self._debugger.api.count_messages(rid, MsgDirection.INCOMING),
            'outbound': self._debugger.api.count_messages(rid, MsgDirection.OUTBOUND),
        }

    def http_exception(self, rid):
        return {'item': self._debugger.api.http_exception(rid)}

    def routes(self):
        routes = []

        for route in self._request.app.router.routes():
            routes.append({
                'name': route.name,
                'method': route.method,
                'info': self._extract_route_info(route),
                'handler': route.handler.__name__,
                'source': inspect.getsource(route.handler)
            })

        return routes

    def _extract_route_info(self, route):
        return {str(key): str(value) for key, value in route.get_info().items()}

    def unsibscribe(self, hid):
        return self._debugger.off(hid=hid)

    def platform_info(self):
        return self._debugger.api.platform_info()

    @property
    def debugger(self):
        return self._debugger


class JSONEncoder(json.JSONEncoder):

    def default(self, data):
        if isinstance(data, Exception):

            return {
                'type': 'error',
                'class': type(data).__name__,
                'message': str(data),
                'traceback': traceback.format_tb(data.__traceback__),
            }
        return data


def dumps(data):
    return json.dumps(data, cls=JSONEncoder)
