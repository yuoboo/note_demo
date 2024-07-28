# -*- coding: utf-8 -*-
import os
import time
from urllib.parse import urlencode

from configs import config as app_config
from utils.client import http_client
from utils.logger import app_logger
from error_code import Code
from kits.exception import APIValidationError

env_mode = os.getenv(app_config.PROJECT_ENV_RT_MODE_KEY, 'dev')


class _InnerRequest(object):

    def __init__(self, service, path, host_type):
        self.service = service
        self.path = path
        self.host_name = self._get_host(host_type)

    @staticmethod
    def _get_host(host_type):

        if host_type == 'api':
            api_hosts = app_config.API_HOSTS
        elif host_type == 'intranet':
            api_hosts = app_config.INTRANET_HOSTS
        elif host_type == 'bp_inner_gateway':
            api_hosts = app_config.BP_INNER_GATEWAY_HOSTS
        else:
            raise APIValidationError(Code.NOTFOUND)

        host_name = api_hosts.get(env_mode, '')
        return host_name

    async def get(self, data=None, headers=None):
        return await self._request(data=data, method='GET', headers=headers)

    async def post(self, data=None, headers=None):
        return await self._request(json=data, method='POST', headers=headers)

    def _get_url(self, data=None, method='GET'):

        host = self.host_name
        url = '%s/%s/%s/' % (host, self.service, self.path)

        if method == 'GET':
            if isinstance(data, (dict, tuple,)):
                url = url + '?' + urlencode(data)

        return url

    async def _request(self, data=None, json=None, method='GET', headers=None):
        # 构造url
        """
        @return is_success,code,data
        """
        self.url = self._get_url(data, method)

        try:
            start_time = time.time()
            http_resp_data = await http_client(self.url, params=data, json=json, method=method, headers=headers)
            req_time = time.time() - start_time
            app_logger.info(f'[ehr request] [e_time: {req_time}] url: {self.url} '
                            f'method: {method} data: {data} json: {json} return: {http_resp_data}')
            return http_resp_data
        except Exception as e:
            app_logger.error(f'request data error: {method} {self.url} {str(e)}')
            return None


class EhrRequest(object):
    def __init__(self, service_name: str):
        self.service_name = service_name

    def api(self, path):
        return _InnerRequest(self.service_name, path, 'api')

    def intranet(self, path):
        return _InnerRequest(self.service_name, path, 'intranet')

    def bp_inner_gateway(self, path):
        return _InnerRequest(self.service_name, path, 'bp_inner_gateway')

