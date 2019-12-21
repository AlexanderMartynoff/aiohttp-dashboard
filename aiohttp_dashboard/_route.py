import logging
from typing import Tuple, List
import time
from os.path import join, normpath, isabs, dirname, abspath
from aiohttp_jinja2 import template, web
from aiohttp.web import WebSocketResponse, RouteTableDef, json_response
from voluptuous import Schema, Required, Coerce, Optional, All, ALLOW_EXTRA
from voluptuous.error import CoerceInvalid
from yarl import URL
from pathlib import Path
import traceback


from ._subscriber import Subcriber
from ._state import DEBUGGER_KEY, JINJA_KEY
from ._setup import DEBUGGER_PREFIX_KEY
from ._misc import MsgDirection

logger = logging.getLogger(__name__)


_URL_POSTFIX_EVENT = '/api/event'
_PATH_STATIC = Path(__file__).resolve().parent / 'static'

_int_coerce = Coerce(int)


def _optional_int_coerce(value):
    if value is None:
        return

    return _int_coerce(value)


_subscribe_schema = Schema({
    Required('id'): str,
    Required('endpoint'): str,
    Required('data'): Schema({
        Required('event'): str,
        Optional('conditions', default=dict): Schema({
            Optional('request'): Coerce(int),
        }, extra=ALLOW_EXTRA),
    })
})

_unsubscribe_schema = Schema({
    Required('id'): str,
    Required('endpoint'): str,
    Required('data'): Schema({
        Optional('event'): str,
        Required('id'): str,
    })
})


def _build_event_endpoint(request):
    prefix = request.app[DEBUGGER_PREFIX_KEY]

    return URL.build(
        scheme='wss' if request.secure else 'ws',
        host=request.url.host,
        port=request.url.port,
        path=prefix + _URL_POSTFIX_EVENT,
    )


@template('index.html', app_key=JINJA_KEY)
async def _index(request):
    prefix = request.app[DEBUGGER_PREFIX_KEY]

    return {
        'timestamp': time.time(),
        'prefix': prefix,
        'endpoint': _build_event_endpoint(request),
    }


async def _event(request):
    state = request.app[DEBUGGER_KEY]
    websocket = WebSocketResponse()
    subscriber = Subcriber(websocket, state)

    await websocket.prepare(request)

    try:
        async for message in websocket:
            message_json = message.json()

            try:
                if message_json['endpoint'] == 'subscribe':
                    subscriber.subscribe(_subscribe_schema(message_json))
                elif message_json['endpoint'] == 'unsubscribe':
                    subscriber.unsubscribe(_unsubscribe_schema(message_json))
            except Exception:
                logger.exception('An error occurred while processing the message')
    finally:
        subscriber.cancel()

    return websocket


async def _messages(request):
    state = request.app[DEBUGGER_KEY]
    request_id = _optional_int_coerce(request.query.get('request'))
    start = _optional_int_coerce(request.query.get('start'))
    limit = _optional_int_coerce(request.query.get('limit'))

    return json_response(state.find_messages(
        request_id=request_id,
        slice_start=start,
        slice_limit=limit,
    ))


async def _request_info(request):
    response = {}

    state = request.app[DEBUGGER_KEY]
    request_id = _optional_int_coerce(request.query.get('request', None))
    time_start = _optional_int_coerce(request.query.get('datestart', None))
    time_stop = _optional_int_coerce(request.query.get('datestop', None))

    response.update({
        'websocket': {
            'countincoming': await state.count_messages(
                request_id, MsgDirection.INCOMING, time_start, time_stop),
            'countoutcoming': await state.count_messages(
                request_id, MsgDirection.OUTBOUND, time_start, time_stop),
        }
    })

    return json_response(response)


async def _requests(request):
    state = request.app[DEBUGGER_KEY]
    return json_response(await state.search_requests())


async def _requests_info(request):
    state = request.app[DEBUGGER_KEY]
    time_start = _optional_int_coerce(request.query.get('datestart', None))
    time_stop = _optional_int_coerce(request.query.get('datestop', None))
    requests = state.find_requests(time_start=time_start, time_stop=time_stop)

    return json_response({
        'count': len(requests)
    })


async def _request(request):
    state = request.app[DEBUGGER_KEY]
    request_id = _optional_int_coerce(request.match_info['id'])

    return json_response(state.find_request(request_id))


async def _request_error(request):
    state = request.app[DEBUGGER_KEY]
    request_id = _optional_int_coerce(request.match_info['id'])
    exception = state.find_request_error(request_id)

    if exception is not None:
        return json_response({
            'class': type(exception).__name__,
            'message': str(exception),
            'traceback': traceback.format_tb(exception.__traceback__),
        })

    return json_response()


async def _request_errors(request):
    state = request.app[DEBUGGER_KEY]
    return json_response(state.find_messages())


async def _request_errors_status(request):
    state = request.app[DEBUGGER_KEY]
    return json_response({
        'count': len(state.find_request_errors()),
    })


async def _status(request):
    state = request.app[DEBUGGER_KEY]
    return json_response(state.status())


def build_routes(prefix) -> Tuple[List[Tuple], List[Tuple]]:
    routes = [
        ('GET', prefix, _index),
        ('GET', prefix + '/api/message', _messages),
        ('GET', prefix + '/api/request/message/status', _request_info),
        ('GET', prefix + '/api/request', _requests),
        ('GET', prefix + '/api/request/status', _requests_info),
        ('GET', prefix + '/api/request/{id}', _request),
        ('GET', prefix + '/api/error/request/status', _request_errors_status),
        ('GET', prefix + '/api/error/request', _request_errors),
        ('GET', prefix + '/api/error/request/{id}', _request_error),
        ('GET', prefix + '/api/status', _status),
        ('GET', prefix + _URL_POSTFIX_EVENT, _event),
    ]

    static_routes = [
        (prefix + '/static', _PATH_STATIC)
    ]

    return routes, static_routes


resource_paths = [_PATH_STATIC]
