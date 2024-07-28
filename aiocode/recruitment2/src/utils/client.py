# -*- coding: utf-8 -*-
import asyncio
import logging
import traceback

import aiohttp
import async_timeout
import ujson

from configs.basic import SERVE_REQUEST_TIMEOUT

logger = logging.getLogger('app')

"""
    http client:
    usage example:
    ```
        data = await http_client('http://www.baidu.com', response_type='text')
    ```
"""

SERVE_RETRY_MAX = 0


async def http_client(
        url, data=None, method='GET', headers=None, json=None, timeout=SERVE_REQUEST_TIMEOUT,
        response_type='json', params=None, max_retry: int = SERVE_RETRY_MAX
):
    request_headers = headers if headers else {}

    with async_timeout.timeout(timeout):
        async with aiohttp.ClientSession(
                headers=request_headers,
                connector=aiohttp.TCPConnector(verify_ssl=False)
        ) as session:
            response = await fetch(session, url, data, method, json, response_type, params=params, max_retry=max_retry)
            return response


async def fetch(session, url, data=None, method='GET', json=None, response_type='json', params=None,
                max_retry: int = SERVE_RETRY_MAX):
    if not params:
        params = dict()
    ret = {}
    try:
        async with session.request(method, url, data=data, json=json, params=params) as response:
            msg = f'REQUEST: {method}, URL: {url}, JSON: {json}, PARAMS:{params}'
            logger.info(msg)
            if response_type == 'json':
                _ret = await response.text()
                # try:
                #     ret = ujson.loads(ret)
                # except ValueError:
                #     logging.error('解析json失败')
                #     return dict()
                ret = ujson.loads(_ret)
            elif response_type == 'text':
                ret = await response.text()
            else:
                ret = await response.content.read()
    except Exception:
        err = traceback.format_exc()
        logger.error('http fetch data error: url:{}, data: {}, json: {}, method: {}, err: {}'.format(
            method, url, data, json, str(err)
        ))

        if max_retry > 1 and isinstance(max_retry, int):
            max_retry -= 1
            return await fetch(session, url, data, method, json, response_type, params, max_retry=max_retry)

    return ret


async def http_client_multi_get(urls, headers=None, timeout=SERVE_REQUEST_TIMEOUT, response_type='json'):
    """
    http get 异步并发请求(暂时只处理get的请求，其余的方式后续再扩展)
    """
    request_headers = headers if headers else {}
    with async_timeout.timeout(timeout):
        async with aiohttp.ClientSession(headers=request_headers) as session:
            tasks = [fetch(session, url, method='GET', response_type=response_type) for url in urls]

            responses = await asyncio.gather(*tasks, return_exceptions=True)

            return responses


class HttpClient:
    @classmethod
    async def get(cls, url, params=None, headers=None, timeout=SERVE_REQUEST_TIMEOUT, max_retry=SERVE_RETRY_MAX):
        return await http_client(url, method='GET', headers=headers, params=params, timeout=timeout, max_retry=max_retry)

    @classmethod
    async def post(cls, url, json_body=None, data=None, timeout=SERVE_REQUEST_TIMEOUT, headers=None, max_retry=SERVE_RETRY_MAX):
        if json_body:
            return await http_client(url, method='POST', json=json_body, timeout=timeout, headers=headers, max_retry=max_retry)
        elif data:
            return await http_client(url, method='POST', data=data, timeout=timeout, headers=headers, max_retry=max_retry)

    @classmethod
    async def put(cls, url, json_body=None, timeout=SERVE_REQUEST_TIMEOUT, headers=None):
        if not json_body:
            json_body = dict()
        return await http_client(url, method='PUT', json=json_body, timeout=timeout, headers=headers)

    @classmethod
    async def patch(cls, url, json_body=None, timeout=SERVE_REQUEST_TIMEOUT, headers=None):
        if not json_body:
            json_body = dict()
        return await http_client(url, method='PATCH', json=json_body, timeout=timeout, headers=headers)

    @classmethod
    async def delete(cls, url, json_body=None, timeout=SERVE_REQUEST_TIMEOUT, headers=None):
        if not json_body:
            json_body = dict()
        return await http_client(url, method='DELETE', json=json_body, timeout=timeout, headers=headers)

    @classmethod
    async def fetch_binary(cls, url, method='GET', json_body=None, timeout=60):
        if method == 'GET':
            return await http_client(url, method=method, response_type='b', timeout=timeout)
        else:
            return await http_client(url, method=method, response_type='b', json=json_body or dict(), timeout=timeout)
