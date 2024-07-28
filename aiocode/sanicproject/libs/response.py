# coding: utf-8
from sanic import response
import logging
from .code import Code

logger = logging.getLogger('app')


def do_response(resultcode=Code.SUCCESS, data=None, user_msg='', errormsg='', status=200):
    """
    异常信息返回
    :param resultcode: 错误码
    :param data: 数据，异常情况下，一般数据为空
    :param user_msg: 提示信息
    :param errormsg: 错误信息
    :param status: http status
    :return: json 格式化之后的数据
    """

    result = True if resultcode == Code.SUCCESS else False

    code, msg = resultcode

    res = {
        "result": result,
        "resultcode": code,
        "msg": user_msg if user_msg else msg,
        "errormsg": errormsg,
        "data": data if data else {},
    }

    return response.json(res, status=status)
