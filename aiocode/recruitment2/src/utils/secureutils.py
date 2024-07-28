# -*- coding: utf-8 -*-
import logging

from configs import config
from utils import rc4


SYMMETRICAL_SECRET_KEY = config.get('SYMMETRICAL_SECRET_KEY') or "it's a secrect"


def user_encode(s):
    """
    用户敏感信息加密
    :param s:
    :return:返回加密后的字符串
    """
    try:
        v = rc4.encode_symmetrical(s, SYMMETRICAL_SECRET_KEY)
        return v
    except:
        logging.error('用户信息加密失败', exc_info=True)
    return s


def user_decode(s):
    """
    用户敏感信息解密
    :param s:
    :return:返回解密后的字符串
    """
    try:
        v = rc4.decode_symmetrical(s, SYMMETRICAL_SECRET_KEY)
        return v
    except:
        logging.error('用户信息解密失败', exc_info=True)
    return s


if __name__ == '__main__':
    print(user_decode('fff8faf9f9fdfaf2f2fffefefef2fafdfe'))
    print(type(user_encode('')))
    print(user_decode('adf3adaeada9ada8adf2adf3adaaadf9adf8adf8ada9adf3adf2adaeada9ada9adf2f2f8'))
