"""
Need refact:
    1 - Maybe remove casemethod?
    2 - Remove DebuggerApi.
    3 - Replace msg.body.id >> int with message schema.

Cover tests after refact!
"""

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
from .tool import casemethod


logger = logging.getLogger("aiohttp_debugger.endpoint")


class WsMsgDispatcherProxy:
    """ Passing websocket meessage
        into target method for processing.
    """

    def __init__(self, socket, debugger, request):
        debugger_api = DebuggerApi(debugger, request)

        self._sender = sender = Sender(socket, debugger_api)
        self._dispatcher = WsMsgDispatcher(sender, debugger_api, debugger)

    def recive(self, message):
        self._sender.send_soon(message, self._dispatcher.recive(message))

    def close(self):
        self._dispatcher.close()
        self._sender.close()


class WsMsgDispatcher:
    """ Endpoints for websocket message processing.
        For more info see `.helper.casemethod`.
        For more info about `rid = inmsg.body.id @ int` see `helper.WsResponseHelper`
    """

    def __init__(self, sender, debugger_api, debugger):
        self._debugger = debugger
        self._sender = sender
        self._debugger_api = debugger_api
    
    @casemethod
    def recive(msg):
        return msg.endpoint

    @recive.case('sibsribe.request')
    def recive(self, msg):
        rid = msg.body.id >> int

        def handler(event):
            if event.rid == rid:
                self._sender.send(msg)

        self._debugger.on([
            HttpRequest,
            HttpResponse
        ], handler, group=self._sender.id, hid=msg.uid)

        return self._debugger_api.request(rid)

    @recive.case('sibsribe.request.messages')
    def recive(self, msg):
        rid = msg.body.id >> int
        page = msg.body.page >> int
        perpage = msg.body.perpage >> int

        def handler(event: (WsMsgIncoming, WsMsgOutbound)):
            if event.rid == rid:
                self._sender.send(msg)

        self._debugger.on([
            WsMsgIncoming,
            WsMsgOutbound
        ], handler, group=self._sender.id, hid=msg.uid)

        return self._debugger_api.messages(rid, page, perpage)

    @recive.case('sibsribe.requests')
    def recive(self, msg):

        def handler(event):
            self._sender.send(msg)

        self._debugger.on([
            HttpRequest,
            HttpResponse
        ], handler, group=self._sender.id, hid=msg.uid)

        return self._debugger_api.requests()

    @recive.case('unsibscribe')
    def recive(self, msg):
        """ with this `hid` probably exist multiple handlers """

        self._debugger.off(hid=msg.body.id.raw)

    @recive.case('fetch.info')
    def recive(self, msg):
        return self._debugger_api.platform_info()

    @recive.case('fetch.routes')
    def recive(self, msg):
        return self._debugger_api.routes()

    @recive.default
    def recive(self, msg):
        return {'status': 'endpoint not found'}

    @recive.catch(Exception)
    def recive(self, exception, msg):
        self._sender.send_soon(msg, {
            'status': 'error',
            'cause': str(exception)
        })

    def close(self):
        logger.info(f"before remove debugger handlers - {self._debugger.subscribers_len}")
        self._debugger.off(group=self._sender.id)
        logger.info(f"after remove debugger handlers - {self._debugger.subscribers_len}")


class Sender:
    """ Use for deferred sending websocket message """

    def __init__(self, socket, debugger_api):
        self._socket = socket
        self._debugger_api = debugger_api
        self._endpoints = defaultdict(lambda: None)

    @casemethod
    def handler(msg):
        """ For handle debugger state change """
        return msg.endpoint

    @handler.case('sibsribe.request')
    def _handler(self, msg):
        self._send(self._debugger_api.request(msg.body.id >> int), msg)

    @handler.case('sibsribe.request.messages')
    def _handler(self, msg):
        rid = msg.body.id >> int
        page = msg.body.page >> int
        perpage = msg.body.perpage >> int
        self._send(self._debugger_api.messages(rid, page, perpage), msg)

    @handler.case('sibsribe.requests')
    def _handler(self, msg):
        self._send(self._debugger_api.requests(), msg)
    
    # not for use from public
    del handler
    
    # NOTE: refact this
    @property
    def _endpoint_state(self):
        return self._EndpointState(handler=self._handler)

    def send_soon(self, msg, out):
        endpoint = self._endpoints[msg.endpoint]

        if endpoint is None:
            endpoint = self._endpoints[msg.endpoint] = self._endpoint_state

        endpoint.handle_soon_with_handler(msg, out, self._send)

    def send(self, msg):

        logger.info(f"try to send data for {msg.endpoint}")

        endpoint = self._endpoints[msg.endpoint]

        if endpoint is None:
            endpoint = self._endpoints[msg.endpoint] = self._endpoint_state
            endpoint.handle_soon(msg)
        elif endpoint.isfree:
            endpoint.handle_soon(msg)
        else:
            endpoint.handle_later(msg)

    def close(self):
        for endpoint_state in self._endpoints.values():
            endpoint_state.close()

    def _send(self, out, msg):
        logger.info(f'send websocket to chanel {msg.endpoint}')
        return ensure_future(self._socket.send_json(self._prepare_ws_response(out, msg)))

    def _prepare_ws_response(self, out, msg):
        return {'data': out, 'uid': msg.uid, 'endpoint': msg.endpoint}

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

        def _handler_caller(self, msg):
            self._handler(msg)
            self._handler_wait_for_send = None
            self._last_send_time = self.time

        def handle_soon_with_handler(self, msg, out, handler):
            handler(out, msg)

        def handle_soon(self, msg):
            self._handler_caller(msg)

        def handle_later(self, msg):
            if self._handler_wait_for_send:
                self._handler_wait_for_send.cancel()
                logger.info(f"cancel deferred task {id(self._handler_wait_for_send)}")

            self._handler_wait_for_send = self._do_send_later(msg)

        def _do_send_later(self, msg):
            when = self._last_send_time + self._delay
            task = get_event_loop().call_at(when, lambda: self._handler_caller(msg))
            logger.info(f"put deferred task {id(task)} call at {when} seconds to {msg.endpoint}")
            return task

        @property
        def isfree(self):
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
