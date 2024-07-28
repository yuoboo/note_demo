# -*- coding: utf-8 -*-
from sanic.response import json, HTTPResponse
from sanic.server import HttpProtocol


class CustomHttpResponseProtocol(HttpProtocol):

    def write_response(self, response):
        if not isinstance(response, HTTPResponse):
            response = json({
                "result": True,
                "resultcode": 200,
                "msg": '',
                "errormsg": '',
                "data": response if response else {},
            }, status=200)

        self.transport.write(
            response.output(self.request.version)
        )
        self.transport.close()


__all__ = [
    'CustomHttpResponseProtocol',
]
