from uuid import uuid4
from collections import defaultdict, Sequence


class PubSub:
    def __init__(self):
        self._handlers = defaultdict(list)

    def on(self, events, handler, *, gid='default', hid=None):
        if not isinstance(events, Sequence):
            events = [events]

        for event in events:
            self._on(event, handler, gid=gid, hid=hid)

    def _on(self, event, handler, *, gid, hid):
        self._handlers[gid].append((event, handler, hid))

    def off(self, *, gid=None, hid=None):
        if hid:
            for gid_, handlers in self._handlers.items():
                for event_type, handler, hid_ in handlers[:]:
                    if hid_ == hid:
                        self._handlers[gid_].remove(
                            (event_type, handler, hid_))

        if gid:
            try:
                del self._handlers[gid]
            except KeyError:
                pass

    def fire(self, event):
        for handlers in self._handlers.values():
            for event_type, handler, hid in handlers:
                if isinstance(event, event_type):
                    handler(event)


class Event:
    pass


class DebuggerAbstractWebEvent(Event):

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
