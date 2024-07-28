import datetime
import sqlalchemy as sa
from sqlalchemy.sql.elements import and_

from constants import redis_keys, SelectFieldUserType
from drivers.mysql import db
from utils.cache_kits import CacheKlass
from models.m_config import tb_select_field
from utils.strutils import uuid2str, gen_uuid


class SelectHeaderService(CacheKlass):
    _company_list_cache_key = redis_keys.COMPANY_SELECT_HEADER
    _user_list_cache_key = redis_keys.USER_SELECT_HEADER

    @classmethod
    async def get_data_from_db(cls, company_id: str, user_id: str = None) -> list:
        company_id = uuid2str(company_id)
        query = sa.select([
            tb_select_field.c.id.label("id"),
            tb_select_field.c.scene_type.label("scene_type"),
            tb_select_field.c.user_type.label("user_type"),
            tb_select_field.c.fields.label("fields"),
            tb_select_field.c.is_deleted.label("is_deleted"),
            tb_select_field.c.add_by_id.label("add_by_id"),
            tb_select_field.c.add_dt.label("add_dt")
        ]).where(
            and_(
                tb_select_field.c.company_id == company_id,
                tb_select_field.c.is_deleted == 0

            )
        ).order_by(
            tb_select_field.c.update_dt,
            tb_select_field.c.add_dt
        )

        if user_id:
            user_id = uuid2str(user_id)
            query = query.where(
                tb_select_field.c.add_by_id == user_id
            )

        engine = await db.default_db
        async with engine.acquire() as conn:
            ret = await conn.execute(query)
            select_header = await ret.fetchall()

        return [dict(s) for s in select_header]

    @classmethod
    async def get_company_data(cls, company_id: str) -> list:
        return await cls.get_data_from_db(company_id)

    @classmethod
    async def get_user_data(cls, company_id: str, user_id: str) -> list:
        return await cls.get_data_from_db(company_id, user_id)

    @classmethod
    async def update_select_fields(cls, company_id: str, user_id: str, fields_list: list,
                                   scene_type: int, user_type: int = SelectFieldUserType.hr
                                   ) -> None:
        """
        更新表头字段
        :param company_id:
        :param user_id:
        :param fields_list: 字段列表
        :param scene_type: 场景编码
        :param user_type: 用户类型
        :return: list
        """
        if not fields_list:
            return None

        company_id = uuid2str(company_id)
        user_id = uuid2str(user_id)
        sql_exist = sa.select([tb_select_field.c.id]).where(
            and_(
                tb_select_field.c.company_id == company_id,
                tb_select_field.c.add_by_id == user_id,
                tb_select_field.c.scene_type == scene_type,
                tb_select_field.c.user_type == user_type,
                tb_select_field.c.is_deleted == 0
            )
        )

        engine = await db.default_db
        async with engine.acquire() as conn:
            _exist = await conn.execute(sql_exist)

            if _exist.rowcount != 0:
                await conn.execute(
                    sa.update(tb_select_field).where(
                        and_(
                            tb_select_field.c.company_id == company_id,
                            tb_select_field.c.add_by_id == user_id,
                            tb_select_field.c.scene_type == scene_type,
                            tb_select_field.c.user_type == user_type,
                            tb_select_field.c.is_deleted == 0
                        )
                    ).values(
                        fields=','.join(fields_list)
                    )
                )
            else:
                await conn.execute(
                    sa.insert(tb_select_field).values(
                        id=gen_uuid(),
                        company_id=company_id,
                        scene_type=scene_type,
                        user_type=user_type,
                        add_by_id=user_id,
                        fields=','.join(fields_list),
                        add_dt=datetime.datetime.now()
                    )
                )

