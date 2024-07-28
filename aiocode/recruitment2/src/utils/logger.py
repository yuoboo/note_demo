# -*- coding:utf-8 -*-

import logging

app_logger = logging.getLogger("sanic.root")
access_logger = logging.getLogger("sanic.access")
error_logger = logging.getLogger("sanic.error")
http_logger = logging.getLogger("sanic.root")      # 这里可以在 init_logging 单独配置一个http formatter
