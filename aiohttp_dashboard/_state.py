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
from typing import Any, Sequence, Tuple, TypeVar, Dict, List
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
from voluptuous import Optional, Schema, ALLOW_EXTRA
import traceback
import typing

from ._misc import MsgDirection, timestamp
from ._event_emitter import EventEmitter


logger = logging.getLogger(__name__)


DEBUGGER_KEY = __name__
JINJA_KEY = __name__ + '-jinja'

_Documents = List[Dict[Any, Any]]
_Query = Dict[str, Any]

_schema_config = Schema({
    Optional('mongo', default=dict): Schema({
        Optional('port', default=27017): int,
        Optional('host', default='localhost'): str,
        Optional('database', default='aiohttp_dashboard'): str,
    }, extra=ALLOW_EXTRA)
}, extra=ALLOW_EXTRA)


class State:
    """ Contains CRUD API for holding application state and
        dashbooard configuration.
    """

    def __init__(self, config: typing.Optional[dict]):
        self._config: dict = _schema_config(config or {})

        self._motor = AsyncIOMotorClient('mongodb://{}:{}'.format(
            self._config['mongo']['host'],
            self._config['mongo']['port'],
        ))

        self._database = self._motor[self._config['mongo']['database']]
        self._emitter = EventEmitter()

        self._api_status = StatusAPI()
        self._api_request = RequestAPI(self._database, self._emitter)
        self._api_message = MessageAPI(self._database, self._emitter)
        self._api_error = ErrorAPI(self._database, self._emitter)

    @property
    def emitter(self):
        return self._emitter

    @property
    def api_status(self):
        return self._api_status

    @property
    def api_request(self):
        return self._api_request

    @property
    def api_message(self):
        return self._api_message

    @property
    def api_error(self):
        return self._api_error


class StatusAPI:
    def __init__(self):
        self._time = time()

    async def get(self):
        return {
            'timestart': self._time
        }


class RequestAPI:

    def __init__(self, database, emitter):
        self._database = database
        self._emitter = emitter

    async def add(self, request: Request) -> int:
        """Insert new request record into database.
        """

        id_ = id(request)
        peername, _ = request.transport.get_extra_info('peername')

        await self._database.requests.insert_one({
            'id': id_,
            'host': request.host,
            'scheme': request.scheme,
            'method': request.method,
            'path': request.raw_path,
            'peername': peername,
            'headersrequest': dict(request.headers),
            'timestart': timestamp(),
        })

        self._emitter.fire('http.request', {
            'request': id_,
        })

        self._emitter.fire('http', {
            'request': id_,
        })

        return id_

    async def put_response(self, request: Request, response: Response) -> int:
        """Put into existing request terminal data.
        """

        id_ = id(request)

        body = response.text if isinstance(
            response, Response) else None

        await self._database.requests.update_one({'id': id_}, {
            '$set': {
                'status': response.status,
                'reason': response.reason,
                'body': body,
                'timestop': timestamp(),
                'headersresponse': dict(response.headers),
            }
        })

        self._emitter.fire('http.request', {
            'request': id_,
        })

        self._emitter.fire('http', {
            'request': id_,
        })

        return id_

    async def find_one(self, id_) -> Dict[Any, Any]:
        return await self._database.requests.find_one(
            {'id': id_}, projection={'_id': False})

    async def find(self, query: _Query) -> _Documents:
        criteria = {}

        if 'timestart' in query and 'timestop' in query:
            criteria.update({
                'timestart': {
                    '$gte': query['timestart'],
                    '$lte': query['timestop'],
                }
            })

        if 'statuscode' in query:
            criteria.update({
                'status': query['statuscode']
            })

        if 'method' in query:
            criteria.update({
                'method': query['method']
            })

        records = await self._database.requests \
            .find(
                criteria,
                limit=query.get('limit', 100),
                skip=query.get('skip', 0),
                projection={'_id': False}
            ) \
            .sort('timestart', DESCENDING) \
            .to_list(None)

        return records

    async def count(self, query: _Query) -> int:
        criteria = {}

        if 'timestart' in query and 'timestop' in query:
            criteria.update({
                'timestart': {
                    '$gte': query['timestart'],
                    '$lte': query['timestop'],
                }
            })

        if 'statuscode' in query:
            criteria.update({
                'status': query['statuscode']
            })

        return await self._database.requests.count_documents(criteria)


class MessageAPI:
    def __init__(self, database, emitter):
        self._database = database
        self._emitter = emitter

    async def add(self, direction: MsgDirection,
                  request: Request, message: Dict[Any, Any]) -> int:

        await self._database.messages.insert_one({
            'id': id(message),
            'requestid': id(request),
            'direction': direction.name,
            'message': message,
            'time': timestamp(),
        })

    async def find(self, query: _Query) -> _Documents:
        criteria = {}

        if query.get('requestid') is not None:
            criteria.update({
                'requestid': query['requestid']
            })

        if 'timestart' in query and 'timestop' in query:
            criteria.update({
                'time': {
                    '$gte': query['timestart'],
                    '$lte': query['timestop'],
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

    async def count(self):
        ...


class ErrorAPI:
    def __init__(self, database, emitter):
        self._database = database
        self._emitter = emitter

    async def add(self, request: Request, exception: Exception) -> int:
        Error = type(exception)

        await self._database.request_errors.insert_one({
            'id': id(exception),
            'type': Error.__module__ + '.' + Error.__name__,
            'requestid': id(request),
            'time': timestamp(),
            'message': str(exception),
            'traceback': traceback.format_tb(exception.__traceback__),
        })

    async def find_one(self, request_id):
        return await self._database.request_errors \
            .find_one({'requestid': request_id}, projection={'_id': False})
