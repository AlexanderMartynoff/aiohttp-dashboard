import asyncio
from aiohttp_dashboard._timeguard import TimeGuardFactory


async def test_passed_args():
    timeguard = TimeGuardFactory(10)
    a, b = 1, 2
    a_, b_ = None, None

    @timeguard
    def function(a, b):
        nonlocal a_, b_
        a_, b_ = a, b

    function(a, b=b)

    assert a is a_ and b is b_


# NOTE: split on few cases
async def test_calls_count():
    timeguard = TimeGuardFactory(.1)
    count = 0

    @timeguard
    def function():
        nonlocal count
        count = count + 1

    # first call
    function()

    # second call
    # must called just one time
    for _ in range(5):
        function()

    assert count == 1

    await asyncio.sleep(.05)
    assert count == 1

    await asyncio.sleep(.05)
    assert count == 2

    function()
    # check without sleep
    assert count == 2

    await asyncio.sleep(.1)
    assert count == 3
