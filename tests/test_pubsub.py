from asyncio import sleep
from aiohttp_dashboard._pubsub import PubSub
import pytest


def _pubsub_length(pubsub):
    return len(pubsub._handlers)


@pytest.fixture
def _pubsub():
    return PubSub()


def test_subcribtion_single_event_count(_pubsub):
    events = []

    def handler(event, parameters):
        events.append(event)

    _pubsub.on('a', handler)

    _pubsub.fire('a', None)
    _pubsub.fire('a', None)

    assert len(events) == 2


def test_subcribtion_multiple_event_count(_pubsub):
    events = []

    def handler(event, parameters):
        events.append(event)

    _pubsub.on(['a', 'b'], handler)

    _pubsub.fire('a', None)
    _pubsub.fire('b', None)

    assert len(events) == 2


def test_subcribtion_event_equals(_pubsub):
    fired_event = None
    event = 'a'

    def handler(event, parameters):
        nonlocal fired_event
        fired_event = event

    _pubsub.on('a', handler)
    _pubsub.fire(event, None)

    assert fired_event is event


def test_subcribtion_handler_count(_pubsub):
    def handler(event, parameters):
        pass

    _pubsub.on('a', handler)
    _pubsub.on('b', handler)

    assert _pubsub_length(_pubsub) == 2


def test_unsubcribtion_family(_pubsub):

    def handler(event, parameters):
        pass

    _pubsub.on('a', handler, family='1')
    _pubsub.on('b', handler, family='1')

    assert _pubsub_length(_pubsub) == 2

    _pubsub.off(family='1')
    assert _pubsub_length(_pubsub) == 0


def test_unsubcribtion_name(_pubsub):

    def handler(event, parameters):
        pass

    _pubsub.on('a', handler, '1')
    _pubsub.on('b', handler, '2')

    _pubsub.off(name='1')
    assert _pubsub_length(_pubsub) == 1

    _pubsub.off(name='2')
    assert _pubsub_length(_pubsub) == 0


def test_unsubcribtion_default_name(_pubsub):
    def handler(event, parameters):
        pass

    _pubsub.on('a', handler)
    _pubsub.on('b', handler)

    _pubsub.off(name='default')

    assert _pubsub_length(_pubsub) == 0


def test_parameters(_pubsub):
    parameters_ = {}

    def handler(event, parameters):
        assert parameters_ is parameters

    _pubsub.on('a', handler)
    _pubsub.fire('a', parameters_)
