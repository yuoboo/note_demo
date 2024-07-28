# coding: utf-8
import logging
from aiohttp import ClientSession, hdrs

logger = logging.getLogger('app')


class Client:
    def __init__(self, app, **kwargs):
        self._client = ClientSession(loop=app.loop)
        logger.info('client: {}'.format(self._client))

    def _request(self, method, url, **kwargs):
        res = self._client.request(method, url, **kwargs)
        return res

    def get(self, url, allow_redirects=True, **kwargs):
        return self._request(hdrs.METH_GET, url, allow_redirects=allow_redirects, **kwargs)

    def post(self, url, data=None, **kwargs):
        return self._request(hdrs.METH_POST, url, data=data, **kwargs)

    def put(self, url, data=None, **kwargs):
        return self._request(hdrs.METH_PUT, url, data=data, **kwargs)

    def delete(self, url, **kwargs):
        return self._request(hdrs.METH_DELETE, url, **kwargs)

    def head(self, url, allow_redirects=False, **kwargs):
        return self._request(hdrs.METH_HEAD, url, allow_redirects=allow_redirects, **kwargs)

    def options(self, url, allow_redirects=True, **kwargs):
        return self._request(hdrs.METH_OPTIONS, url, allow_redirects=allow_redirects, **kwargs)

    def close(self):
        self._client.close()
