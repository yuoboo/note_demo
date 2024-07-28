# -*- coding: utf-8 -*-
import traceback
from sanic.response import HTTPResponse
from sanic.exceptions import NotFound, MethodNotSupported
from utils.json_util import json_dumps
from error_code import Code
from .exception import Error


def customer_exception_handler(request, exception):
    if isinstance(exception, Error):
        resultcode = exception.code
        errormsg = str(exception.msg)
        status = exception.status_code

    elif isinstance(exception, NotFound):
        resultcode, errormsg = Code.NOTFOUND
        status = resultcode

    elif isinstance(exception, MethodNotSupported):
        resultcode, errormsg = Code.METHODNOTSUPPORT
        status = resultcode

    else:
        resultcode, errormsg = Code.SYSTEM_ERROR.value
        status = resultcode

    exc_data = None
    if request and request.app.config.DEBUG:
        # errormsg = errormsg + ', err: {}'.format(str(exception))
        traceback.print_exc()
        exc_data = traceback.format_exc()

    body = {
        'result': False,
        'resultcode': resultcode,
        'resultfrom': request.app.config.PROJECT_NAME,
        'msg': '',
        'errormsg': errormsg,
        'data': exc_data,
    }
    return HTTPResponse(
        json_dumps(body),
        headers=None,
        content_type="application/json; charset=utf-8",
        status=status,
    )


# def customer_exception_handler(request, exception):
#     if isinstance(exception, ServiceException):
#         data = {
#             'result': False,
#             'resultcode': exception.code,
#             'msg': '',
#             'errormsg': str(exception.msg),
#             'data': {},
#         }
#         return response.json(data, status=200)
#     else:
#         errormsg = Code.SYSTEM_ERROR.msg
#         exc_data = None
#
#         if request and config.DEBUG:
#             errormsg = errormsg + ', err: {}'.format(str(exception))
#             traceback.print_exc()
#             exc_data = traceback.format_exc()
#
#         data = {
#             'result': False,
#             'errormsg': errormsg,
#             'resultcode': Code.SYSTEM_ERROR.code,
#             'data': exc_data,
#         }
#         return response.json(data, status=Code.SYSTEM_ERROR.code)


# async def not_found_error_handler(request, exception):
#     data = {
#         'result': False,
#         'msg': Code.NOTFOUND.msg,
#         'errormsg': str(Code.NOTFOUND.msg) + f': {request.path}',
#         'resultcode': Code.NOTFOUND.code,
#         'data': None,
#     }
#     return response.json(data, status=200)
#
#
# async def api_validation_error_handler(request, exception):
#     data = {
#         'result': False,
#         'msg': exception.message,
#         'errormsg': exception.message,
#         'resultcode': exception.code,
#         'data': exception.data,
#     }
#     return response.json(data, status=200)
#
#
# async def method_not_supported_handler(request, exception):
#     data = {
#         'result': False,
#         'msg': '',
#         'errormsg': str(exception),
#         'resultcode': 405,
#         'data': None,
#     }
#     return response.json(data, status=405)
