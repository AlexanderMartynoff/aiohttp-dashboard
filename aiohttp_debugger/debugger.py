class Debugger:
    self = None

    @classmethod
    def instance(cls, application):
        if cls.self is None:
            cls.self = cls()
            cls.self._application = application
            cls.self._application.middlewares.append(cls.self)

        return cls.self

    def __init__(self):
        self._application = None
        self._state = self.State()

    async def __call__(self, *args, **kwargs):
        return await self._middleware_factory(*args, **kwargs)

    async def _middleware_factory(self, application, handler):

        async def middleware_handler(request):
            self._handle_request(request)
            print(self._state)
            return await handler(request)
        return middleware_handler

    def _handle_request(self, request):
        self._state.requests.append(request)

    class State:
        def __init__(self):
            self._requests = []

        @property
        def requests(self):
            return self._requests

        def __repr__(self):
            return "%s" % ", ".join(repr(request) for request in self.requests)
