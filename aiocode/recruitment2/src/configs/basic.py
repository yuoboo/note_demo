# -*- coding: utf-8 -*-
import os

# Project config
PROJECT_NAME = 'eebo.ehr.recruitment2'
PROJECT_ENV_RT_MODE_KEY = "APP_ENV"
PROJECT_ENV_VAR_PREFIX = f'{PROJECT_NAME.upper()}_'
PROJECT_ROOT_PATH = os.path.dirname(os.path.dirname(__file__))

PROJECT_URL_WHITELIST = []

VERSION = '2.12.80'

# Basic config
APP_ENV = "local"
DEBUG = True
AUTO_RELOAD = False
DEFAULT_LOG_LEVEL = 'INFO'

# Basic Serve config
SERVE_HOST = '0.0.0.0'
SERVE_PORT = 8100
SERVE_ACCESS_LOG = True
SERVE_WORKERS = 4
SERVE_REQUEST_MAX_SIZE = 100 * 1024 * 1024
SERVE_REQUEST_TIMEOUT = 60
HTTP_REQUEST_CONCURRENCY_LIMIT = 50

# consul配置信息
CONFIG_FROM_CONSUL = True  # 配置是否从consul拉取
# consul连接配置, CONFIG_FROM_CONSUL 为True时才使用
CONSUL_HOSTS = {
    'local': {'host': 'consul-dev.2haohr.com', 'port': 8500},
    'dev': {'host': 'consul-dev.2haohr.com', 'port': 8500},
    'test': {'host': 'consul-test.2haohr.com', 'port': 8500},
    'production': {'host': 'consul.2haohr.com', 'port': 8500},
}

API_HOSTS = {
    'local': 'https://api-dev.2haohr.com',
    'dev': 'https://api-dev.2haohr.com',
    'test': 'https://api-test.2haohr.com',
    'production': 'https://api.2haohr.com'
}

ADMIN_HOSTS = {
    'local': 'https://admin-dev.2haohr.com',
    'dev': 'https://admin-dev.2haohr.com',
    'test': 'https://admin-test.2haohr.com',
    'production': 'https://admin.2haohr.com'
}

INTRANET_HOSTS = {
    'local': 'http://intranet-dev.2haohr.com',
    'dev': 'http://intranet-dev.2haohr.com',
    'test': 'http://intranet-test.2haohr.com',
    'production': 'http://intranet.2haohr.com'
}

BP_INNER_GATEWAY_HOSTS = {
    'local': 'http://bp-inner-gateway-dev.2haohr.com/bp',
    'dev': 'http://bp-inner-gateway-dev.2haohr.com/bp',
    'test': 'http://bp-inner-gateway-test.2haohr.com/bp',
    'production': 'http://bp-inner-gateway.2haohr.com/bp'
}

WECHAT_HOOK_LOG_URL = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=dc7154d0-17a6-4877-8532-acbc832d626f'
WECHAT_HOOK_SENTRY_URL = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=a1625439-3cc1-4d83-9ed5-99ded3540c03'

if __name__ == '__main__':
    assert SERVE_HOST == '0.0.0.0', 'bad'
    assert SERVE_PORT == 9000, 'bad'
    assert DEBUG, 'bad'
    assert AUTO_RELOAD, 'bad'
    assert SERVE_ACCESS_LOG, 'bad'
    assert SERVE_WORKERS == 1, 'bad'
    assert SERVE_REQUEST_MAX_SIZE == 100 * 1024 * 1024, 'bad'
