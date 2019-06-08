from uuid import uuid4
from collections import defaultdict, Sequence


class PubSub:
    def __init__(self):
        self._handlers = []

    def on(self, event, handler, name='default'):
        if isinstance(event, list):
            events = event
        else:
            events = [event]

        for event in events:
            self._on(event, handler, name)

    def _on(self, event, handler, name):
        self._handlers.append((event, handler, name))

    def off(self, event=None, name=None):
        for event_, handler, name_ in self._handlers[:]:
            if event_ == event or name_ == name:
                self._handlers.remove((event_, handler, name_))

    def fire(self, event, parameters):
        for event_, handler, name in self._handlers:
            if event_ == event:
                handler(event, parameters)
