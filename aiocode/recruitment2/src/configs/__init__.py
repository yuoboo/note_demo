# -*- coding: utf-8 -*-
import os

import ujson
from sanic.config import Config

from . import basic

# 加载基础配置

config = Config(load_env=False)
config.from_object(basic)

# 运行环境变量
env_mode = os.getenv("APP_ENV", 'local')

if env_mode == 'local':
    # 配置从本地文件加载
    local_json_path = os.path.join(config.PROJECT_ROOT_PATH, 'configs/local.json')
    with open(local_json_path) as f:
        obj = ujson.loads(f.read())
        config.update(obj)
else:
    # 配置从consul加载
    from drivers.consul import DynamicConfigFromConsul

    init_consul_config = DynamicConfigFromConsul(**config.CONSUL_HOSTS[env_mode], namespace=config.PROJECT_NAME)
    # 拉取consul配置更新本地的basic配置
    init_consul_config.init_config(config)
