from uuid import uuid4
from collections import defaultdict, Sequence


class PubSub:
    def __init__(self):
        self._handlers = []

    def on(self, event, handler, name='default', family='default'):
        if isinstance(event, list):
            events = event
        else:
            events = [event]

        for event in events:
            self._on(event, handler, name, family)

    def _on(self, event, handler, name, family):
        self._handlers.append((event, handler, name, family))

    def off(self, name=None, family=None):
        for event_, handler, name_, family_ in self._handlers[:]:
            if name_ == name or family_ == family:
                self._handlers.remove((event_, handler, name_, family_))

    def fire(self, event, parameters):
        for event_, handler, name, family in self._handlers:
            if event_ == event:
                handler(event, parameters)
