from asyncio import sleep
from aiohttp_dashboard import _misc


def test_is_subset_dict():
    assert _misc.is_subset_dict({}, {'one': 1})
    assert _misc.is_subset_dict({'one': 1}, {'one': 1, 'two': 2})
    assert not _misc.is_subset_dict({'one': 1}, {'one': 2})
    assert not _misc.is_subset_dict({'one': 1}, {'two': 1})


def test_dictqueue_default():
    dictqueue = _misc.QueueDict(5, dict)

    assert dictqueue[0] == {}
    dictqueue[0][0] = 0
    assert dictqueue[0] == {0: 0}


def test_dictqueue_maxsize():
    dictqueue = _misc.QueueDict(3, dict)

    for number in range(10):
        dictqueue[number] = number

    assert len(dictqueue) == 3

    assert dictqueue[9] == 9
    assert dictqueue[8] == 8
    assert dictqueue[7] == 7


def test_dictqueue_kwargs_maxlen():
    dictqueue = _misc.QueueDict(
        maxlen=5,
        default=dict,
        key1='value1',
        key2='value2',
    )

    assert len(dictqueue) == 2

    assert dictqueue['key1'] == 'value1'
    assert dictqueue['key2'] == 'value2'
