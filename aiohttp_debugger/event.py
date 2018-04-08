from enum import Enum

from .tool import Bus


class DebuggerAbstractWebEvent(Bus.Event):
    _rid = None

    def __init__(self, rid=None):
        self._rid = rid

    @property
    def rid(self):
        return self._rid

    @rid.setter
    def rid(self, rid):
        self._rid = rid


class DebuggerAbstractReqResEvent(DebuggerAbstractWebEvent):
    def __init__(self, rid):
        self.rid = rid


class HttpRequest(DebuggerAbstractReqResEvent):
    def __init__(self, rid):
        super().__init__(rid)


class HttpResponse(DebuggerAbstractWebEvent):
    def __init__(self, rid):
        super().__init__(rid)


class WsMsgIncoming(DebuggerAbstractWebEvent):
    pass


class WsMsgOutbound(DebuggerAbstractWebEvent):
    pass

# ticket for web socket messages
class MsgDirection(Enum):
    OUTBOUND = 1
    INCOMING = 2
