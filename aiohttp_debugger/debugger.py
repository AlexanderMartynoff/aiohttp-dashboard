from datetime import datetime


class Debugger:
    self = None

    @classmethod
    def instance(cls, application):
        from . import action

        if cls.self is None:
            cls.self = cls(application, action.routes)

        return cls.self

    def __init__(self, application, routes):
        self._application = self._configure_application(application, routes)
        self._state = self._State()
        self._api = self._Api(self._state)

    async def __call__(self, *args, **kwargs):
        return await self._middleware_factory(*args, **kwargs)

    def _configure_application(self, application, routes):
        self._add_middlewares(application)
        self._add_routes(application, routes)
        application.on_response_prepare.append(self._on_response_prepare)
        return application

    def _add_middlewares(self, application):
        application.middlewares.append(self)

    def _add_routes(self, application, routes):
        for method, path, handler in routes:
            application.router.add_route(method, path, handler)

    async def _middleware_factory(self, application, handler):

        async def middleware_handler(request):
            self._handle_request(request)
            return await handler(request)
        return middleware_handler

    async def _on_response_prepare(self, request, response):
        rid = id(request)
        if rid in self._state.requests.keys():
            self._state.requests[rid].update(
                donetime=self._state.now,
                done=True
            )

    def _handle_request(self, request):
        self._state.put_request(request)

    @property
    def api(self):
        return self._api

    class _Api:

        def __init__(self, state):
            self._state = state

        @property
        def requests(self):
            return list(self._state.requests.values())

    class _State:

        def __init__(self):
            self._requests = dict()

        def put_request(self, request):
            id, record = self._make_request_log(request)
            self.requests[id] = record

        def _make_request_log(self, request) -> (int, dict):
            return id(request), dict(
                scheme=request.scheme,
                host=request.host,
                path=request.raw_path,
                method=request.method,
                begintime=self.now,
                done=False
            )

        @property
        def now(self):
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")

        @property
        def requests(self):
            return self._requests
