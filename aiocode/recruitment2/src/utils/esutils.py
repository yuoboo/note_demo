# -*- coding: utf-8 -*-
import traceback
import logging

from utils.timeutils import to_datetime


def format_datetime(dt):
    if dt in (None, ''):
        return None

    try:
        new_dt = to_datetime(dt)
        if new_dt:
            return new_dt.isoformat().split('.')[0] + '+08:00'
        return None
    except:
        exc = traceback.format_exc()
        exc = '日期转换错误!!!\n {} \n {}'.format(
            exc, dt
        )
        logging.error(exc)
        try:
            logging.exception(exc)
        except Exception:
            pass
        return None
