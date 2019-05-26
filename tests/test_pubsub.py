from asyncio import sleep
from aiohttp_dashboard._pubsub import PubSub
import pytest


class _EventA:
    pass


class _EventB:
    pass


def _pubsub_length(pubsub):
    return sum(len(handlers) for handlers in pubsub._handlers.values())


@pytest.fixture
def _pubsub():
    return PubSub()


def test_subcribtion_single_event_count(_pubsub):
    events = []

    def handler(event):
        events.append(event)

    _pubsub.on(_EventA, handler)

    _pubsub.fire(_EventA())
    _pubsub.fire(_EventA())

    assert len(events) == 2


def test_subcribtion_multiple_event_count(_pubsub):
    events = []

    def handler(event):
        events.append(event)

    _pubsub.on([_EventA, _EventB], handler)

    _pubsub.fire(_EventA())
    _pubsub.fire(_EventB())

    assert len(events) == 2


def test_subcribtion_event_type(_pubsub):
    fired_event = None
    event = _EventA()

    def handler(event):
        nonlocal fired_event
        fired_event = event

    _pubsub.on(_EventA, handler)

    _pubsub.fire(event)

    assert isinstance(fired_event, _EventA)
    assert fired_event is event


def test_subcribtion_handler_count(_pubsub):
    def handler(event):
        pass

    _pubsub.on(_EventA, handler)
    _pubsub.on(_EventA, handler)

    assert _pubsub_length(_pubsub) == 2


def test_unsubcribtion_default_gid(_pubsub):
    def handler(event):
        pass

    _pubsub.on(_EventA, handler)
    _pubsub.on(_EventB, handler)

    _pubsub.off(gid='default')

    assert _pubsub_length(_pubsub) == 0


def test_unsubcribtion_gid(_pubsub):
    def handler(event):
        pass

    _pubsub.on(_EventA, handler, gid='gid-1')
    _pubsub.on(_EventB, handler, gid='gid-2')

    _pubsub.off(gid='default')
    assert _pubsub_length(_pubsub) == 2

    _pubsub.off(gid='gid-1')
    assert _pubsub_length(_pubsub) == 1

    _pubsub.off(gid='gid-2')
    assert _pubsub_length(_pubsub) == 0


def test_unsubcribtion_hid(_pubsub):
    def handler(event):
        pass

    _pubsub.on(_EventB, handler, hid='hid-1')
    _pubsub.on(_EventB, handler, hid='hid-2')

    _pubsub.off(hid='hid-2')
    assert _pubsub_length(_pubsub) == 1

    _pubsub.off(hid='hid-1')
    assert _pubsub_length(_pubsub) == 0
