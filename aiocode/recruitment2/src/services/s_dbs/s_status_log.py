# coding: utf-8
from datetime import datetime, timedelta
from operator import and_

from sqlalchemy import select

from drivers.mysql import db
from models.m_candidate_record import t_status_log
from utils.sa_db import db_executor
from utils.strutils import gen_uuid, uuid2str


class CandidateStatusLog(object):

    @classmethod
    async def create_status_log(
            cls, company_id, user_id, candidate_id, cr_id, job_position_id, status_before, status_after
    ):
        """
        添加状态log
        """
        engine = await db.default_db
        async with engine.acquire() as conn:
            await conn.execute(
                t_status_log.insert().values(
                    id=gen_uuid(),
                    company_id=uuid2str(company_id),
                    candidate_id=uuid2str(candidate_id),
                    candidate_record_id=uuid2str(cr_id),
                    job_position_id=uuid2str(job_position_id),
                    status_before=status_before,
                    status_after=status_after,
                    add_dt=datetime.now(),
                    add_by_id=uuid2str(user_id)
                )
            )

    @classmethod
    async def query_log_by_positions(cls, company_id: str, position_ids: list, fields: list, **kwargs):
        """
        根据招聘职位ids获取操作记录
        @param company_id:
        @param position_ids:
        @param fields:
        @param kwargs:
        @return:
        """
        stmt = select(
            [t_status_log.c.get(field).label(field) for field in fields]
        ).where(
            and_(
                t_status_log.c.company_id == company_id,
                t_status_log.c.job_position_id.in_(position_ids)
            )
        )
        start_dt = kwargs.get("start_dt")
        if start_dt:
            stmt = stmt.where(t_status_log.c.add_dt >= start_dt)
        end_dt = kwargs.get("end_dt")
        if end_dt:
            end_dt = (datetime.strptime(end_dt, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
            stmt = stmt.where(t_status_log.c.add_dt < end_dt)
        engine = await db.default_db
        res = await db_executor.fetch_all_data(engine, stmt)

        return [dict(item) for item in res]

    @classmethod
    async def query_logs(cls, company_id: str, fields: list, **kwargs):
        """
        @param company_id:
        @param fields:
        @param kwargs:
        @return:
        """
        stmt = select(
            [t_status_log.c.get(field).label(field) for field in fields]
        ).where(t_status_log.c.company_id == company_id)

        position_ids = kwargs.get("position_ids")
        if position_ids:
            stmt = stmt.where(t_status_log.c.job_position_id.in_(position_ids))
        add_by_ids = kwargs.get("add_by_ids")
        if add_by_ids:
            stmt = stmt.where(t_status_log.c.add_by_id.in_(add_by_ids))
        start_dt = kwargs.get("start_dt")
        if start_dt:
            stmt = stmt.where(t_status_log.c.add_dt >= start_dt)
        end_dt = kwargs.get("end_dt")
        if end_dt:
            end_dt = (datetime.strptime(end_dt, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
            stmt = stmt.where(t_status_log.c.add_dt < end_dt)
        engine = await db.default_db
        res = await db_executor.fetch_all_data(engine, stmt)

        return [dict(item) for item in res]
