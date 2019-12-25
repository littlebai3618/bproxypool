from .exception import APIException


class Success(APIException):
    code = 200
    msg = 'ok!'
    errno = 0


class GetSuccess(Success):
    pass


class PostSuccess(Success):
    code = 201


class PutSuccess(Success):
    pass


class PatchSuccess(Success):
    pass


class DeleteSuccess(Success):
    code = 204

class PartialSuccess(Success):
    code = 206
