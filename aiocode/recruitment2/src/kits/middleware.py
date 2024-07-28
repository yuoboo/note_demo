# -*- coding: utf-8 -*-
import aiotask_context
from sanic import Sanic

from error_code import Code
from kits.exception import ServiceError

# METHODS: GET / POST / HEAD / OPTIONS / PUT / PATCH / DELETE / TRACE / CONNECT
ACCESS_METHODS = ('GET', "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH", "TRACE", "CONNECT")


async def request_hijack_middleware(request):
    if request.method not in ACCESS_METHODS:
        raise ServiceError(Code.METHODNOTSUPPORT)


async def init_app_context(request):
    aiotask_context.set('app', request.app)
    aiotask_context.set('accesstoken', request.headers.get('accesstoken', ''))
    aiotask_context.set('x-platform', str(request.headers.get('x-platform', '')).upper())


async def request_middleware(request):
    await request_hijack_middleware(request)
    await init_app_context(request)


async def response_middleware(request, response):
    ...
