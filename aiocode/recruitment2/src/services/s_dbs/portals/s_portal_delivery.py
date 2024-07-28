
import sqlalchemy as sa
from sqlalchemy.sql import and_, or_, func

from constants import RecruitPageType, DeliveryType
from drivers.mysql import db
from utils.sa_db import db_executor, Paginator
from utils.strutils import uuid2str
from utils.table_util import TableUtil
from models.m_portals import tb_recruitment_portal_record, tb_delivery_record, tb_recruit_portal_position

delivery_record_tbu = TableUtil(tb_delivery_record)


class DeliveryRecordService(object):

    @classmethod
    async def create_delivery_record(
            cls, company_id: str, candidate_record_id: str, position_record_id: str,
            delivery_scene: int = RecruitPageType.referral,
            delivery_type: int = DeliveryType.candidate,
            **kwargs
    ) -> str:
        """
        创建投递记录
        :param company_id:
        :param candidate_record_id: 应聘记录id
        :param position_record_id: 申请职位id
        :param delivery_scene: 投递场景 1 微信招聘， 2.内推
        :param delivery_type: 投递人类型 1 求职者， 2.员工 3. hr
        :param kwargs: 其他model字段
        """
        engine = await db.default_db
        _values = {
            "company_id": company_id,
            "candidate_record_id": candidate_record_id,
            "position_record_id": position_record_id,
            "delivery_scene": delivery_scene,
            "delivery_type": delivery_type
        }
        validate_dict = delivery_record_tbu.check_and_pop_fields(kwargs)
        _values.update(validate_dict)
        if _values['open_id'] is None:
            _values['open_id'] = ''
        _id = await db_executor.single_create(engine=engine, table_name=tb_delivery_record, values=_values)
        return _id

    @classmethod
    async def get_delivery_records_with_page(
            cls, company_id: str, page,
            candidate_record_ids: list = None, position_record_ids: list = None,
            is_payed: bool = None, start_dt: str = None, end_dt: str = None, referee_id: str = None,
            recruitment_page_ids: list = None, is_has_bonus: bool = None,
            fields: list = None, limit: int = 10) -> dict:
        """查询投递记录, 带分页"""
        exp = cls._build_filter(
            company_id=company_id, candidate_record_ids=candidate_record_ids,
            position_record_ids=position_record_ids, is_payed=is_payed, start_dt=start_dt, end_dt=end_dt,
            referee_id=referee_id, fields=fields, recruitment_page_ids=recruitment_page_ids,
            is_has_bonus=is_has_bonus
        )

        engine = await db.default_db
        paginator = Paginator(engine, exp, page, limit)
        return await paginator.data()

    @classmethod
    def _build_filter(
            cls, company_id: str, candidate_record_ids: list = None, position_record_ids: list = None,
            is_payed: bool = None, start_dt: str = None, end_dt: str = None, referee_id: str = None,
            recruitment_page_ids: list = None, is_has_bonus: bool = None,
            fields: list = None
    ):
        query_keys = delivery_record_tbu.filter_keys(fields)

        _and_exp = [
            tb_delivery_record.c.company_id == company_id,
            tb_delivery_record.c.is_delete == 0,
        ]
        if recruitment_page_ids:
            _and_exp.append(tb_delivery_record.c.recruitment_page_id.in_(recruitment_page_ids))
        if referee_id:
            _and_exp.append(tb_delivery_record.c.referee_id == referee_id)
        if candidate_record_ids:
            _and_exp.append(tb_delivery_record.c.candidate_record_id.in_(candidate_record_ids))
        if position_record_ids:
            _and_exp.append(tb_delivery_record.c.position_record_id.in_(position_record_ids))
        if is_payed is not None:
            _and_exp.append(tb_delivery_record.c.is_payed == is_payed)
        if start_dt:
            _and_exp.append(tb_delivery_record.c.add_dt >= start_dt)
        if end_dt:
            _and_exp.append(tb_delivery_record.c.add_dt <= end_dt)

        if is_has_bonus is not None:
            if is_has_bonus:
                _and_exp.append(tb_delivery_record.c.referral_bonus != '')
            else:
                _and_exp.append(tb_delivery_record.c.referral_bonus == '')

        exp = sa.select(
            [tb_delivery_record.c[key].label(key) for key in query_keys]
        ).where(
            and_(*_and_exp)
        ).order_by(
            tb_delivery_record.c.add_dt.desc()
        )
        return exp

    @classmethod
    async def delivery_record_stat(
            cls, company_id: str, emp_id: str = None, start_dt: str = None, end_dt: str = None
    ) -> dict:
        """投递记录统计, 按招聘门户分类"""
        exp = sa.select(
            [
                tb_delivery_record.c.recruitment_page_id.label("recruitment_page_id"),
                func.count(tb_delivery_record.c.id).label('count')
            ]
        ).where(
            and_(
                tb_delivery_record.c.company_id == company_id,
                tb_delivery_record.c.is_delete == 0
            )
        )
        if emp_id:
            exp = exp.where(tb_delivery_record.c.referee_id == emp_id)
        if start_dt:
            exp = exp.where(tb_delivery_record.c.add_dt >= start_dt)
        if end_dt:
            exp = exp.where(tb_delivery_record.c.add_dt <= end_dt)

        exp = exp.group_by("recruitment_page_id")
        engine = await db.default_db
        items = await db_executor.fetch_all_data(engine, exp)

        return {item.recruitment_page_id: item.count for item in items}

    @classmethod
    async def count_delivery_records_by_emp(cls, company_id: str, emp_id: str) -> int:
        """返回所有内推记录数量"""
        exp = sa.select(
            [sa.func.count(1)]
        ).where(
            and_(
                tb_delivery_record.c.company_id == company_id,
                tb_delivery_record.c.is_delete == 0,
                tb_delivery_record.c.referee_id == emp_id
            )
        )
        engine = await db.default_db
        async with engine.acquire() as conn:
            cur = await conn.execute(exp)
            count = await cur.scalar()
        return count

    @classmethod
    async def get_referral_records(
            cls, company_id: str, candidate_record_ids: list = None, position_record_ids: list = None,
            is_payed: bool = None, start_dt: str = None, end_dt: str = None, referee_id: str = None,
            recruitment_page_ids: list = None, is_has_bonus: bool = None,
            fields: list = None) -> list:
        """查询内推记录"""
        exp = cls._build_filter(
            company_id=company_id, candidate_record_ids=candidate_record_ids,
            position_record_ids=position_record_ids, is_payed=is_payed, start_dt=start_dt, end_dt=end_dt,
            referee_id=referee_id, recruitment_page_ids=recruitment_page_ids, is_has_bonus=is_has_bonus,
            fields=fields
        )
        engine = await db.default_db
        res = await db_executor.fetch_all_data(engine, exp)
        return [dict(r) for r in res]

    @classmethod
    async def update_record_payed(cls, company_id: str, user_id: str, ids: list, is_payed: bool):
        """批量更新内推记录是否发放奖金"""

        _where = and_(
            tb_delivery_record.c.company_id == company_id,
            tb_delivery_record.c.id.in_(ids),
            tb_delivery_record.c.is_delete == 0
        )
        engine = await db.default_db
        await db_executor.update_data(
            engine, tb_delivery_record,
            values={"is_payed": is_payed, "update_by_id": user_id}, where_stmt=_where
        )

    @classmethod
    async def update_record_referral_bonus(cls, company_id: str, user_id: str, ids: list, referral_bonus: str):
        """批量更新投递记录内推奖励"""
        referral_bonus = referral_bonus or ""
        _where = and_(
            tb_delivery_record.c.company_id == company_id,
            tb_delivery_record.c.id.in_(ids),
            tb_delivery_record.c.is_delete == 0
        )
        engine = await db.default_db
        await db_executor.update_data(
            engine, tb_delivery_record, where_stmt=_where,
            values={"referral_bonus": referral_bonus, "update_by_id": user_id}
        )

    @classmethod
    async def delete_records_by_candidate_records(cls, company_id: str, user_id: str, candidate_record_ids: list):
        """
        根据应聘记录删除投递记录
        @param company_id:
        @param user_id:
        @param candidate_record_ids:
        @return:
        """
        candidate_record_ids = [uuid2str(_id) for _id in candidate_record_ids]
        _where = and_(
            tb_delivery_record.c.company_id == uuid2str(company_id),
            tb_delivery_record.c.candidate_record_id.in_(candidate_record_ids),
            tb_delivery_record.c.is_delete == 0
        )
        engine = await db.default_db
        await db_executor.update_data(
            engine, tb_delivery_record,
            values={"is_delete": 1, "update_by_id": uuid2str(user_id)}, where_stmt=_where
        )

