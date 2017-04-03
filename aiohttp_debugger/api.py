from .debugger import (Debugger, WsMsgIncoming, WsMsgOutbound,
                       HttpRequest, HttpResponse)
from .helper import casemethod
from operator import itemgetter
from asyncio import sleep, ensure_future


class Sender:
    _timeout = 1

    def __init__(self, socket):
        self._socket = socket
        self._endpoints = dict()
        self._is_run = False

    def put(self, res_msg, req_msg):
        self._endpoints[req_msg.endpoint] = res_msg, req_msg

        if not self._is_run:
            ensure_future(self._start())
            self._is_run = True

    def _send(self, res_msg, req_msg):
        self._socket.send_json(self._prepare_ws_response(res_msg, req_msg))

    async def _start(self):
        while True:
            for endpoint, pair in list(self._endpoints.items()):
                self._send(*pair)
                del self._endpoints[endpoint]
            await sleep(self._timeout)

    def _prepare_ws_response(self, res_msg, req_msg):
        return dict(data=res_msg, uid=req_msg.uid, endpoint=req_msg.endpoint)

    @property
    def id(self):
        return self._socket.id


class WsMsgDispatcherProxy:
    def __init__(self, dispatcher, sender):
        self._dispatcher = dispatcher
        self._sender = sender

    async def recive(self, req_msg):
        self._sender.put(await self._dispatcher.recive(req_msg), req_msg)

    def close(self):
        return self._dispatcher.close()


class WsMsgDispatcher:

    def __init__(self, sender):
        self._debugger = Debugger.self
        self._sender = sender

    @casemethod
    def recive(req_msg):
        return req_msg.endpoint

    @recive.case('sibsribe.request')
    async def recive(self, req_msg):
        rid = int(req_msg.data['id'])

        def response():
            return dict(item=self._debugger.api.request(rid))

        def on(event):
            self._send(response(), req_msg)

        self._debugger.on(HttpRequest, on, group=self._sender.id, hid=req_msg.uid)
        self._debugger.on(HttpResponse, on, group=self._sender.id, hid=req_msg.uid)

        return response()

    @recive.case('sibsribe.request.messages')
    async def recive(self, req_msg):
        rid = int(req_msg.data['id'])
        page = int(req_msg.data['page'])
        perpage = int(req_msg.data['perpage'])

        def res_msg():
            return dict(
                collection=self._debugger.api.messages(rid, page, perpage),
                total=self._debugger.api.messages(rid, perpage=-1).__len__(),
                incoming=self._debugger.api.incoming_messages(rid).__len__(),
                outbound=self._debugger.api.outbound_messages(rid).__len__()
            )

        def on(event):
            self._send(res_msg(), req_msg)

        self._debugger.on(WsMsgIncoming, on, group=self._sender.id, hid=req_msg.uid)
        self._debugger.on(WsMsgOutbound, on, group=self._sender.id, hid=req_msg.uid)

        return res_msg()

    @recive.case('sibsribe.requests')
    async def recive(self, req_msg):

        def res_msg():
            return self._debugger.api.requests

        def on(event):
            self._send(res_msg(), req_msg)

        self._debugger.on(HttpRequest, on, group=self._sender.id, hid=req_msg.uid)
        self._debugger.on(HttpResponse, on, group=self._sender.id, hid=req_msg.uid)

        return res_msg()

    @recive.case('unsibscribe')
    async def recive(self, req_msg):
        self._debugger.off(hid=req_msg.data['id'])

    @recive.default
    async def recive(self, req_msg):
        return {"status": "endpoint not found"}

    @recive.catch(Exception)
    async def recive(self, exception):
        """ TODO - async eception not catch with this way """
        return {"status": "error", "cause": str(exception)}

    def close(self):
        self._debugger.off(group=self._sender.id)

    def _send(self, res_msg, req_msg):
        self._sender.put(res_msg, req_msg)
