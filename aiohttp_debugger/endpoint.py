from .debugger import Debugger, WsMsgIncoming, WsMsgOutbound, HttpRequest, HttpResponse, MsgDirection
from .helper import casemethod
from operator import itemgetter
from asyncio import sleep, ensure_future, get_event_loop
from time import time
from collections import defaultdict
import warnings
import ujson
import logging
import concurrent.futures
from collections import namedtuple
from time import sleep, time
import re


log = logging.getLogger("aiohttp_debugger.endpoint")


class WsMsgDispatcherProxy:
    """ Passing websocket meessage
        into target method for processing.
    """
    _counter = 0
    
    def __init__(self, dispatcher, sender):
        self._dispatcher = dispatcher
        self._sender = sender

        self.__class__._counter += 1

    def recive(self, inmsg):
        self._sender.send_soon(inmsg, self._dispatcher.recive(inmsg))

    @property
    def counter(self):
        return self.__class__._counter

    def close(self):
        return self._dispatcher.close()


class WsMsgDispatcher:
    """ Endpoints for websocket message processing.
        For more info see `.helper.casemethod`.
        For more info about `rid = inmsg.body.id @ int` see `helper.WsResponseHelper`
    """

    def __init__(self, sender):
        self._debugger_api = DebuggerApi()
        self._debugger = Debugger.instance
        self._sender = sender
    
    @casemethod
    def recive(inmsg):
        return inmsg.endpoint
    
    @recive.case('sibsribe.request')
    def recive(self, inmsg):
        rid = inmsg.body.id >> int

        def handler(event):
            if event.rid == rid:
                self._sender.send(inmsg)

        self._debugger.on(HttpRequest, handler, group=self._sender.id, hid=inmsg.uid)
        self._debugger.on(HttpResponse, handler, group=self._sender.id, hid=inmsg.uid)

        return self._debugger_api.request(rid)

    @recive.case('sibsribe.request.messages')
    def recive(self, inmsg):
        rid = inmsg.body.id >> int
        page = inmsg.body.page >> int
        perpage = inmsg.body.perpage >> int

        def handler(event: (WsMsgIncoming, WsMsgOutbound)):
            if event.rid == rid:
                self._sender.send(inmsg)

        self._debugger.on(WsMsgIncoming, handler, group=self._sender.id, hid=inmsg.uid)
        self._debugger.on(WsMsgOutbound, handler, group=self._sender.id, hid=inmsg.uid)

        return self._debugger_api.messages(rid, page, perpage)

    @recive.case('sibsribe.requests')
    def recive(self, inmsg):
        def handler(event):
            self._sender.send(inmsg)

        self._debugger.on(HttpRequest, handler, group=self._sender.id, hid=inmsg.uid)
        self._debugger.on(HttpResponse, handler, group=self._sender.id, hid=inmsg.uid)

        return self._debugger_api.requests()

    @recive.case('unsibscribe')
    def recive(self, inmsg):
        """ with this `hid` probably exist multiple handlers """
        self._debugger.off(hid=inmsg.body.id.raw)

    @recive.case('fetch.info')
    def recive(self, inmsg):
        return self._debugger_api.platform_info()

    @recive.case('fetch.routes')
    def recive(self, inmsg):
        return self._debugger.api.routes()

    @recive.default
    def recive(self, inmsg):
        return {'status': 'endpoint not found'}

    @recive.catch(Exception)
    def recive(self, exception, inmsg):
        self._sender.send_soon(inmsg, {
            'status': 'error',
            'cause': str(exception)
        })

    def close(self):
        log.info(f"will off for debugger handlers - {self._debugger.subscribers_len}")
        self._debugger.off(group=self._sender.id)
        log.info(f"was off for debugger handlers - {self._debugger.subscribers_len}")


class Sender:
    """ Use for deferred sending websocket message """

    def __init__(self, socket, debugger_api):
        self._socket = socket
        self._debugapi = debugger_api
        self._endpoints = defaultdict(lambda: None)

    @casemethod
    def handler(inmsg):
        """ For handle debugger state change. """
        return inmsg.endpoint

    @handler.case('sibsribe.request')
    def _handler(self, inmsg):
        self._send(self._debugapi.request(inmsg.body.id >> int), inmsg)

    @handler.case('sibsribe.request.messages')
    def _handler(self, inmsg):
        rid = inmsg.body.id >> int
        page = inmsg.body.page >> int
        perpage = inmsg.body.perpage >> int
        self._send(self._debugapi.messages(rid, page, perpage), inmsg)

    @handler.case('sibsribe.requests')
    def _handler(self, inmsg):
        self._send(self._debugapi.requests(), inmsg)

    @property
    def _endpoint_state(self):
        return self._EndpointState(handler=self._handler)

    def send_soon(self, inmsg, out):
        endpoint = self._endpoints[inmsg.endpoint]

        if endpoint is None:
            endpoint = self._endpoints[inmsg.endpoint] = self._endpoint_state

        endpoint.handle_soon_with_handler(inmsg, out, self._send)

    def send(self, inmsg):
        """ :inmsg: incoming websocket message
        """
        
        log.info("try to send data for {inmsg.endpoint}")

        endpoint = self._endpoints[inmsg.endpoint]

        if endpoint is None:
            endpoint = self._endpoints[inmsg.endpoint] = self._endpoint_state
            endpoint.handle_soon(inmsg)
        elif endpoint.isfree:
            endpoint.handle_soon(inmsg)
        else:
            endpoint.handle_later(inmsg)

    def _send(self, out, inmsg):
        try:
            # await self._socket.close()
            self._socket.send_json(self._prepare_ws_response(out, inmsg), dumps=ujson.dumps)
        except RuntimeError as error:
            log.error(f"an error while send data to debugger client: {error}")

    def _prepare_ws_response(self, out, inmsg):
        return dict(data=out, uid=inmsg.uid, endpoint=inmsg.endpoint)

    @property
    def id(self):
        return self._socket.id

    # not for use from out
    del handler

    class _EndpointState:
        _delay = 4
        _handler = None
        _last_send_time = None
        _handler_wait_for_send = None

        def __init__(self, handler):
            self._handler = handler
            self._last_send_time = self.time

        @property
        def time(self):
            return time()

        def _handler_caller(self, inmsg, task=None):
            if task:
                log.info(f"send from task {id(task)}")
            
            self._handler(inmsg)
            self._handler_wait_for_send = None
            self._last_send_time = self.time

        def handle_soon_with_handler(self, inmsg, out, handler):
            handler(out, inmsg)

        def handle_soon(self, inmsg):
            self._handler_caller(inmsg)

        def handle_later(self, inmsg):
            if self._handler_wait_for_send:
                self._handler_wait_for_send.cancel()
                log.info(f"cancel deferred task {id(self._handler_wait_for_send)}")

            self._handler_wait_for_send = self._do_send_later(inmsg)

        def _do_send_later(self, inmsg):
            when = self._last_send_time + self._delay
            task = get_event_loop().call_at(when, lambda: self._handler_caller(inmsg, task))
            log.info(f"put deferred task {id(task)} call at {when} seconds to {inmsg.endpoint}")
            return task

        @property
        def isfree(self):
            passed = self.time - self._last_send_time
            isfree = passed >= self._delay
            log.info(f"passed time {passed}, isfree: {'Yes' if isfree else 'No'}")
            return isfree


class DebuggerApi:
    """ Facade layer for WEB.
    """
    
    def __init__(self):
        self._debugger = Debugger.instance

    def request(self, rid):
        return dict(item=self._debugger.api.request(rid))

    def requests(self):
        return self._debugger.api.requests()

    def messages(self, rid, page, perpage):
        return dict(
            collection=self._debugger.api.messages(rid, page, perpage),
            total=self._debugger.api.count_by_direction(rid),
            incoming=self._debugger.api.count_by_direction(rid, MsgDirection.INCOMING),
            outbound=self._debugger.api.count_by_direction(rid, MsgDirection.OUTBOUND)
        )

    def unsibscribe(self, hid):
        return self._debugger.off(hid=hid)

    def platform_info(self):
        return self._debugger.api.platform_info()

    def routes(self):
        return self._debugger.api.routes()
