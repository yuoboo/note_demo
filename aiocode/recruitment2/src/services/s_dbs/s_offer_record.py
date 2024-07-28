import datetime

import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.sql import and_

from drivers.mysql import db
from models.m_offer import tb_offer_record, tb_offer_submit_record
from utils.sa_db import db_executor
from utils.strutils import uuid2str


class OfferRecordQueryService(object):

    @classmethod
    async def count_today_to_entry(cls, company_id: str, candidate_record_ids: list) -> dict:
        """
        统计今日待入职： 入职日期为今天的应聘记录
        """
        query = sa.select([
            tb_offer_record.c.job_position_id,
            sa.func.count(1)
        ]).where(
            and_(
                tb_offer_record.c.company_id == company_id,
                tb_offer_record.c.candidate_record_id.in_(candidate_record_ids),
                tb_offer_record.c.is_latest == 1,
                tb_offer_record.c.hire_dt == datetime.datetime.today().strftime("%Y-%m-%d")
            )
        ).group_by(
            tb_offer_record.c.job_position_id
        )
        engine = await db.default_db
        res = await db_executor.fetch_all_data(engine=engine, stmt=query)
        return {r[0]: r[1] for r in res}

    @classmethod
    async def get_offer_records_by_cdr_ids(cls, company_id: str, cdr_ids: list, fields: list, **kwargs) -> list:
        """
        根据应聘记录获取对应的offer记录
        @param company_id:
        @param cdr_ids:
        @param fields:
        @return:
        """
        stmt = select(
            [tb_offer_record.c.get(field).label(field) for field in fields]
        ).where(
            and_(
                tb_offer_record.c.company_id == uuid2str(company_id),
                tb_offer_record.c.candidate_record_id.in_(cdr_ids),
                tb_offer_record.c.is_real_offer == 1
            )
        )
        start_dt = kwargs.get("start_dt")
        if start_dt:
            stmt = stmt.where(tb_offer_record.c.add_dt >= start_dt)
        end_dt = kwargs.get("end_dt")
        if end_dt:
            end_dt = (datetime.datetime.strptime(end_dt, "%Y-%m-%d") + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            stmt = stmt.where(tb_offer_record.c.add_dt < end_dt)

        engine = await db.default_db
        res = await db_executor.fetch_all_data(engine, stmt)

        return [dict(item) for item in res]

    @classmethod
    async def get_offer_records(cls, company_id: str, fields: list, **kwargs) -> list:
        """
        @param company_id:
        @param fields:
        @return:
        """
        stmt = select(
            [tb_offer_record.c.get(field).label(field) for field in fields]
        ).where(
            and_(
                tb_offer_record.c.company_id == uuid2str(company_id),
                tb_offer_record.c.is_real_offer == 1
            )
        )
        position_ids = kwargs.get("position_ids")
        if position_ids:
            stmt = stmt.where(tb_offer_record.c.job_position_id.in_(position_ids))

        add_by_ids = kwargs.get("add_by_ids")
        if add_by_ids:
            stmt = stmt.where(tb_offer_record.c.add_by_id.in_(add_by_ids))
        start_dt = kwargs.get("start_dt")
        if start_dt:
            stmt = stmt.where(tb_offer_record.c.add_dt >= start_dt)
        end_dt = kwargs.get("end_dt")
        if end_dt:
            end_dt = (datetime.datetime.strptime(end_dt, "%Y-%m-%d") + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            stmt = stmt.where(tb_offer_record.c.add_dt < end_dt)

        engine = await db.default_db
        res = await db_executor.fetch_all_data(engine, stmt)

        return [dict(item) for item in res]


class OfferSubmitRecord(object):
    @classmethod
    async def get_offer_submit_by_candidate_record_ids(
            cls, company_id: str, candidate_record_ids: list) -> dict:
        """
        根据职位Ids获取职位信息
        """
        company_id = uuid2str(company_id)
        engine = await db.default_db
        stmt = select([tb_offer_submit_record.c.get(field).label(field) for field in tb_offer_submit_record.c.keys()]).where(
            and_(
                tb_offer_submit_record.c.company_id == company_id,
                tb_offer_submit_record.c.candidate_record_id.in_(candidate_record_ids),
                tb_offer_submit_record.c.is_latest == 1
            )
        )
        result_list = await db_executor.fetch_all_data(engine, stmt)
        id2info = {}
        for item in result_list:
            id2info[item.candidate_record_id] = dict(item)
        return id2info
