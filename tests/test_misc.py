from asyncio import sleep
from aiohttp_dashboard import _misc


def test_is_subset_dict():
    assert _misc.is_subset_dict({}, {'one': 1})
    assert _misc.is_subset_dict({'one': 1}, {'one': 1, 'two': 2})
    assert not _misc.is_subset_dict({'one': 1}, {'one': 2})
    assert not _misc.is_subset_dict({'one': 1}, {'two': 1})
