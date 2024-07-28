import datetime

import sqlalchemy as sa
from sqlalchemy import select, and_

from drivers.mysql import db
from models.m_wework import tb_wework_external_contact, tb_wework_external_contact_way, tb_wework_external_contact_data
from utils.sa_db import db_executor
from utils.table_util import TableUtil

external_contact_tbu = TableUtil(tb_wework_external_contact)
external_contact_data_tbu = TableUtil(tb_wework_external_contact_data)


class WeWorkService(object):
    @classmethod
    async def get_by_external_id(cls, company_id: str, external_id: str, fields: list = None) -> dict:
        """
        根据外部联系人id， 获取第一条符合条件的数据
        @param company_id:
        @param external_id:
        @return:
        """
        query_keys = external_contact_tbu.filter_keys(fields)
        exp = select(
            [tb_wework_external_contact.c[key].label(key) for key in query_keys]
        ).where(
            and_(
                tb_wework_external_contact.c.company_id == company_id,
                tb_wework_external_contact.c.external_id == external_id,
                tb_wework_external_contact.c.is_delete == 0
            )
        )
        engine = await db.default_db
        return await db_executor.fetch_one_data(engine, exp)

    @classmethod
    async def get_by_candidate_id(cls, company_id: str, candidate_id: str, fields: list = None) -> dict:
        """
        根据外部联系人id， 获取第一条符合条件的数据
        @param company_id:
        @param candidate_id:
        @return:
        """
        query_keys = external_contact_tbu.filter_keys(fields)
        exp = select(
            [tb_wework_external_contact.c[key].label(key) for key in query_keys]
        ).where(
            and_(
                tb_wework_external_contact.c.company_id == company_id,
                tb_wework_external_contact.c.candidate_id == candidate_id,
                tb_wework_external_contact.c.is_delete == 0
            )
        )
        engine = await db.default_db
        return await db_executor.fetch_one_data(engine, exp)

    @classmethod
    async def get_data_by_wework_external_contact_id(cls, company_id: str, wework_external_contact_id: str, fields: list = None) -> dict:
        """
        根据外部联系人id， 获取第一条符合条件的数据
        @param company_id:
        @param wework_external_contact_id:
        @return:
        """
        query_keys = external_contact_data_tbu.filter_keys(fields)
        exp = select(
            [tb_wework_external_contact_data.c[key].label(key) for key in query_keys]
        ).where(
            and_(
                tb_wework_external_contact_data.c.company_id == company_id,
                tb_wework_external_contact_data.c.wework_external_contact_id == wework_external_contact_id,
                tb_wework_external_contact_data.c.is_delete == 0
            )
        )
        engine = await db.default_db
        return await db_executor.fetch_one_data(engine, exp)

    @classmethod
    async def create_obj(cls, company_id: str, unionid: str, name: str,
                         external_type: int = 1, **kwargs) -> str:
        """
        创建外部联系人
        :param company_id:
        :param unionid: 微信唯一识别id
        :param name: 外部联系人姓名
        :param external_type: 外部联系人类型 1.微信， 2.企业微信
        :param kwargs: t_wework_external_contact 表里的字段
        """
        _values = {
            "company_id": company_id,
            "unionid": unionid,
            "name": name,
            "external_type": external_type
        }
        other_fields = external_contact_tbu.check_and_pop_fields(kwargs)
        if other_fields:
            _values.update(other_fields)
        engine = await db.default_db
        _id = await db_executor.single_create(engine, tb_wework_external_contact, _values)
        return _id

    @classmethod
    async def create_obj_data(cls, company_id: str, wework_external_contact_id: str, follow_user):
        """
        创建外部联系人数据
        :param company_id:
        :param wework_external_contact_id: 外部联系人表id
        :param follow_user: 外部联系人关联json
        """
        _values = {
            "company_id": company_id,
            "wework_external_contact_id": wework_external_contact_id,
            "follow_user": follow_user
        }
        engine = await db.default_db
        _id = await db_executor.single_create(engine, tb_wework_external_contact, _values)
        return _id

    @classmethod
    async def get_external_by_unionid(cls, company_id: str, unionid: str, fields: list = None):
        query_keys = external_contact_tbu.filter_keys(fields)
        exp = sa.select(
            [tb_wework_external_contact.c[key].label(key) for key in query_keys]
        ).where(
            and_(
                tb_wework_external_contact.c.company_id == company_id,
                tb_wework_external_contact.c.unionid == unionid
            )
        )
        engine = await db.default_db
        return await db_executor.fetch_one_data(engine, exp)

    @classmethod
    async def get_or_create(cls, company_id: str, unionid: str, name: str,
                            external_type: int = 1, fields: list = None, **kwargs):
        """
        获取或者创建外部联系人记录
        :param company_id:
        :param unionid: 微信唯一标识id
        :param name: 微信唯一标识id
        :param external_type: 外部联系人类型
        :param fields: 返回字段信息，创建对象时不受此字段影响
        """
        _fields = external_contact_tbu.filter_keys(fields)
        _obj = await cls.get_external_by_unionid(
            company_id, unionid, fields=_fields
        )
        if _obj:
            return False, _obj

        # 创建对象
        _values = {
            "company_id": company_id,
            "name": name,
            "unionid": unionid,
            "external_type": external_type
        }
        other_ = external_contact_tbu.check_and_pop_fields(kwargs)
        _values.update(other_)

        _id = await cls.create_obj(**_values)
        _values["id"] = _id
        return True, _values

    @classmethod
    async def update_external_contact(cls, company_id: str, unionid: str, **update_values) -> int:
        """
        创建或者更新对象
        :param company_id:
        :param unionid:
        :param update_values:
        :returns rowcount
        """
        _values = external_contact_tbu.check_and_pop_fields(update_values)
        _where = and_(
            tb_wework_external_contact.c.company_id == company_id,
            tb_wework_external_contact.c.unionid == unionid,
            tb_wework_external_contact.c.is_delete == 0
        )
        engine = await db.default_db
        return await db_executor.update_data(
            engine, tb_wework_external_contact, _values, where_stmt=_where
        )

    @classmethod
    async def create_or_update_external_contact_data(
            cls, company_id: str, wework_external_contact_id: str, follow_user):
        """
        创建
        :param company_id:
        :param wework_external_contact_id:
        :param follow_user:
        :return:
        """
        model = await cls.get_data_by_wework_external_contact_id(company_id, wework_external_contact_id)
        if model:
            await cls.update_external_contact_data(company_id, wework_external_contact_id, follow_user)
        else:
            await cls.create_external_contact_data(company_id, wework_external_contact_id, follow_user)

    @classmethod
    async def create_external_contact_data(cls, company_id: str, wework_external_contact_id: str, follow_user):
        """
        创建
        :param company_id:
        :param wework_external_contact_id:
        :param follow_user:
        :return:
        """
        _values = {
            'company_id': company_id,
            'wework_external_contact_id': wework_external_contact_id,
            'follow_user': follow_user
        }
        engine = await db.default_db
        _id = await db_executor.single_create(
            engine, tb_wework_external_contact_data, _values
        )
        return _id

    @classmethod
    async def update_external_contact_data(cls, company_id: str, wework_external_contact_id: str, follow_user):
        """
        更新
        :param company_id:
        :param wework_external_contact_id:
        :param follow_user:
        :return:
        """
        _values = {
            'follow_user': follow_user
        }
        _where = and_(
            tb_wework_external_contact_data.c.company_id == company_id,
            tb_wework_external_contact_data.c.wework_external_contact_id == wework_external_contact_id,
            tb_wework_external_contact_data.c.is_delete == 0
        )
        engine = await db.default_db
        return await db_executor.update_data(
            engine, tb_wework_external_contact_data, _values, where_stmt=_where
        )


class WeWorkExternalContactWay(object):
    @classmethod
    async def create(cls, app_id: int, company_id: str, employee_id: str, wework_user_id: str, config_id: str, qr_code: str):
        """
        创建企业微信联系我二维码管理
        @param app_id:
        @param company_id:
        @param employee_id:
        @param wework_user_id:
        @param config_id:
        @param qr_code:
        @return:
        """
        data = {
            'app_id': app_id,
            'company_id': company_id,
            'employee_id': employee_id,
            'wework_user_id': wework_user_id,
            'config_id': config_id,
            'qr_code': qr_code,
            'add_dt': datetime.datetime.now(),
            'update_dt': datetime.datetime.now()
        }
        engine = await db.default_db
        _id = await db_executor.single_create(engine, tb_wework_external_contact_way, data)
        return _id

    @classmethod
    async def get(cls, app_id: int, company_id: str, employee_id: str) -> dict:
        exp = sa.select(
            [
                tb_wework_external_contact_way.c.id.label('id'),
                tb_wework_external_contact_way.c.app_id.label('app_id'),
                tb_wework_external_contact_way.c.company_id.label('company_id'),
                tb_wework_external_contact_way.c.employee_id.label('employee_id'),
                tb_wework_external_contact_way.c.wework_user_id.label('wework_user_id'),
                tb_wework_external_contact_way.c.config_id.label('config_id'),
                tb_wework_external_contact_way.c.qr_code.label('qr_code'),
                tb_wework_external_contact_way.c.add_dt.label('add_dt'),
                tb_wework_external_contact_way.c.update_dt.label('update_dt')
            ]
        ).where(
            and_(
                tb_wework_external_contact_way.c.app_id == app_id,
                tb_wework_external_contact_way.c.company_id == company_id,
                tb_wework_external_contact_way.c.employee_id == employee_id,
                tb_wework_external_contact_way.c.is_delete == 0
            )
        )
        engine = await db.default_db
        result = await db_executor.fetch_one_data(engine, exp)
        return dict(result)

    @classmethod
    async def update(cls, app_id: int, company_id: str, employee_id: str, **kwargs):
        kwargs['update_dt'] = datetime.datetime.now()
        engine = await db.default_db
        async with engine.acquire() as conn:
            await conn.execute(
                sa.update(tb_wework_external_contact_way).where(
                    and_(
                        tb_wework_external_contact_way.c.app_id == app_id,
                        tb_wework_external_contact_way.c.company_id == company_id,
                        tb_wework_external_contact_way.c.employee_id == employee_id
                    )
                ).values(
                    **kwargs
                )
            )
