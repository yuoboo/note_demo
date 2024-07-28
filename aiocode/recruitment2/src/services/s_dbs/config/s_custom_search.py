import datetime

import sqlalchemy as sa
import ujson
from sqlalchemy.sql.elements import and_

from drivers.mysql import db

from models.m_config import tb_custom_search
from utils.strutils import gen_uuid


class CustomSearchService(object):
    """
    自定义筛选条件配置服务
    """

    @classmethod
    async def create_or_update(cls, company_id: str, scene_type: int, user_type: int, add_by_id: str, config: str):
        """
        创建或修改自定义筛选条件配置
        @param company_id: 企业id
        @param scene_type: 场景类型
        @param user_type: 用户类型
        @param add_by_id: 添加人id
        @param config: 配置内容
        @return:
        """
        if not isinstance(config, str):
            config = ujson.dumps(config)

        sql_exist = sa.select([tb_custom_search.c.id]).where(
            and_(
                tb_custom_search.c.company_id == company_id,
                tb_custom_search.c.add_by_id == add_by_id,
                tb_custom_search.c.scene_type == scene_type,
                tb_custom_search.c.user_type == user_type
            )
        )

        engine = await db.default_db
        async with engine.acquire() as conn:
            _exist = await conn.execute(sql_exist)

            if _exist.rowcount != 0:
                await conn.execute(
                    sa.update(tb_custom_search).where(
                        and_(
                            tb_custom_search.c.company_id == company_id,
                            tb_custom_search.c.add_by_id == add_by_id,
                            tb_custom_search.c.scene_type == scene_type,
                            tb_custom_search.c.user_type == user_type
                        )
                    ).values(
                        config=config,
                        update_dt=datetime.datetime.now()
                    )
                )
            else:
                await conn.execute(
                    sa.insert(tb_custom_search).values(
                        id=gen_uuid(),
                        company_id=company_id,
                        scene_type=scene_type,
                        user_type=user_type,
                        add_by_id=add_by_id,
                        config=config,
                        add_dt=datetime.datetime.now()
                    )
                )

    @classmethod
    async def get(cls, company_id: str, scene_type: int, user_type: int, user_id: str) -> dict:
        """
        获取自定义筛选条件配置
        @param company_id: 企业id
        @param scene_type: 场景类型
        @param user_type: 用户类型
        @return:
        """
        query = sa.select([
            tb_custom_search.c.config.label("config")
        ]).where(
            and_(
                tb_custom_search.c.company_id == company_id,
                tb_custom_search.c.scene_type == scene_type,
                tb_custom_search.c.user_type == user_type

            )
        )

        if user_id:
            query = query.where(
                tb_custom_search.c.add_by_id == user_id
            )

        engine = await db.default_db
        async with engine.acquire() as conn:
            ret = await conn.execute(query)
            result = await ret.fetchone()

        return dict(result) if result else {}
