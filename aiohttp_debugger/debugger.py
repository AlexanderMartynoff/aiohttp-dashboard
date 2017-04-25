from datetime import datetime
from asyncio import ensure_future
from aiohttp.web import WebSocketResponse
from .helper import PubSubSupport
from .helper import LimitedDict
from queue import Queue
from collections import deque, defaultdict
import os
import sys
from enum import Enum
import ruamel
import aiohttp_jinja2
import jinja2
import inspect


class Debugger(PubSubSupport):
    instance = None

    @classmethod
    def setup(cls, application):
        from . import action

        if cls.instance is None:

            cls.instance = cls(application, action.routes, action.static_routes)
            aiohttp_jinja2.setup(
                application,
                loader=jinja2.FileSystemLoader(f"{action.debugger_dir}/static"))
        return cls.instance

    def __init__(self, application, routes, static_routes):
        self._application = self._configure_application(
            application, routes, static_routes)

        self._state = State(application)
        self._api = Api(self._state)

    async def __call__(self, *args, **kwargs):
        return await self._middleware_factory(*args, **kwargs)

    def _configure_application(self, application, routes, static_routes):
        self._add_middlewares(application)
        self._add_routes(application, routes)
        self._add_static_routes(application, static_routes)
        application.on_response_prepare.append(self._on_response_prepare)
        return application

    def _add_middlewares(self, application):
        application.middlewares.append(self)

    def _add_static_routes(self, application, static_routes):
        for url, path in static_routes:
            application.router.add_static(url, path)

    def _add_routes(self, application, routes):
        for method, path, handler in routes:
            application.router.add_route(method, path, handler)

    async def _middleware_factory(self, application, handler):

        async def middleware_handler(request):
            if self._is_sutable_req(request):
                self._handle_request(request)
            return await handler(request)
        return middleware_handler

    async def _on_response_prepare(self, request, response):
        if self._is_sutable_req(request):
            rid = id(request)
            if rid in self._state.requests.keys():
                self._state.requests[rid].update(
                    donetime=self._state.now,
                    done=True,
                    resheaders=dict(response.headers),
                    status=response.status,
                    reason=response.reason)

            self.fire(HttpResponse(id(request)))

            if isinstance(response, WebSocketResponse):
                self._ws_resposne_do_monkey_patching(request, response)

    def _is_sutable_req(self, req):
        return not req.path.startswith("/_debugger")

    def _ws_resposne_do_monkey_patching(self, request, response):

        def ping_overload(data):
            """ for catch outbound message """

            self._handle_ws_msg(
                MsgDirection.INCOMING,
                request, data, self._out_msg_mapper, WsMsgOutbound())
            return response.__aiohttp_debugger_ping__(data)

        response.__aiohttp_debugger_ping__ = response.ping
        response.pong = ping_overload

        def pong_overload(data):
            """ for catch outbound message """

            self._handle_ws_msg(
                MsgDirection.INCOMING,
                request, data, self._out_msg_mapper, WsMsgOutbound())
            return response.__aiohttp_debugger_pong__(data)

        response.__aiohttp_debugger_pong__ = response.pong
        response.pong = pong_overload

        def send_str_overload(data):
            """ for catch outbound message """

            self._handle_ws_msg(
                MsgDirection.INCOMING,
                request, data, self._out_msg_mapper, WsMsgOutbound())
            return response.__aiohttp_debugger_send_str__(data)

        response.__aiohttp_debugger_send_str__ = response.send_str
        response.send_str = send_str_overload

        def send_bytes_overload(data):
            """ for catch outbound message """

            self._handle_ws_msg(
                MsgDirection.INCOMING,
                request, data, self._out_msg_mapper, WsMsgOutbound())
            return response.__aiohttp_debugger_send_str__(data)

        response.__aiohttp_debugger_send_bytes__ = response.send_bytes
        response.send_bytes = send_bytes_overload

        # outbound
        async def receive_overload():
            """ for catch incoming message """

            msg = await response.__aiohttp_debugger_receive__()
            self._handle_ws_msg(
                MsgDirection.OUTBOUND,
                request, msg, self._in_msg_mapper, WsMsgIncoming())
            return msg

        response.__aiohttp_debugger_receive__ = response.receive
        response.receive = receive_overload

        return response

    def _in_msg_mapper(self, msg):
        return msg.data

    def _out_msg_mapper(self, msg):
        return msg

    def _handle_ws_msg(self, direction, req, msg, msg_mapper, event):
        # refact this and move to Debugger._State class

        if self._is_sutable_req(req):
            rid, mid = id(req), id(msg)
            event.rid = rid

            self._state.put_ws_message(rid, dict(
                id=mid,
                msg=msg_mapper(msg),
                time=self._state.now,
                direction=direction
            ))

            self.fire(event)

    def _handle_request(self, request):
        self._state.put_request(request)
        self.fire(HttpRequest(id(request)))

    @property
    def api(self):
        return self._api


class Api:
    """ Facade API for `Debugger` """

    def __init__(self, state):
        self._state = state

    def platform_info(self):
        import platform
        import sys
        import aiohttp
        from . import __version__

        return dict(
            platform=platform.platform(),
            python=sys.version,
            aiohttp=aiohttp.__version__,
            debugger=__version__
        )

    def requests(self, *args, **kwargs):
        return list(self._state.requests.values())

    def request(self, rid):
        record = next((request for request in self.requests()
                       if request['id'] == rid), None)

        return record

    def messages(self, rid, page=1, perpage=-1):

        if rid not in self._state.messages:
            return None

        messages = list(self._state.messages[rid])

        if perpage == -1:
            return messages

        start = (page - 1) * perpage
        end = start + perpage

        return messages[start:end]

    def count_by_direction(self, rid, direction=None):
        if direction is None:
            return self._state.incoming_msg_counter[rid] + \
                self._state.outbound_msg_counter[rid]
        elif direction is MsgDirection.OUTBOUND:
            return self._state.outbound_msg_counter[rid]
        elif MsgDirection.INCOMING:
            return self._state.incoming_msg_counter[rid]
        else:
            return None

    def routes(self):

        routes = []
        for route in self._state.application.router.routes():
            # todo: parse this struct - route.get_info().items()

            routes += dict(
                name=route.name,
                method=route.method,
                handler=route.handler.__name__,
                source=inspect.getsource(route.handler)),

        return routes


class State:
    def __init__(self, application, maxlen=50_000):
        self._application = application
        self._maxlen = maxlen
        self._requests = LimitedDict(maxlen=self._maxlen)
        self._messages = LimitedDict(maxlen=self._maxlen)
        self._incoming_msg_counter = defaultdict(lambda: 0)
        self._outbound_msg_counter = defaultdict(lambda: 0)

    def put_request(self, request):
        rid = id(request)
        ip, _ = request.transport.get_extra_info('peername')
        self._requests[rid] = dict(
            id=rid,
            scheme=request.scheme,
            host=request.host,
            path=request.raw_path,
            method=request.method,
            begintime=self.now,
            done=False,
            reqheaders=dict(request.headers),
            ip=ip
        )

    def put_ws_message(self, rid, message):
        """
        :param req: request id
        """
        if rid not in self._messages:
            self._messages[rid] = deque(maxlen=self._maxlen)

        self._messages[rid] += message,

        if self._outbound_msg_counter[rid] + self._incoming_msg_counter[rid] >= self._maxlen:
            return

        if message['direction'] is MsgDirection.OUTBOUND:
            self._outbound_msg_counter[rid] += 1
        else:
            self._incoming_msg_counter[rid] += 1

    @property
    def outbound_msg_counter(self):
        return self._outbound_msg_counter

    @property
    def incoming_msg_counter(self):
        return self._incoming_msg_counter

    @property
    def now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")

    @property
    def requests(self) -> dict:
        return self._requests

    @property
    def messages(self) -> LimitedDict:
        return self._messages

    @property
    def application(self):
        return self._application


class MsgDirection(Enum):
    OUTBOUND = 1
    INCOMING = 2


class DebuggerAbstractWebEvent(PubSubSupport.Event):
    # request id
    _rid = None

    def __init__(self, rid=None):
        self._rid = rid

    @property
    def rid(self):
        return self._rid

    @rid.setter
    def rid(self, rid):
        self._rid = rid


class DebuggerAbstractReqResEvent(DebuggerAbstractWebEvent):
    def __init__(self, rid):
        self.rid = rid


class HttpRequest(DebuggerAbstractReqResEvent):
    def __init__(self, rid):
        super().__init__(rid)


class HttpResponse(DebuggerAbstractWebEvent):
    def __init__(self, rid):
        super().__init__(rid)


class WsMsgIncoming(DebuggerAbstractWebEvent):
    ...


class WsMsgOutbound(DebuggerAbstractWebEvent):
    ...
