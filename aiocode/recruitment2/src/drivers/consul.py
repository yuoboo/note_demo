# -*- coding: utf-8 -*-
import asyncio
import json

from consul import Consul as SyncConsul
from consul.aio import Consul as AioConsul

from utils.logger import app_logger


class DynamicConfigFromConsul(object):

    def __init__(self, host, port, namespace, app_type='data'):
        self.host = host
        self.port = port
        self.namespace_path = 'configs/%s' % namespace
        self.app_type = app_type
        self.consul = None
        self.sync_consul = SyncConsul(host=self.host, port=self.port)

    def init_config(self, config):
        index = 0
        index, data = self.sync_consul.kv.get(self.namespace_path, index=index, wait='1s', recurse=True)

        if bool(data):
            consul_config_data = self.loads_configs(data)
            app_logger.info("consul:config:data{}".format(consul_config_data))
            consul_config = consul_config_data.get(self.app_type.upper(), {})

            config.update(consul_config)

    async def update_config(self, config: dict, app_config: dict, loop):

        if self.consul is None:
            self.consul = AioConsul(host=self.host, port=self.port, loop=loop)

        index = None
        while True:
            try:
                index, data = await self.consul.kv.get(self.namespace_path, index=index, wait='3s', recurse=True)

                if bool(data):
                    consul_config_data = self.loads_configs(data)
                    consul_config = consul_config_data.get(self.app_type.upper(), {})

                    config.update(consul_config)
                    app_config.update(consul_config)

            except asyncio.TimeoutError:
                pass

            await asyncio.sleep(30)

    @staticmethod
    def parse_config(row):
        conf_key = row.get('Key')
        conf_value = row.get("Value")
        conf_index = row.get('CreateIndex')

        # app_logger.info(f"pull conf, sub-namespace={conf_key}, index={conf_index}")
        if not conf_value:
            return None, None

        key = conf_key.split('/')[-1].upper()
        try:
            conf = json.loads(conf_value)
        except ValueError:
            conf = None
        # app_logger.info(f'conf pull done, sub-namespace={conf_key}, index={conf_index}')
        return key, conf

    def loads_configs(self, rows):
        configs = {}
        for row in rows:
            key, conf = self.parse_config(row)
            if key:
                configs[key] = conf
        return configs
