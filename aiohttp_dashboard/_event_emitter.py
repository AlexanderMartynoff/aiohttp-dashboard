from uuid import uuid4
from collections import defaultdict, Sequence
from typing import Union, List, Callable, TypeVar, Generic, Any, Dict


Event_T = Union[str, List[str]]
EventHandler_T = Callable[[Event_T, Dict[Any, Any]], None]


class EventEmitter:
    _handlers: List[EventHandler_T]

    def __init__(self):
        self._handlers = []

    def on(self, event: Event_T, handler: EventHandler_T,
           name: str ='default', family: str = 'default'):

        if isinstance(event, list):
            events = event
        else:
            events = [event]

        for event in events:
            self._on(event, handler, name, family)

    def _on(self, event: str, handler: EventHandler_T, name: str, family: str):
        self._handlers.append((event, handler, name, family))

    def off(self, name=None, family=None):
        # DOIT: rename these vars but how? 
        for event_, handler, name_, family_ in self._handlers[:]:
            if name_ == name or family_ == family:
                self._handlers.remove((event_, handler, name_, family_))

    def fire(self, event, parameters: Dict[Any, Any]):
        for event_, handler, name, family in self._handlers:
            if event_ == event:
                handler(event, parameters)
