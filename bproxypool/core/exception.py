import json

from flask import request
from werkzeug.exceptions import HTTPException


class APIException(HTTPException):
    code = 500  # 通用错误响应
    msg = 'sorry, server make a mistake'
    errno = -1
    data = None

    def __init__(self, code=None, msg=None, errno=None, data=None):
        if code:
            self.code = code
        if msg:
            self.msg = msg
        if errno:
            self.errno = errno
        self.data = data
        super().__init__(description=self.msg)

    def get_body(self, environ=None):
        req_uri = '{} {}'.format(request.method, str(request.full_path).split('?')[0])
        body = {
            'msg': self.msg,
            'errno': self.errno,
            'request': req_uri,
        }
        if self.data is not None:
            body['data'] = self.data
        return json.dumps(body)

    def get_headers(self, environ=None):
        return [("Content-Type", "application/json")]


class ClientTypeError(APIException):
    code = 400  # 参数错误
    msg = 'client is invalid'
    errno = 10001


class NotFound(APIException):
    code = 404
    msg = 'not found'
    errno = 101


class ParameterException(APIException):
    code = 400
    msg = 'invalid parameter'
    errno = 100


class AuthFailed(APIException):
    code = 401
    msg = 'Unauthorized'
    errno = 10001


class Forbidden(APIException):
    code = 403
    msg = 'forbidden, op failed'
    errno = 10004


class PreconditionFailed(APIException):
    code = 412
    msg = 'Precondition Failed'
    errno = 102


class Conflict(APIException):
    """操作异常"""
    code = 409
    msg = 'conflict'
    errno = 103

class ProxyGetterError(Exception):
    pass
