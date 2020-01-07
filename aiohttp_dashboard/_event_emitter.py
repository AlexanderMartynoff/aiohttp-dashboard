from __future__ import annotations

from uuid import uuid4
from collections import defaultdict, Sequence
from typing import (
    Union,
    List,
    Callable,
    TypeVar,
    Generic,
    Any,
    Dict,
    Optional
)


_Event = Union[str, List[str]]
_Handler = Callable[[_Event, Dict[Any, Any]], None]


class EventEmitter:

    def __init__(self):
        self._handlers: List[_Handler] = []

    def on(self, event: _Event, handler: _Handler,
           name: str = 'default', family: str = 'default') -> None:

        if isinstance(event, list):
            events = event
        else:
            events = [event]

        for event in events:
            self._on(event, handler, name, family)

    def _on(self, event: str, handler: _Handler, name: str, family: str):
        self._handlers.append((event, handler, name, family))

    def off(self, name: Optional[str] = None,
            family: Optional[str] = None) -> None:
        # DOIT: rename these vars but how? 
        for event_, handler, name_, family_ in self._handlers[:]:
            if name_ == name or family_ == family:
                self._handlers.remove((event_, handler, name_, family_))

    def fire(self, event: str, parameters: dict) -> None:
        for event_, handler, name, family in self._handlers:
            if event_ == event:
                handler(event, parameters)
