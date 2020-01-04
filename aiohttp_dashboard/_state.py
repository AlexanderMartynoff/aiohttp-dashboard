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
from pymongo import ASCENDING, DESCENDING
import voluptuous
import traceback


from ._misc import MsgDirection, timestamp
from ._event_emitter import EventEmitter


logger = logging.getLogger(__name__)


DEBUGGER_KEY = __name__
JINJA_KEY = __name__ + '-jinja'

_Documents = List[Dict[Any, Any]]
_Query = Dict[str, Any]

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
            'time': timestamp(),
        })

    async def add_message_error(self, request: Request,
                                exception: Exception) -> int:
        ...

    async def find_request(self, id_) -> Dict[Any, Any]:
        return await self._database.requests.find_one(
            {'id': id_}, projection={'_id': False})

    async def search_requests(self, query: _Query) -> _Documents:
        criteria = {}

        if 'time_start' in query and 'time_stop' in query:
            criteria.update({
                'time_start': {
                    '$gte': query['time_start'],
                    '$lte': query['time_stop'],
                }
            })

        if 'status_code' in query:
            criteria.update({
                'status_code': query['status_code']
            })

        records = await self._database.requests \
            .find(
                criteria,
                limit=query.get('limit', 100),
                skip=query.get('skip', 0),
                projection={'_id': False}
            ) \
            .sort('time_start', DESCENDING) \
            .to_list(None)

        return records

    async def count_requests(self, query: _Query) -> int:
        criteria = {}

        if 'time_start' in query and 'time_stop' in query:
            criteria.update({
                'time_start': {
                    '$gte': query['time_start'],
                    '$lte': query['time_stop'],
                }
            })

        if 'status_code' in query:
            criteria.update({
                'status_code': query['status_code']
            })

        return await self._database.requests.count_documents(criteria)

    async def add_request_error(self, request: Request,
                                exception: Exception) -> int:
        ErrorType = type(exception)

        await self._database.request_errors.insert_one({
            'id': id(exception),
            'type': ErrorType.__module__ + '.' + ErrorType.__name__,
            'request_id': id(request),
            'time': timestamp(),
            'message': str(exception),
            'traceback': traceback.format_tb(exception.__traceback__),
        })

    async def find_request_error(self, request_id):
        return await self._database.request_errors \
            .find_one({'request_id': request_id}, projection={'_id': False})

    async def search_messages(self, query: _Query) -> _Documents:
        criteria = {}

        if query.get('request_id') is not None:
            criteria.update({
                'request_id': query['request_id']
            })

        if 'time_start' in query and 'time_stop' in query:
            criteria.update({
                'time': {
                    '$gte': query['time_start'],
                    '$lte': query['time_stop'],
                }
            })

        records = await self._database.messages \
            .find(
                criteria,
                limit=query.get('limit', 100),
                skip=query.get('skip', 0),
                projection={'_id': False}
            ) \
            .sort('time', DESCENDING) \
            .to_list(None)

        return records

    async def count_messages(self):
        ...

    async def status(self):
        return {
            'time-start': self._time
        }

    @property
    def emitter(self):
        return self._emitter


class RequestAPI:
    ...


class MessageAPI:
    ...


class ErrorAPI:
    ...
