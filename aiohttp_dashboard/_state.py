from datetime import datetime
from asyncio import ensure_future
from aiohttp.web import WebSocketResponse, Response
from queue import Queue
from collections import deque, defaultdict
from functools import partial
from os.path import join
from inspect import isfunction
from time import time
from typing import Any, Sequence, Tuple, TypeVar, Dict
import logging
from tortoise import QuerySet


from ._misc import MsgDirection, QueueDict, timestamp
from ._event_emitter import EventEmitter
from ._model import Request, RequestError, Message


logger = logging.getLogger(__name__)


_T = TypeVar('T')

_QueryResult_T = Dict[str, Any]
_QueryResultCount_T = Tuple[_QueryResult_T, int]


DEBUGGER_KEY = __name__
JINJA_KEY = __name__ + '-jinja'


class State:

    def __init__(self):
        self._time_start = time()
        self._emitter = EventEmitter()

    async def add_request(self, request):
        id_ = id(request)
        peername, _ = request.transport.get_extra_info('peername')

        return await Request.create(
            id=id_,
            host=request.host,
            scheme=request.scheme,
            method=request.method,
            path=request.raw_path,
            peername=peername,
            headers_request=dict(request.headers),
            time_start=timestamp()
        )

    async def add_response(self, request, response):
        id_ = id(request)

        body = response.text if isinstance(
            response, Response) else None

        await Request.filter(id=id_).update(
            status=response.status,
            reason=response.reason,
            body=body,
            headers_response=dict(response.headers),
        )

    async def get_request(self, id_):
        await Request.get(id=id_)

    async def search_requests(self, time_start=None,
                              time_stop=None, status_code=None,
                              offset=None, limit=None) -> _QueryResultCount_T:
        query = Request.filter()

        if time_start and time_stop:
            query = Request.filter(
                time_start__gte=time_start,
                time_stop__lte=time_stop,
            )

        if status_code:
            query = query.filter(status_code=status_code)

        count = await query.count()

        if limit:
            query = query.limit(limit)

        if offset:
            query = query.offset(offset)

        return await query.values(), count

    async def count_requests(self, time_start=None,
                             time_stop=None, status_code=None) -> int:
        query = Request.filter()

        if time_start and time_stop:
            query = Request.filter(
                time_start__gte=time_start,
                time_stop__lte=time_stop,
            )

        if status_code:
            query = query.filter(status_code=status_code)

        return await query.count()

    async def add_request_error(self, request, exception):
        raise NotImplementedError()

    async def search_request_error(self, request_id):
        raise NotImplementedError()

    async def search_request_errors(self):
        raise NotImplementedError()

    async def add_message(self, direction, request, message):
        raise NotImplementedError()

    async def search_messages(self, id_=None, direction=None,
                              time_start=None, time_stop=None,
                              slice_start=None, slice_limit=None):
        raise NotImplementedError()

    async def count_messages(self):
        raise NotImplementedError()

    async def status(self):
        return {
            'time-start': self._time_start
        }

    @property
    def emitter(self):
        return self._emitter
