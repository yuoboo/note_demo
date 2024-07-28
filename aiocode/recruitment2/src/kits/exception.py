
from error_code import Code


__all__ = [
    'Error',
    'APIValidationError',
    'AuthenticationFailed',
    'ParamsError',
    'FeedBack',
    'ServiceError',
    'UpstreamError'
]


class Error(Exception):
    """异常错误基础类"""
    msg = None
    code = None
    status_code = 500

    def __init__(self, code_enum: Code, msg: str):
        _code, _msg = code_enum.value
        self.code = _code
        self.msg = msg if msg else _msg

    def __str__(self):
        return f"{self.__class__.__name__}: {self.code}, {self.msg}"


class APIValidationError(Error):
    """
    API 基础验证异常
    """
    status_code = 400

    def __init__(self, code_enum: Code = Code.SYSTEM_ERROR, msg: str = ""):
        super().__init__(code_enum=code_enum, msg=msg)


class AuthenticationFailed(Error):
    """用户认证失败"""
    status_code = 401

    def __init__(self, code_enum: Code = Code.UNAUTHORIZED, msg: str = ""):
        super().__init__(code_enum=code_enum, msg=msg)


class ParamsError(Error):
    """参数错误"""
    status_code = 400

    def __init__(self, code_enum: Code = Code.PARAM_ERROR, msg: str = ""):
        super().__init__(code_enum=code_enum, msg=msg)


class FeedBack(Error):
    """错误反馈提示"""
    status_code = 200

    def __init__(self, code_enum: Code = Code.FEEDBACK, msg: str = ""):
        super().__init__(code_enum=code_enum, msg=msg)


class ServiceError(Error):
    """服务内部错误"""
    status_code = 500

    def __init__(self, code_enum: Code = Code.SYSTEM_ERROR, msg: str = ""):
        super().__init__(code_enum=code_enum, msg=msg)


class UpstreamError(Error):
    """上游服务错误"""
    status_code = 500

    def __init__(self, code_enum: Code = Code.SYSTEM_ERROR, msg: str = ""):
        super().__init__(code_enum=code_enum, msg=msg)


# class APIValidationError(Exception):
#     """
#     API 基础验证异常
#     """
#     status_code = 400
#     errors = {}
#
#     def __init__(self, code, status_code=None, data=None, msg=None):
#         self.code = code
#         self.data = data
#         self.message = self.errors.get(code) if not msg else msg
#         if status_code is not None:
#             self.status_code = status_code
#         super(APIValidationError, self).__init__(self.message)


class ServiceException(Exception):
    """
    项目基础异常， 临时使用
    """
    status_code = 400
    msg = ''
    errors = {}

    def __init__(self, code=500, status_code=None, data=None, msg=None):
        self.code = code
        self.data = data
        self.msg = self.errors.get(code) if not msg else msg
        if status_code is not None:
            self.status_code = status_code
        else:
            self.status_code = code

        super(ServiceException, self).__init__(self.msg)

