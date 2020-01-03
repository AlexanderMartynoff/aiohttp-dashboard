from enum import Enum
from datetime import datetime
from asyncio import ensure_future
from aiohttp.web import Request, Response
from queue import Queue
from collections import deque, defaultdict
from functools import partial
from os.path import join
from inspect import isfunction
from time import time
from typing import Any, Sequence, Tuple, TypeVar, Dict, List, Optional
import logging
from motor.motor_asyncio import AsyncIOMotorClient
import voluptuous

from ._misc import MsgDirection, timestamp
from ._event_emitter import EventEmitter


logger = logging.getLogger(__name__)


DEBUGGER_KEY = __name__
JINJA_KEY = __name__ + '-jinja'


_schema_config = voluptuous.Schema({
    voluptuous.Optional('mongo', default=dict): voluptuous.Schema({
        voluptuous.Optional('port', default=27017): int,
        voluptuous.Optional('host', default='localhost'): str,
        voluptuous.Optional('database', default='aiohttp_dashboard'): str,
    }, extra=voluptuous.ALLOW_EXTRA)
}, extra=voluptuous.ALLOW_EXTRA)


class State:
    """ Summary CRUD API for holding application state.
    """

    def __init__(self, config: Optional[dict]):
        self._config: dict = _schema_config(config or {})

        self._emitter = EventEmitter()
        self._motor = AsyncIOMotorClient('mongodb://{}:{}'.format(
            self._config['mongo']['host'],
            self._config['mongo']['port'],
        ))

        self._database = self._motor[self._config['mongo']['database']]
        self._time = time()

    async def add_request(self, request: Request) -> int:
        id_ = id(request)
        peername, _ = request.transport.get_extra_info('peername')

        await self._database.requests.insert_one({
            'id': id_,
            'host': request.host,
            'scheme': request.scheme,
            'method': request.method,
            'path': request.raw_path,
            'peername': peername,
            'headers_request': dict(request.headers),
            'time_start': timestamp(),
        })

        self._emitter.fire('http.request', {
            'request': id_,
        })

        self._emitter.fire('http', {
            'request': id_,
        })

        return id_

    async def add_response(self, request: Request,
                           response: Response) -> int:
        id_ = id(request)

        body = response.text if isinstance(
            response, Response) else None

        await self._database.requests.update_one({'id': id_}, {
            '$set': {
                'status': response.status,
                'reason': response.reason,
                'body': body,
                'time_stop': timestamp(),
                'headers_response': dict(response.headers),
            }
        })

        self._emitter.fire('http.request', {
            'request': id_,
        })

        self._emitter.fire('http', {
            'request': id_,
        })

        return id_

    async def add_message(self, direction: MsgDirection,
                          request: Request, message: Dict[Any, Any]) -> int:

        await self._database.messages.insert_one({
            'id': id(message),
            'request_id': id(request),
            'direction': direction.name,
            'message': message,
        })

    async def add_request_error(self, request: Request,
                                exception: Exception) -> int:
        ...

    async def add_message_error(self, request: Request,
                                exception: Exception) -> int:
        ...

    async def find_request(self, id_) -> Dict[Any, Any]:
        return await self._database.requests.find_one(
            {'id': id_}, projection={'_id': False})

    async def search_requests(
        self, time_start=None, time_stop=None,
        status_code=None, limit=0, skip=0
    ) -> List[Dict[Any, Any]]:
        query = {}

        if time_start and time_stop:
            query.update({
                'time_start': {
                    '$gte': time_start,
                    '$lte': time_stop,
                }
            })

        if status_code:
            query.update({'status_code': status_code})

        records = await self._database.requests \
            .find(query, limit=limit, skip=skip, projection={'_id': False}) \
            .to_list(None)

        return records

    async def count_requests(self, time_start=None, time_stop=None,
                             status_code=None) -> int:
        query = {}

        if time_start and time_stop:
            query.update({
                'time_start': {
                    '$gte': time_start,
                    '$lte': time_stop,
                }
            })

        if status_code:
            query.update({'status_code': status_code})

        return await self._database.requests.count_documents(query)

    async def search_request_error(self, request_id):
        ...

    async def search_request_errors(self):
        ...

    async def search_messages(self, id_=None, direction=None,
                              time_start=None, time_stop=None,
                              limit=0, skip=0):

        return await self._database.messages \
            .find({}, limit=limit, skip=skip, projection={'_id': False}) \
            .to_list(None)

    async def count_messages(self):
        ...

    async def status(self):
        return {
            'time-start': self._time
        }

    @property
    def emitter(self):
        return self._emitter
