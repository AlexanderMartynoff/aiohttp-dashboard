from __future__ import annotations

from tortoise.models import Model
from tortoise import fields


class Request(Model):
    id = fields.IntField(pk=True)
    scheme = fields.TextField()
    host = fields.TextField()
    method = fields.TextField()
    path = fields.TextField()
    time_start = fields.IntField()
    time_stop = fields.IntField()
    status = fields.TextField()
    reason = fields.TextField()
    peername = fields.TextField()
    body = fields.TextField()
    headers_request = fields.JSONField()
    headers_response = fields.JSONField()
    messages: fields.ReverseRelation[Message]
    errors: fields.ReverseRelation[RequestError]


class RequestError(Model):
    request: fields.ForeignKeyRelation[Request] = \
        fields.ForeignKeyField('debugger.Request', related_name='errors')


class Message(Model):
    request: fields.ForeignKeyRelation[Request] = \
        fields.ForeignKeyField('debugger.Request', related_name='messages')
    errors: fields.ReverseRelation[MessageError]


class MessageError(Model):
    message: fields.ForeignKeyRelation[Message] = \
        fields.ForeignKeyField('debugger.Request', related_name='errors')
