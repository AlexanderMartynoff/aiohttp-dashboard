from enum import Enum
from uuid import uuid4
from collections import defaultdict, Sequence


class EventDriven:
    def __init__(self):
        self._handlers = defaultdict(list)

    def on(self, events, handler, *, group=uuid4(), hid=uuid4()):
        if not isinstance(events, Sequence):
            events = [events]

        for event in events:
            self._on(event, handler, group=group, hid=hid)

        return self

    def _on(self, event, handler, *, group, hid):
        self._handlers[group] += (event, handler, hid),

    # NOTE: add prefix `target_` to name for `group` and `hid`
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


class DebuggerAbstractWebEvent(EventDriven.Event):

    def __init__(self, rid):
        self._rid = rid

    @property
    def rid(self):
        return self._rid


class HttpRequest(DebuggerAbstractWebEvent):
    pass


class HttpResponse(DebuggerAbstractWebEvent):
    pass


class WsMsgIncoming(DebuggerAbstractWebEvent):
    pass


class WsMsgOutbound(DebuggerAbstractWebEvent):
    pass


# ticket for web socket messages
class MsgDirection(Enum):
    OUTBOUND = 1
    INCOMING = 2
