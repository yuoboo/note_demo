import sys
import os


def get_log_config(config):
    default_level = 'DEBUG' if config['DEBUG'] else 'INFO'
    log_path = os.path.join(config['BASE_DIR'], 'logs')

    return {
        'version': 1,
        'disable_existing_loggers': False,
        'loggers': {
            'sanic.root': {
                'level': config.get('LOGGER_SANIC_ROOT_LEVEL', default_level),
                'handlers': ['console'],
            },
            'sanic.error': {
                'level': config.get('LOGGER_SANIC_ERROR_LEVEL', default_level),
                'handlers': ['error_console'],
                'propagate': True,
                'qualname': 'sanic.error',
            },
            'sanic.access': {
                'level': config.get('LOGGER_SANIC_ACCESS_LEVEL', default_level),
                'handlers': [config.get('LOGGER_SANIC_ACCESS_HANDLER', 'access_console')],
                'propagate': True,
                'qualname': 'sanic.access',
            },
            'app': {
                'level': config.get('LOGGER_APP_LEVEL', default_level),
                'handlers': ['app_file'],
                'propagate': True,
                'qualname': 'app',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'generic',
                'stream': sys.stdout,
            },
            'error_console': {
                'class': 'logging.StreamHandler',
                'formatter': 'generic',
                'stream': sys.stderr,
            },
            'access_console': {
                'class': 'logging.StreamHandler',
                'formatter': 'access',
                'stream': sys.stdout,
            },
            'access_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'access',
                'filename': '{}/access.log'.format(log_path),
                'maxBytes': 50 * 1024 * 1024,
            },
            'app_console': {
                'class': 'logging.StreamHandler',
                'formatter': 'generic',
                'stream': sys.stdout,
            },
            'app_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'generic',
                'filename': '{}/app.log'.format(log_path),
                'maxBytes': 50 * 1024 * 1024,
            },
        },
        'formatters': {
            'generic': {
                'format': '%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
                'datefmt': '[%Y-%m-%d %H:%M:%S %z]',
                'class': 'logging.Formatter',
            },
            'access': {
                'format': '%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
                'datefmt': '[%Y-%m-%d %H:%M:%S %z]',
                'class': 'logging.Formatter',
            },
        },
    }
