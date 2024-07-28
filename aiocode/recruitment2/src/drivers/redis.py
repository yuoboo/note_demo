# -*- coding: utf-8 -*-

import asyncio
from functools import lru_cache

import aioredis
from cached_property import cached_property

from configs import config


@lru_cache(maxsize=2000)
def redis_get_conf(name: str) -> dict:
    """ get config by env name
    :param name: default/
    :return: dict
    """
    conf = config.REDIS_CONFIG[name]
    return dict(
        address=(conf["host"], conf["port"] or 6379),
        maxsize=conf["pool_max_size"],
        minsize=conf["pool_min_size"],
        timeout=conf["timeout"],
        password=conf["password"],
        db=conf["db_index"],
        encoding=conf["encoding"]
    )


class RedisCache:

    def __init__(self):
        self.common = None
        self.default = None

    @cached_property
    async def common_redis(self) -> aioredis.ConnectionsPool:
        pool = await aioredis.create_redis_pool(**redis_get_conf("common"))
        return pool

    @cached_property
    async def default_redis(self) -> aioredis.ConnectionsPool:
        pool = await aioredis.create_redis_pool(**redis_get_conf("default"))
        return pool

    async def init_redis_cache(self):
        self.common = await self.common_redis
        self.default = await self.default_redis

    async def close_redis_cache(self):
        self.common.close()
        await self.common.wait_closed()

        self.default.close()
        await self.default.wait_closed()


redis_db = RedisCache()

__all__ = ['redis_db']

if __name__ == '__main__':

    async def _helper():
        cli = await redis_db.common_redis
        res = await cli.get('4d8107f8967b4d078cae9edc3afddfe3_corp_news_related_emps')
        print(222, res)

    asyncio.run(_helper())
