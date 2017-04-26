"""
todo: Refact this module
"""

from .debugger import (Debugger, WsMsgIncoming, WsMsgOutbound,
                       HttpRequest, HttpResponse, MsgDirection)
from .helper import casemethod
from operator import itemgetter
from asyncio import sleep, ensure_future, get_event_loop
from time import time
from collections import defaultdict
import warnings
import ujson


class WsMsgDispatcher:

    def __init__(self, sender):
        self._debugger = Debugger.instance
        self._sender = sender

    @casemethod
    def recive(req_msg):
        return req_msg.endpoint

    @recive.case('sibsribe.request')
    async def recive(self, req_msg):
        rid = int(req_msg.data['id'])

        def res_msg():
            return dict(item=self._debugger.api.request(rid))

        def on(event):
            if event.rid == rid:
                self._sender.fire(
                    req_msg.endpoint,
                    lambda: (res_msg(), req_msg))

        self._debugger.on(HttpRequest, on, group=self._sender.id, hid=req_msg.uid)
        self._debugger.on(HttpResponse, on, group=self._sender.id, hid=req_msg.uid)

        return res_msg()

    @recive.case('sibsribe.request.messages')
    async def recive(self, req_msg):

        rid = int(req_msg.data['id'])
        page = int(req_msg.data['page'])
        perpage = int(req_msg.data['perpage'])

        def res_msg():
            return dict(
                collection=self._debugger.api.messages(rid, page, perpage),
                total=self._debugger.api.count_by_direction(rid),
                incoming=self._debugger.api.count_by_direction(rid, MsgDirection.INCOMING),
                outbound=self._debugger.api.count_by_direction(rid, MsgDirection.OUTBOUND)
            )

        def on(event: WsMsgIncoming or WsMsgOutbound):
            if event.rid == rid:
                self._sender.fire(
                    req_msg.endpoint,
                    lambda: (res_msg(), req_msg))

        self._debugger.on(WsMsgIncoming, on, group=self._sender.id, hid=req_msg.uid)
        self._debugger.on(WsMsgOutbound, on, group=self._sender.id, hid=req_msg.uid)

        return res_msg()

    @recive.case('sibsribe.requests')
    async def recive(self, req_msg):

        def res_msg():
            return self._debugger.api.requests()

        def on(event):
            self._sender.fire(
                req_msg.endpoint,
                lambda: (res_msg(), req_msg))

        self._debugger.on(HttpRequest, on, group=self._sender.id, hid=req_msg.uid)
        self._debugger.on(HttpResponse, on, group=self._sender.id, hid=req_msg.uid)

        return res_msg()

    @recive.case('unsibscribe')
    async def recive(self, req_msg):
        """ with this hid maybe be multiple handlers """
        self._debugger.off(hid=req_msg.data['id'])

    @recive.case('fetch.info')
    async def recive(self, req_msg):
        return self._debugger.api.platform_info()

    @recive.case('fetch.routes')
    async def recive(self, req_msg):
        return self._debugger.api.routes()

    @recive.default
    async def recive(self, req_msg):
        return {"status": "endpoint not found"}

    @recive.catch(Exception)
    async def recive(self, exception):
        """ TODO - async exception not catch by this way """
        return {"status": "error", "cause": str(exception)}

    def close(self):
        self._debugger.off(group=self._sender.id)

    def _send(self, res_msg, req_msg):
        self._sender.put(res_msg, req_msg)


class Sender:

    def __init__(self, socket):
        self._socket = socket
        self._endpoints = defaultdict(lambda: None)

    def fire(self, endpoint, args_getter):
        send_token = self._endpoints[endpoint]

        if send_token is None:
            send_token = self._endpoints[endpoint] = \
                self.Proxy(handler=self._send)

            send_token.send_soon(args_getter=args_getter)
        elif send_token.isready:
            send_token.send_soon(args_getter=args_getter)
        else:
            send_token.send_later(args_getter=args_getter)

    def _send(self, res_msg, req_msg):
        if not self._socket.closed:
            self._socket.send_json(self._prepare_ws_response(res_msg, req_msg),
                dumps=ujson.dumps)
        else:
            warnings.warn('try send into closed websoclet connection')

    def _prepare_ws_response(self, res_msg, req_msg):
        return dict(data=res_msg, uid=req_msg.uid, endpoint=req_msg.endpoint)

    @property
    def id(self):
        return self._socket.id

    class Proxy:
        _loop = get_event_loop()
        _delay = 2
        _handler = None
        _last_send_time = None
        _handler_wait_for_send = None

        def __init__(self, handler):
            self._handler = handler
            self._last_send_time = self._loop.time()

        def _handler_caller(self, args_getter):
            self._handler(*args_getter())
            self._handler_wait_for_send = None
            self._last_send_time = self._loop.time()

        def send_soon(self, args_getter):
            self._handler_caller(args_getter)

        def send_later(self, args_getter):

            if self._handler_wait_for_send:
                self._handler_wait_for_send.cancel()

            self._handler_wait_for_send = self._do_send_later(args_getter)

        def _do_send_later(self, args_getter):
            return self._loop.call_at(
                self._last_send_time + self._delay,
                lambda: self._handler_caller(args_getter)
            )

        @property
        def isready(self):
            return (self._loop.time() - self._last_send_time) >= self._delay


class WsMsgDispatcherProxy:
    def __init__(self, dispatcher, sender):
        self._dispatcher = dispatcher
        self._sender = sender

    async def recive(self, req_msg):
        res_msg = await self._dispatcher.recive(req_msg)
        self._sender.fire(
            req_msg.endpoint,
            lambda: (res_msg, req_msg))

    def close(self):
        return self._dispatcher.close()
