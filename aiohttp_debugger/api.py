from .debugger import Debugger, WsMsgIncoming, WsMsgOutbound
from .helper import casemethod


def _prepare_ws_response(res_type, res, msg):
    return dict(data=res, uid=msg.uid, type=res_type)


class WsMsgDispatcherProxy:
    def __init__(self, socket, dispatcher):
        self._socket = socket
        self._dispatcher = dispatcher

    async def recive(self, msg):
        res_type, res = await self._dispatcher.recive(msg)
        self._socket.send_json(_prepare_ws_response(
            res_type, res, msg))


class WsMsgDispatcher:
    """

    Answers types:
        - fetch
        - subscribe
        - fire
        - undefined

        Recive methods must return tuple: (res_type: string, payload: any)
    """

    def __init__(self, socket):
        self._debugger = Debugger.self
        self._socket = socket

    @casemethod
    def recive(msg):
        return msg.endpoint

    @recive.case('fetch.requests')
    async def recive(self, msg):
        return "fetch", self._debugger.api.requests

    @recive.case('sibsribe.requests')
    async def recive(self, msg):

        def listener(event):
            self._send_json(
                "fire.WsMsgIncoming", self._debugger.api.requests, msg)

        self._debugger.on(WsMsgIncoming, listener)
        self._debugger.on(WsMsgOutbound, listener)

        return "sibsribe", self._debugger.api.requests

    @recive.default
    async def recive(self, msg):
        return "undefined", {}

    def _send_json(self, res_type, json, msg):
        if not self._socket.closed:
            self._socket.send_json(_prepare_ws_response(res_type, json, msg))
