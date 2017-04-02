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
        rid = int(msg.data['id'])

        def on(event):
            self._send_json(self._debugger.api.request(rid), msg)

        self._debugger.on(WsMsgIncoming, on, group=self._socket.id, hid=msg.uid)
        self._debugger.on(WsMsgOutbound, on, group=self._socket.id, hid=msg.uid)

        return self._debugger.api.request(rid)

    @recive.case('fetch.requests')
    async def recive(self, msg):
        return self._debugger.api.requests

    @recive.case('sibsribe.requests')
    async def recive(self, msg):

        def on(event):
            self._send_json(self._debugger.api.requests, msg)

        self._debugger.on(HttpRequest, on, group=self._socket.id, hid=msg.uid)
        self._debugger.on(HttpResponse, on, group=self._socket.id, hid=msg.uid)

        return self._debugger.api.requests

    @recive.case('unsibscribe')
    async def recive(self, msg):
        self._debugger.off(hid=msg.data['id'])

    @recive.default
    async def recive(self, msg):
        return {"status": "endpoint not found"}

    @recive.catch(Exception)
    async def recive(self, exception):
        """ TODO - async eception not catch with this way """
        return {"status": "error", "cause": str(exception)}

    def close(self):
        self._debugger.off(group=self._socket.id)

    def _send_json(self, json, msg):
        if not self._socket.closed:
            self._socket.send_json(_prepare_ws_response(json, msg))
