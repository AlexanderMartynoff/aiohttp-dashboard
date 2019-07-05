from asyncio import sleep
from aiohttp_dashboard._event_emitter import EventEmitter
import pytest


def _emitter_length(emitter):
    return len(emitter._handlers)


@pytest.fixture
def _emitter():
    return EventEmitter()


def test_subcribtion_single_event_count(_emitter):
    events = []

    def handler(event, parameters):
        events.append(event)

    _emitter.on('a', handler)

    _emitter.fire('a', None)
    _emitter.fire('a', None)

    assert len(events) == 2


def test_subcribtion_multiple_event_count(_emitter):
    events = []

    def handler(event, parameters):
        events.append(event)

    _emitter.on(['a', 'b'], handler)

    _emitter.fire('a', None)
    _emitter.fire('b', None)

    assert len(events) == 2


def test_subcribtion_event_equals(_emitter):
    fired_event = None
    event = 'a'

    def handler(event, parameters):
        nonlocal fired_event
        fired_event = event

    _emitter.on('a', handler)
    _emitter.fire(event, None)

    assert fired_event is event


def test_subcribtion_handler_count(_emitter):
    def handler(event, parameters):
        pass

    _emitter.on('a', handler)
    _emitter.on('b', handler)

    assert _emitter_length(_emitter) == 2


def test_unsubcribtion_family(_emitter):

    def handler(event, parameters):
        pass

    _emitter.on('a', handler, family='1')
    _emitter.on('b', handler, family='1')

    assert _emitter_length(_emitter) == 2

    _emitter.off(family='1')
    assert _emitter_length(_emitter) == 0


def test_unsubcribtion_name(_emitter):

    def handler(event, parameters):
        pass

    _emitter.on('a', handler, '1')
    _emitter.on('b', handler, '2')

    _emitter.off(name='1')
    assert _emitter_length(_emitter) == 1

    _emitter.off(name='2')
    assert _emitter_length(_emitter) == 0


def test_unsubcribtion_default_name(_emitter):
    def handler(event, parameters):
        pass

    _emitter.on('a', handler)
    _emitter.on('b', handler)

    _emitter.off(name='default')

    assert _emitter_length(_emitter) == 0


def test_parameters(_emitter):
    parameters_ = {}

    def handler(event, parameters):
        assert parameters_ is parameters

    _emitter.on('a', handler)
    _emitter.fire('a', parameters_)
