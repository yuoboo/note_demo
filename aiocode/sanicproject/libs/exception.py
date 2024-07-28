import traceback
from sanic.exceptions import SanicException
from services import ServiceException
from .code import Code
from .response import do_response


def customer_exception_handler(request, e):
    code, msg = Code.SYSTEM_ERROR
    message = msg
    status = 500

    if isinstance(e, SanicException):
        status = e.status_code
    elif isinstance(e, ServiceException):
        if request and request.app.config['DEBUG']:
            message = message + e.message
        if e.code:
            code = e.code
        status = 200

    data = {}
    errormsg = ''
    if request and request.app.config['DEBUG']:
        message = message + ' : {}'.format(str(e))
        errormsg = message
        traceback.print_exc()
        data['exception'] = traceback.format_exc()

    resultcode = code, message
    return do_response(resultcode=resultcode, data=data, errormsg=errormsg, status=status)
