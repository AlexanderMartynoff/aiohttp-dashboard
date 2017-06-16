from .debugger import Debugger, WsMsgIncoming, WsMsgOutbound, HttpRequest, HttpResponse, MsgDirection
from .helper import casemethod
from operator import itemgetter
from asyncio import sleep, ensure_future, get_event_loop
from time import time
from collections import defaultdict
import warnings
import ujson
import logging
import concurrent.futures
from collections import namedtuple


log = logging.getLogger("aiohttp_debugger.debugger")


class WsMsgDispatcherProxy:
    """ Passing websocket meessage
        into target method for processing.
    """
    
    def __init__(self, dispatcher, sender):
        self._dispatcher = dispatcher
        self._sender = sender

    def recive(self, inmsg):
        self._sender.on_soon(inmsg, self._dispatcher.recive(inmsg))

    def close(self):
        return self._dispatcher.close()


class WsMsgDispatcher:
    """ Endpoints for websocket message processing.
        For more info see `.helper.casemethod`.
        For more info about `rid = inmsg.body.id @ int` see `helper.WsResponseHelper`
    """

    @casemethod
    def recive(inmsg):
        return inmsg.endpoint

    def __init__(self, sender):
        self._debugger_api = DebuggerApi()
        self._debugger = Debugger.instance
        self._sender = sender

    @recive.case('sibsribe.request')
    def recive(self, inmsg):
        rid = inmsg.body.id >> int

        def handler(event):
            if event.rid == rid: self._sender.on(inmsg)

        self._debugger.on(HttpRequest, handler, group=self._sender.id, hid=inmsg.uid)
        self._debugger.on(HttpResponse, handler, group=self._sender.id, hid=inmsg.uid)

        return self._debugger_api.request(rid)

    @recive.case('sibsribe.request.messages')
    def recive(self, inmsg):
        rid = inmsg.body.id >> int
        page = inmsg.body.page >> int
        perpage = inmsg.body.perpage >> int

        def handler(event: (WsMsgIncoming, WsMsgOutbound)):
            if event.rid == rid:
                self._sender.on(inmsg)

        self._debugger.on(WsMsgIncoming, handler, group=self._sender.id, hid=inmsg.uid)
        self._debugger.on(WsMsgOutbound, handler, group=self._sender.id, hid=inmsg.uid)

        return self._debugger_api.messages(rid, page, perpage)

    @recive.case('sibsribe.requests')
    def recive(self, inmsg):
        
        def handler(event):
            self._sender.on(inmsg)

        self._debugger.on(HttpRequest, handler, group=self._sender.id, hid=inmsg.uid)
        self._debugger.on(HttpResponse, handler, group=self._sender.id, hid=inmsg.uid)

        return self._debugger_api.requests()

    @recive.case('unsibscribe')
    def recive(self, inmsg):
        """ with this `hid` probably exist multiple handlers """
        self._debugger.off(hid=inmsg.body.id.raw)

    @recive.case('fetch.info')
    def recive(self, inmsg):
        return self._debugger_api.platform_info()

    @recive.case('fetch.routes')
    def recive(self, inmsg):
        return self._debugger.api.routes()

    @recive.default
    def recive(self, inmsg):
        return {'status': 'endpoint not found'}

    @recive.catch(Exception)
    def recive(self, exception, inmsg):
        self._sender.on_soon(inmsg, {
            'status': 'error',
            'cause': str(exception)
        })

    def close(self):
        self._debugger.off(group=self._sender.id)

# TODO: rename this maybe to `Gateway`?
class Sender:
    """ Use for deferred sending websocket message """

    def __init__(self, socket, debugger_api):
        self._socket = socket
        self._debugapi = debugger_api
        self._endpoints = defaultdict(lambda: None)

    @casemethod
    def _handler(inmsg):
        """ For handle debugger state change. """
        return inmsg.endpoint

    @_handler.case('sibsribe.request')
    def _handler(self, inmsg):
        self._send(self._debugapi.request(inmsg.body.id >> int), inmsg)

    @_handler.case('sibsribe.request.messages')
    def _handler(self, inmsg):
        rid = inmsg.body.id >> int
        page = inmsg.body.page >> int
        perpage = inmsg.body.perpage >> int
        self._send(self._debugapi.messages(rid, page, perpage), inmsg)

    @_handler.case('sibsribe.requests')
    def _handler(self, inmsg):
        self._send(self._debugapi.requests(), inmsg)

    def newtoken(self):
        return self._Token(handler=self._handler)

    def on_soon(self, inmsg, out):
        token = self._endpoints[inmsg.endpoint]

        if token is None:
            token = self._endpoints[inmsg.endpoint] = self.newtoken()

        token.handle_soon_with_handler(inmsg, out, self._send)

    def on(self, inmsg):
        """ :inmsg: incoming websocket message
        """

        token = self._endpoints[inmsg.endpoint]

        if token is None:
            token = self._endpoints[inmsg.endpoint] = self.newtoken()
            token.handle_soon(inmsg)
        elif token.isready:
            token.handle_soon(inmsg)
        else:
            token.handle_later(inmsg)

    def _send(self, out, inmsg):
        try:
            self._socket.send_json(self._prepare_ws_response(out, inmsg), dumps=ujson.dumps)
        except RuntimeError as error:
            log.error(f"an error while send data to debugger client: {error}")

    def _prepare_ws_response(self, out, inmsg):
        return dict(data=out, uid=inmsg.uid, endpoint=inmsg.endpoint)

    @property
    def id(self):
        return self._socket.id

    class _Token:
        _delay = 2
        _handler = None
        _last_send_time = None
        _handler_wait_for_send = None

        def __init__(self, handler):
            self._handler = handler
            self._last_send_time = get_event_loop().time()

        def _handler_caller(self, inmsg):
            self._handler(inmsg)
            self._handler_wait_for_send = None
            self._last_send_time = get_event_loop().time()

        def handle_soon_with_handler(self, inmsg, out, handler):
            handler(out, inmsg)

        def handle_soon(self, inmsg):
            self._handler_caller(inmsg)

        def handle_later(self, inmsg):

            if self._handler_wait_for_send:
                self._handler_wait_for_send.cancel()

            self._handler_wait_for_send = self._do_send_later(inmsg)

        def _do_send_later(self, inmsg):
            return get_event_loop().call_at(
                self._last_send_time + self._delay, lambda: self._handler_caller(inmsg))

        @property
        def isready(self):
            return (get_event_loop().time() - self._last_send_time) >= self._delay


class DebuggerApi:
    """ Presentation layer for WEB.
    """
    
    def __init__(self):
        self._debugger = Debugger.instance

    def request(self, rid):
        return dict(item=self._debugger.api.request(rid))

    def requests(self):
        return self._debugger.api.requests()

    def messages(self, rid, page, perpage):
        return dict(
            collection=self._debugger.api.messages(rid, page, perpage),
            total=self._debugger.api.count_by_direction(rid),
            incoming=self._debugger.api.count_by_direction(rid, MsgDirection.INCOMING),
            outbound=self._debugger.api.count_by_direction(rid, MsgDirection.OUTBOUND)
        )

    def unsibscribe(self, hid):
        return self._debugger.off(hid=hid)

    def platform_info(self):
        return self._debugger.api.platform_info()

    def routes(self):
        return self._debugger.api.routes()
