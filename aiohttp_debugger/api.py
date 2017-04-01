from .debugger import (Debugger, WsMsgIncoming, WsMsgOutbound,
                       HttpRequest, HttpResponse)
from .helper import casemethod
from operator import itemgetter


def _prepare_ws_response(res, msg):
    return dict(data=res, uid=msg.uid, endpoint=msg.endpoint)


class WsMsgDispatcherProxy:
    def __init__(self, socket, dispatcher):
        self._socket = socket
        self._dispatcher = dispatcher

    async def recive(self, msg):
        self._socket.send_json(
            _prepare_ws_response(await self._dispatcher.recive(msg), msg))

    def close(self):
        return self._dispatcher.close()


class WsMsgDispatcher:

    def __init__(self, socket):
        self._debugger = Debugger.self
        self._socket = socket

    @casemethod
    def recive(msg):
        return msg.endpoint

    @recive.case('fetch.request')
    async def recive(self, msg):
        mid = int(msg.data['id'])
        return next((record for record in self._debugger.api.requests
                     if record['id'] == mid), None)

    @recive.case('fetch.requests')
    async def recive(self, msg):
        return self._debugger.api.requests

    @recive.case('sibsribe.requests')
    async def recive(self, msg):

        def listener(event):
            self._send_json(self._debugger.api.requests, msg)

        self._debugger.on(WsMsgIncoming, listener, self._socket.id)
        self._debugger.on(WsMsgOutbound, listener, self._socket.id)
        self._debugger.on(HttpRequest, listener, self._socket.id)
        self._debugger.on(HttpResponse, listener, self._socket.id)

        return self._debugger.api.requests

    @recive.default
    async def recive(self, msg):
        return {}

    def close(self):
        self._debugger.off(self._socket.id)

    def _send_json(self, json, msg):
        if not self._socket.closed:
            self._socket.send_json(_prepare_ws_response(json, msg))
