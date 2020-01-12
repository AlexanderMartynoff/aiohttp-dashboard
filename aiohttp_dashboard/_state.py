from aiohttp.web import Request, Response
from time import time
from typing import Any, Dict, List
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
from voluptuous import Optional, Schema, ALLOW_EXTRA
import traceback
import typing
import uuid

from ._misc import MsgDirection, timestamp
from ._event_emitter import EventEmitter


logger = logging.getLogger(__name__)


DEBUGGER_KEY = __name__
JINJA_KEY = __name__ + '-jinja'

_Document = Dict[Any, Any]
_Documents = List[_Document]
_Query = Dict[str, Any]

_schema_config = Schema({
    Optional('mongo', default=dict): Schema({
        Optional('port', default=27017): int,
        Optional('host', default='localhost'): str,
        Optional('database', default='aiohttp_dashboard'): str,
    }, extra=ALLOW_EXTRA)
}, extra=ALLOW_EXTRA)


def _id() -> str:
    """ Used for generate id for documents.
    """
    return uuid.uuid4().hex


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

        # create uniq indexes for collections
        self._database.requests.create_index([
            ('id', DESCENDING)
        ], unique=True)
        self._database.messages.create_index([
            ('id', DESCENDING)
        ], unique=True)

        self._emitter = EventEmitter()
        self._api_status = _StatusAPI()
        self._api_request = _RequestAPI(self._database, self._emitter)
        self._api_message = _MessageAPI(self._database, self._emitter)
        self._api_error = _ErrorAPI(self._database, self._emitter)

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


class _StatusAPI:
    def __init__(self):
        self._time = time()

    async def get(self):
        """ Return current
        in the first approximation status. """
        return {
            'timestart': self._time
        }


class _RequestAPI:

    def __init__(self, database, emitter):
        self._database = database
        self._emitter = emitter

    async def add(self, request: Request) -> str:
        """ Insert new request record into database.
        """

        id_ = _id()
        host, port = request.transport.get_extra_info('peername')

        await self._database.requests.insert_one({
            'id': id_,
            'host': request.host,
            'scheme': request.scheme,
            'method': request.method,
            'path': request.raw_path,
            'peername': '{}:{}'.format(host, port),
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

    async def put_response(self, id_, request: Request,
                           response: Response) -> None:
        """ Put into existing request terminal data.
        """

        body = response.text if isinstance(
            response, Response) else None

        await self._database.requests.update_one({'id': id_}, {
            '$set': {
                'status': str(response.status),  # for search by re
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

    async def find_one(self, id_) -> _Document:
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
                'status': {
                    '$regex': '^{}$'.format(query['statuscode']),
                }
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


class _MessageAPI:
    def __init__(self, database, emitter):
        self._database = database
        self._emitter = emitter

    async def add(self, request_id, direction: MsgDirection,
                  request: Request, message: str) -> str:
        message_id = _id()

        await self._database.messages.insert_one({
            'id': message_id,
            'requestid': request_id,
            'direction': direction.name,
            'message': message,  # save always as a string
            'time': timestamp(),
        })

        self._emitter.fire('websocket', {
            'requestid': request_id,
            'messageid': message_id,
        })

        return message_id

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

        if 'content' in query:
            criteria.update({
                'message': {
                    '$regex': '.*{}.*'.format(query['content'])
                }
            })

        if 'direction' in query:
            criteria.update({
                'direction': query['direction']
            })

        records = await self._database.messages \
            .find(
                criteria,
                limit=query.get('limit', 100),
                skip=query.get('skip', 0),
                projection={'_id': False}
            ) \
            .sort('time', criteria.get('sort', DESCENDING)) \
            .to_list(None)

        return records

    async def count(self):
        ...


class _ErrorAPI:
    def __init__(self, database, emitter):
        self._database = database
        self._emitter = emitter

    async def add(self, request_id,
                  request: Request, exception: Exception) -> str:
        id_ = _id()
        Error = type(exception)

        await self._database.request_errors.insert_one({
            'id': id_,
            'type': Error.__module__ + '.' + Error.__name__,
            'requestid': request_id,
            'time': timestamp(),
            'message': str(exception),
            'traceback': traceback.format_tb(exception.__traceback__),
        })

        return id_

    async def find_one(self, request_id) -> _Document:
        return await self._database.request_errors \
            .find_one({'requestid': request_id}, projection={'_id': False})
