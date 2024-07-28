# -*- coding: utf-8 -*-
import os

import sentry_sdk
from sanic import Sanic
from sentry_sdk.integrations.sanic import SanicIntegration

from apps.employee_apis.routes import add_employee_routes
from apps.hr_apis.routes import add_api_routes
from apps.int_apis.routes import add_intranet_routes
from apps.public.routes import add_public_routes
from configs import config
from configs.log import init_logging
from drivers.consul import DynamicConfigFromConsul
from kits.error_handler import customer_exception_handler
from kits.listener import setup_serve, teardown_serve
from kits.middleware import request_middleware, response_middleware


APP_ENV = config.APP_ENV


def _register_delay_tasks(app):
    if APP_ENV != 'local':
        consul_basic_config = config.CONSUL_HOSTS.get(APP_ENV, {})
        consul_config = DynamicConfigFromConsul(**consul_basic_config, namespace=config.PROJECT_NAME)
        app.add_task(consul_config.update_config(config, app.config, app.loop))


def _register_middlewares(app):
    app.register_middleware(request_middleware, 'request')
    app.register_middleware(response_middleware, 'response')


def _register_listeners(app):
    app.register_listener(setup_serve, 'before_server_start')
    app.register_listener(teardown_serve, 'before_server_stop')


def _register_error_handler(app):
    # app.error_handler.add(APIValidationError, api_validation_error_handler)
    # app.error_handler.add(NotFound, not_found_error_handler)
    # app.error_handler.add(MethodNotSupported, method_not_supported_handler)
    app.error_handler.add(Exception, customer_exception_handler)


def _register_routes(app):
    add_api_routes(app)
    add_employee_routes(app)
    add_intranet_routes(app)
    add_public_routes(app)


def create_app():
    app = Sanic(config.PROJECT_NAME)
    init_logging()

    app.config.update(config)

    app.env_mode = os.getenv(config.PROJECT_ENV_RT_MODE_KEY, 'dev')

    @app.listener('before_server_start')
    def before(_app, _loop):
        _register_delay_tasks(_app)

    _register_error_handler(app)
    _register_listeners(app)
    _register_middlewares(app)
    _register_routes(app)

    if app.config.get('SENTRY_DSN'):
        sentry_sdk.init(
            dsn=app.config['SENTRY_DSN'],
            integrations=[SanicIntegration()],
            environment=app.config['APP_ENV'],
            release="{}@{}".format(app.config['PROJECT_NAME'], app.config['VERSION']),
        )

    return app
