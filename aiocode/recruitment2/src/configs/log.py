# coding=utf-8
import datetime
import logging
import sys

import pytz

from configs import config

log_level = config.DEFAULT_LOG_LEVEL or 'INFO'


class CustomDateFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        tz = pytz.timezone('Asia/Shanghai')
        ct = datetime.datetime.fromtimestamp(record.created, tz=tz)
        return ct.isoformat()


def init_logging():
    logging.Formatter = CustomDateFormatter
    log_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'loggers': {
            "sanic.root": {
                "level": log_level,
                "handlers": ["console"]
            },
            "sanic.error": {
                "level": log_level,
                "handlers": ["error_console"],
                "propagate": True,
                "qualname": "sanic.error",
            },
            "sanic.access": {
                "level": log_level,
                "handlers": ["access_console"],
                "propagate": True,
                "qualname": "sanic.access",
            },
            'aiomysql': {
                'level': log_level,
                'handlers': ['console'],
                "propagate": True,
                "qualname": "aiomysql",
            },
            "celery.task": {
                'level': log_level,
                'handlers': ['console'],
                "propagate": True,
                "qualname": "celery.task",
            },
            "celery.worker": {
                'level': log_level,
                'handlers': ['console'],
                "propagate": True,
                "qualname": "celery.worker",
            }
        },
        'handlers': {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "generic",
                "stream": sys.stdout,
            },
            "error_console": {
                "class": "logging.StreamHandler",
                "formatter": "generic",
                "stream": sys.stderr,
            },
            "access_console": {
                "class": "logging.StreamHandler",
                "formatter": "access",
                "stream": sys.stdout,
            },
        },
        'formatters': {
            "generic": {
                "format": "[%(asctime)s (%(process)d) (%(levelname)s) %(message)s]",
                "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
                "class": "logging.Formatter",
                # "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            },
            "access": {
                "format": "[%(asctime)s - (%(name)s) (%(levelname)s)(%(host)s): "
                          + "%(request)s %(message)s %(status)d %(byte)d]",
                "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
                # "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "class": "logging.Formatter",
            },
        },
    }
    logging.config.dictConfig(log_config)
