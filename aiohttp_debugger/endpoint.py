from operator import itemgetter
from asyncio import sleep, ensure_future, get_event_loop
from time import time
from collections import defaultdict
import warnings
import logging
import concurrent.futures
from collections import namedtuple
from time import sleep, time
import re
import inspect

from .event import WsMsgIncoming, WsMsgOutbound, HttpRequest, HttpResponse, MsgDirection
from .router import Router, route


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
    """ Endpoints for websocket message processing.
    """

    def __init__(self, sender, debugger_api, debugger):
        self._debugger = debugger
        self._sender = sender
        self._debugger_api = debugger_api

    @route('sibsribe.request')
    def sibsribe_request(self, message):
        rid = message.body.id >> int

        def handler(event):
            if event.rid == rid:
                self._sender.send(message)

        self._debugger.on([
            HttpRequest,
            HttpResponse
        ], handler, group=self._sender.id, hid=message.uid)

        return self._debugger_api.request(rid)

    @route('sibsribe.request.messages')
    def sibsribe_request_messages(self, message):
        rid = message.body.id >> int
        page = message.body.page >> int
        perpage = message.body.perpage >> int

        def handler(event):
            if event.rid == rid:
                self._sender.send(message)

        self._debugger.on([
            WsMsgIncoming,
            WsMsgOutbound
        ], handler, group=self._sender.id, hid=message.uid)

        return self._debugger_api.messages(rid, page, perpage)

    @route('sibsribe.requests')
    def sibsribe_requests(self, message):

        def handler(event):
            self._sender.send(message)

        self._debugger.on([
            HttpRequest,
            HttpResponse
        ], handler, group=self._sender.id, hid=message.uid)

        return self._debugger_api.requests()

    @route('unsibscribe')
    def unsibscribe(self, message):
        """ With this `hid` probably exist multiple handlers """

        self._debugger.off(hid=message.body.id >> str)

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
        logger.info(f"after remove debugger handlers - {self._debugger.size}")


class Sender(Router):
    """ Use for deferred sending websocket message """

    def __init__(self, socket, debugger_api):
        self._socket = socket
        self._debugger_api = debugger_api
        self._endpoints = defaultdict(lambda: None)

    @route('sibsribe.request')
    def _sibsribe_request(self, message):
        self._send(self._debugger_api.request(message.body.id >> int), message)

    @route('sibsribe.request.messages')
    def _sibsribe_request_messages(self, message):
        rid = message.body.id >> int
        page = message.body.page >> int
        perpage = message.body.perpage >> int
        
        self._send(self._debugger_api.messages(rid, page, perpage), message)

    @route('sibsribe.requests')
    def _sibsribe_requests(self, message):
        self._send(self._debugger_api.requests(), message)
    
    # NOTE: refact this!
    def send_soon(self, message, out):
        endpoint = self._endpoints[message.endpoint]

        if endpoint is None:
            endpoint = self._endpoints[message.endpoint] = self._EndpointState(handler=self.router)

        endpoint.handle_soon(message, out, self._send)

    def send(self, message):

        logger.info(f"try to send data for {message.endpoint}")

        endpoint = self._endpoints[message.endpoint]

        if endpoint is None:
            endpoint = self._endpoints[message.endpoint] = self._EndpointState(handler=self.router)
            endpoint.handle_soon(message)
        elif endpoint.is_free():
            endpoint.handle_soon(message)
        else:
            endpoint.handle_later(message)

    def close(self):
        for endpoint_state in self._endpoints.values():
            endpoint_state.close()

    def _send(self, out, message):
        logger.info(f'send websocket to chanel {message.endpoint}')
        return ensure_future(self._socket.send_json(self._prepare_ws_response(out, message)))

    def _prepare_ws_response(self, out, message):
        return {'data': out, 'uid': message.uid, 'endpoint': message.endpoint}

    @property
    def id(self):
        return self._socket.id

    class _EndpointState:
        _delay = 5
        _handler = None
        _last_send_time = None
        _handler_wait_for_send = None

        def __init__(self, handler):
            self._handler = handler
            self._last_send_time = self.time

        @property
        def time(self):
            return get_event_loop().time()

        def _handler_caller(self, message):
            self._handler(message.endpoint, message)
            self._handler_wait_for_send = None
            self._last_send_time = self.time

        def handle_soon(self, message, out=None, handler=None):
            if handler is not None:
                return handler(out, message)

            return self._handler_caller(message)

        def handle_later(self, message):
            if self._handler_wait_for_send:
                self._handler_wait_for_send.cancel()
                logger.info(f"cancel deferred task {id(self._handler_wait_for_send)}")

            self._handler_wait_for_send = self._do_send_later(message)

        def _do_send_later(self, message):
            when = self._last_send_time + self._delay
            task = get_event_loop().call_at(when, lambda: self._handler_caller(message))
            
            logger.info(f"put deferred task {id(task)} call at {when} seconds to {message.endpoint}")
            
            return task

        # NOTE: remove logging from there
        # and return tuple(passed, isfree)
        def is_free(self):
            passed = self.time - self._last_send_time
            isfree = passed >= self._delay

            logger.info(f"passed time {passed}, isfree: {'Yes' if isfree else 'No'}")

            return isfree

        def close(self):
            if self._handler_wait_for_send:
                self._handler_wait_for_send.cancel()


class DebuggerApi:
    """ Facade layer for WEB """
    
    def __init__(self, debugger, http_request):
        self._debugger = debugger
        self._http_request = http_request

    def request(self, rid):
        return {'item': self._debugger.api.request(rid)}

    def requests(self):
        return self._debugger.api.requests()

    def messages(self, rid, page, perpage):
        return {
            'collection': self._debugger.api.messages(rid, page, perpage),
            'total': self._debugger.api.count_by_direction(rid),
            'incoming': self._debugger.api.count_by_direction(rid, MsgDirection.INCOMING),
            'outbound': self._debugger.api.count_by_direction(rid, MsgDirection.OUTBOUND)
        }

    def routes(self):
        routes = []

        for route in self._http_request.app.router.routes():
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
