from .debugger import Debugger
from .helper import casemethod


class WsMsgDispatcherProxy:
    def __init__(self, socket, dispatcher):
        self._socket = socket
        self._dispatcher = dispatcher

    async def recive(self, msg):
        self._socket.send_json(self._prepare_response(
            msg, await self._dispatcher.recive(msg)))

    def _prepare_response(self, msg, response):
        response_type, data = response
        return dict(data=data, uid=msg.uid, type=response_type)


class WsMsgDispatcher:
    """

    Answers types:
        - fetch
        - subscribe
        - fire
        - undefined

        Recive methods must return tuple:
            (response_type: string, payload: any)
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
        return "sibsribe", {}

    @recive.default
    async def recive(self, msg):
        return "undefined", {}
