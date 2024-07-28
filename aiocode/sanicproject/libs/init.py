# coding: utf-8
from aiomysql.sa import create_engine
import aioredis
from aiocache import caches


async def init_db(config):
    db = await create_engine(
        minsize=config['MYSQL_POOL_MIN_SIZE'],
        maxsize=config['MYSQL_POOL_MIN_SIZE'],
        pool_recycle=3600,
        host=config['MYSQL_HOST'],
        port=config['MYSQL_PORT'],
        user=config['MYSQL_USER'],
        password=config['MYSQL_PASSWORD'],
        db=config['MYSQL_DB'],
        echo=config['DEBUG'],
        charset='utf8mb4',
        connect_timeout=config['MYSQL_TIMEOUT'],
        autocommit=True
    )

    return db


async def close_db(db):
    db.close()
    await db.wait_closed()


async def init_redis(config):
    redis = await aioredis.create_redis_pool(
        config['REDIS_URI'],
        timeout=config['REDIS_TIMEOUT'],
        minsize=config['REDIS_POOL_MIN_SIZE'],
        maxsize=config['REDIS_POOL_MAX_SIZE']
    )

    return redis


async def close_redis(redis):
    redis.close()
    await redis.wait_closed()


def init_cache(config):
    caches.set_config(config['CONFIG_CACHE'])
    return caches.get('default')


async def close_cache(cache):
    await cache.close()
