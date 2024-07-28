# coding=utf-8
from sanic import Sanic

from apps.employee_apis.routes import add_employee_routes
from apps.hr_apis.routes import add_api_routes
from apps.int_apis.routes import add_intranet_routes
from apps.public.routes import add_public_routes


def register_app_routes(app: Sanic):
    add_api_routes(app)
    add_employee_routes(app)
    add_intranet_routes(app)
    add_public_routes(app)


__all__ = ['register_app_routes']
