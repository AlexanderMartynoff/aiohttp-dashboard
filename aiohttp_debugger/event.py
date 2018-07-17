from enum import Enum
from uuid import uuid4
from collections import defaultdict, OrderedDict, Sequence


class Bus:
    def __init__(self):
        self._handlers = defaultdict(list)

    def on(self, event, handler, *, group=uuid4(), hid=uuid4()):
        if not isinstance(event, Sequence):
            event = [event]

        for _ in event:
            self._on(_, handler, group=group, hid=hid)

        return self

    def _on(self, event, handler, *, group, hid):
        self._handlers[group] += (event, handler, hid),

    def off(self, *, group=None, hid=None):
        if group is None and hid is None:
            raise ValueError('group or/and hid must be not None')

        if group:
            try:
                del self._handlers[group]
            except KeyError:
                pass

        if hid:
            for group_, handlers in self._handlers.items():
                for type, handler, hid_ in handlers[:]:
                    if hid_ == hid:
                        self._handlers[group_].remove((type, handler, hid_))

    def fire(self, event):
        for handlers in self._handlers.values():
            for type, handler, hid in handlers:
                if isinstance(event, type):
                    handler(event)

    @property
    def size(self):
        return sum(len(handlers) for handlers in self._handlers.values())

    class Event:
        pass


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
