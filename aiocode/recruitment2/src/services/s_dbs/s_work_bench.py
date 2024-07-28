
import sqlalchemy as sa
import ujson
from sqlalchemy.sql import and_

from drivers.mysql import db
from drivers.redis import redis_db
from constants import redis_keys
from models.m_job_position import tb_job_position
from utils.sa_db import db_executor


class WorkBenchService(object):

    @classmethod
    async def get_last_position_ids(cls, company_id: str, user_id: str) -> dict:
        """
        从缓存拉取最近职位数据
        :return: {"position_id": 时间戳}
        """
        _redis = await redis_db.common_redis
        hash_key = redis_keys.LAST_POSITION_IDS[0].format(
            company_id=company_id, user_id=user_id
        )

        return await _redis.hgetall(hash_key)

    @classmethod
    async def set_cache_for_bench_api(cls, cache_key: str, data, expire: int):
        """
        工作台缓存接口缓存
        :param cache_key:
        :param expire:
        :param data:
        :return:
        """
        _redis = await redis_db.default_redis
        json_data = ujson.dumps(data)
        await _redis.set(cache_key, json_data, expire=expire)

    @classmethod
    async def get_cache_for_bench_api(cls, cache_key: str):
        """
        获取工作台缓存接口
        :param cache_key:
        """
        _redis = await redis_db.default_redis
        cache = await _redis.get(cache_key)
        if cache:
            return ujson.loads(cache)
        return None

    @classmethod
    async def get_last_position_list(cls, company_id: str, ids: list) -> list:
        """
        根据职位ids 返回最近职位信息

        """
        query = sa.select([
            tb_job_position.c.id.label("id"),
            tb_job_position.c.name.label("name"),
            tb_job_position.c.dep_id.label("dep_id"),
            tb_job_position.c.dep_name.label("dep_name"),
            tb_job_position.c.position_total.label("position_total"),
            tb_job_position.c.status.label("status"),
            tb_job_position.c.secret_position.label("secret_position")
        ]).where(
            and_(
                tb_job_position.c.is_delete == 0,
                tb_job_position.c.company_id == company_id,
                tb_job_position.c.id.in_(ids)
            )
        )
        # position_total 招聘人数 None 表示无，0表示不限
        engine = await db.default_db
        data = await db_executor.fetch_all_data(engine=engine, stmt=query)
        return [dict(d) for d in data]

