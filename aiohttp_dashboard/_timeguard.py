from asyncio import get_event_loop


class TimeGuardFactory:
    def __init__(self, timeout):
        self._timeout = timeout

    def __call__(self, function):
        return _TimeGuardHolder(self._timeout, function)


class _TimeGuardHolder:

    def __init__(self, timeout, function):
        self._states = {
            'default': _TimeGuard(timeout, function)
        }
        self._timeout = timeout
        self._function = function

    def __call__(self, *args, **kwargs):
        state = kwargs.pop('_state', 'default')

        if state not in self._states:
            self._states[state] = _TimeGuard(
                self._timeout, self._function)

        return self._states[state](*args, **kwargs)


class _TimeGuard:
    def __init__(self, timeout, function):
        self._timeout = timeout
        self._function = function
        self._last_time = None
        self._waiter_task = None

    def __call__(self, *args, **kwargs):
        if self.ready:
            self._call_soon(args, kwargs)
        else:
            self._call_later(args, kwargs)

    def _call_soon(self, args, kwargs):
        self._last_time = get_event_loop().time()
        self._waiter_task = None

        self._function(*args, **kwargs)

    def _call_later(self, args, kwargs):
        if self._waiter_task:
            self._waiter_task.cancel()

        when_time = self._last_time + self._timeout

        self._waiter_task = get_event_loop().call_at(
            when_time, self._call_soon, args, kwargs)

    def cancel(self):
        if self._waiter_task:
            self._waiter_task.cancel()

    @property
    def ready(self):
        if self._last_time:
            return get_event_loop().time() - self._last_time >= self._timeout

        return True
