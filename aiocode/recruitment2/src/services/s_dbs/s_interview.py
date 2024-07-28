from __future__ import absolute_import

import datetime
from collections import defaultdict

import sqlalchemy as sa
from sqlalchemy import join
from sqlalchemy.sql import and_

from constants import CandidateRecordStatus
from drivers.mysql import db
from models.m_candidate_record import tb_candidate_record
from models.m_interview import tb_interview, tb_interview_participant_rel
from models.m_recruitment_team import tb_participant
from utils import time_cal
from utils.sa_db import db_executor
from utils.strutils import uuid2str


class InterviewQueryService(object):

    @classmethod
    async def count_to_interview(cls, company_id: str, candidate_record_ids: list) -> int:
        """统计待面试"""
        query = sa.select([
            sa.func.count(1)
        ]).where(
            and_(
                tb_interview.c.is_delete == 0,
                tb_interview.c.company_id == company_id,
                tb_interview.c.candidate_record_id.in_(candidate_record_ids),
                tb_interview.c.interview_dt > datetime.datetime.now()
            )
        )
        if candidate_record_ids:
            query = query.where(
                tb_interview.c.candidate_record_id.in_(candidate_record_ids)
            )

        engine = await db.default_db
        async with engine.acquire() as conn:
            cur = await conn.execute(query)
            count = await cur.scalar()
        return count

    @classmethod
    async def count_today_interview(cls, company_id: str, candidate_record_ids: list = None) -> int:
        """统计今日待面试数量"""
        today_min = datetime.datetime.now()
        today_max = time_cal.get_date_max_datetime(datetime.datetime.today())

        query = sa.select([
            sa.func.count(1)
        ]).where(
            and_(
                tb_interview.c.is_delete == 0,
                tb_interview.c.company_id == company_id,
                tb_interview.c.candidate_record_id.in_(candidate_record_ids),
                tb_interview.c.interview_dt.between(today_min, today_max)
            )
        )

        engine = await db.default_db
        async with engine.acquire() as conn:
            cur = await conn.execute(query)
            count = await cur.scalar()

        return count

    @classmethod
    async def count_today_interview_group_by(cls, company_id: str, candidate_record_ids: list):

        return

    @classmethod
    async def get_interviews_by_cdr_ids(cls, company_id: str, cdr_ids: list, fields: list, **kwargs) -> list:
        """
        根据应聘记录获取对应的面试记录
        @param company_id:
        @param cdr_ids:
        @param fields:
        @return:
        """
        stmt = sa.select(
            [tb_interview.c.get(field).label(field) for field in fields]
        ).where(
            and_(
                tb_interview.c.company_id == uuid2str(company_id),
                tb_interview.c.candidate_record_id.in_(cdr_ids),
            )
        ).order_by(
            tb_interview.c.count.asc()
        )
        start_dt = kwargs.get("start_dt")
        if start_dt:
            stmt = stmt.where(tb_interview.c.interview_dt >= start_dt)
        end_dt = kwargs.get("end_dt")
        if end_dt:
            end_dt = (datetime.datetime.strptime(end_dt, "%Y-%m-%d") + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            stmt = stmt.where(tb_interview.c.interview_dt < end_dt)
        is_latest = kwargs.get('is_latest')
        if is_latest is not None:
            stmt = stmt.where(tb_interview.c.is_latest == is_latest)
        is_delete = kwargs.get('is_delete')
        if is_delete is not None:
            stmt = stmt.where(tb_interview.c.is_delete == is_delete)

        engine = await db.default_db
        res = await db_executor.fetch_all_data(engine, stmt)

        return [dict(item) for item in res]

    @classmethod
    async def get_interviews(cls, company_id: str, fields: list, **kwargs) -> list:

        stmt = sa.select(
            [tb_interview.c.get(field).label(field) for field in fields]
        ).where(
            and_(
                tb_interview.c.company_id == uuid2str(company_id),
                tb_interview.c.is_delete == 0,
            )
        )
        add_by_ids = kwargs.get("add_by_ids")
        if add_by_ids:
            stmt = stmt.where(tb_interview.c.add_by_id.in_(add_by_ids))
        start_dt = kwargs.get("start_dt")
        if start_dt:
            stmt = stmt.where(tb_interview.c.add_dt >= start_dt)
        end_dt = kwargs.get("end_dt")
        if end_dt:
            end_dt = (datetime.datetime.strptime(end_dt, "%Y-%m-%d") + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            stmt = stmt.where(tb_interview.c.add_dt < end_dt)
        position_ids = kwargs.get("position_ids")
        if position_ids:
            tbs = join(
                tb_interview, tb_candidate_record,
                tb_interview.c.candidate_record_id == tb_candidate_record.c.id
            )
            stmt = stmt.select_from(tbs).where(
                tb_candidate_record.c.job_position_id.in_(position_ids)
            )

        engine = await db.default_db
        res = await db_executor.fetch_all_data(engine, stmt)

        return [dict(item) for item in res]

    @classmethod
    async def get_interviews_by_positions(cls, company_id: str, position_ids: list, **kwargs) -> list:
        tbs = join(
            tb_interview, tb_candidate_record,
            tb_interview.c.candidate_record_id == tb_candidate_record.c.id,
        )
        stmt = sa.select(
            [
                tb_interview.c.id.label("id"),
                tb_candidate_record.c.job_position_id.label("job_position_id")
            ]
        ).where(
            and_(
                tb_interview.c.company_id == uuid2str(company_id),
                tb_candidate_record.c.job_position_id.in_(position_ids),
                tb_interview.c.is_delete == 0,
            )
        ).select_from(tbs)
        start_dt = kwargs.get("start_dt")
        if start_dt:
            stmt = stmt.where(tb_interview.c.add_dt >= start_dt)
        end_dt = kwargs.get("end_dt")
        if end_dt:
            end_dt = (datetime.datetime.strptime(end_dt, "%Y-%m-%d") + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            stmt = stmt.where(tb_interview.c.add_dt < end_dt)
        engine = await db.default_db
        res = await db_executor.fetch_all_data(engine, stmt)

        return [dict(item) for item in res]


class InterViewParticipantService(object):

    @classmethod
    async def get_participant_interviews(cls, company_id: str, **kwargs) -> dict:
        tbs = join(
            tb_interview, tb_interview_participant_rel,
            tb_interview.c.id == tb_interview_participant_rel.c.interview_id,
        )
        stmt = sa.select(
            [
                tb_interview_participant_rel.c.participant_id.label("participant_id"),
                tb_interview_participant_rel.c.interview_id.label("interview_id"),
            ]
        ).where(
            and_(
                tb_interview_participant_rel.c.company_id == company_id,
                tb_interview_participant_rel.c.is_delete == 0,
                tb_interview.c.is_delete == 0
            )
        ).select_from(tbs)

        start_dt = kwargs.get("start_dt")
        end_dt = kwargs.get("end_dt")
        if start_dt:
            stmt = stmt.where(tb_interview.c.interview_dt >= start_dt)
        if end_dt:
            end_dt = (datetime.datetime.strptime(end_dt, "%Y-%m-%d") + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            stmt = stmt.where(tb_interview.c.interview_dt < end_dt)
        position_ids = kwargs.get("position_ids")
        engine = await db.default_db
        if position_ids:
            record_stmt = sa.select(
                [tb_candidate_record.c.id.label("id")]
            ).where(
                and_(
                    tb_candidate_record.c.company_id == company_id,
                    tb_candidate_record.c.job_position_id.in_(position_ids),
                    tb_candidate_record.c.is_delete == 0
                )
            )
            records = await db_executor.fetch_all_data(engine, record_stmt)
            record_ids = [item["id"] for item in records]
            if not record_ids:
                return {}
            stmt = stmt.where(tb_interview_participant_rel.c.candidate_record_id.in_(record_ids))

        res = await db_executor.fetch_all_data(engine, stmt)
        participant_id2interviews = defaultdict(list)
        for item in res:
            participant_id2interviews.setdefault(item["participant_id"], []).append(
                item["interview_id"]
            )

        return participant_id2interviews

    @classmethod
    async def get_participant_employed_records(cls, company_id: str, **kwargs) -> dict:
        """
        获取面试官相关的入职情况
        @param company_id:
        @return:
        """
        tbs = join(
            tb_candidate_record, tb_interview_participant_rel,
            tb_candidate_record.c.id == tb_interview_participant_rel.c.candidate_record_id,
        )
        stmt = sa.select(
            [
                tb_interview_participant_rel.c.participant_id.label("participant_id"),
                tb_interview_participant_rel.c.candidate_record_id.label("candidate_record_id"),
            ]
        ).where(
            and_(
                tb_interview_participant_rel.c.company_id == company_id,
                tb_interview_participant_rel.c.is_delete == 0,
                tb_candidate_record.c.status == CandidateRecordStatus.EMPLOY_STEP4,
                tb_candidate_record.c.is_delete == 0
            )
        ).select_from(tbs)

        start_dt = kwargs.get("start_dt")
        end_dt = kwargs.get("end_dt")
        if start_dt:
            stmt = stmt.where(tb_candidate_record.c.entry_dt >= start_dt)
        if end_dt:
            end_dt = (datetime.datetime.strptime(end_dt, "%Y-%m-%d") + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            stmt = stmt.where(tb_candidate_record.c.entry_dt < end_dt)
        position_ids = kwargs.get("position_ids")
        engine = await db.default_db
        if position_ids:
            stmt = stmt.where(tb_candidate_record.c.job_position_id.in_(position_ids))

        res = await db_executor.fetch_all_data(engine, stmt)
        participant_id2employed_records = defaultdict(set)
        for item in res:
            participant_id2employed_records.setdefault(item["participant_id"], set()).add(
                item["candidate_record_id"]
            )
        return participant_id2employed_records

    @classmethod
    async def get_participant_by_interview_ids(cls, company_id: str, interview_ids: list) -> dict:
        tbs = join(
            tb_participant, tb_interview_participant_rel,
            tb_participant.c.id == tb_interview_participant_rel.c.participant_id,
        )

        stmt = sa.select(
            [
                tb_interview_participant_rel.c.id.label("id"),
                tb_interview_participant_rel.c.interview_id.label("interview_id"),
                tb_participant.c.id.label('participant_id'),
                tb_participant.c.participant_refer_id.label('participant_refer_id'),
                tb_participant.c.name.label('name'),
                tb_interview_participant_rel.c.participant_type.label('participant_type'),
                tb_interview_participant_rel.c.is_comment.label('is_comment'),

            ]
        ).where(
            and_(
                tb_interview_participant_rel.c.company_id == company_id,
                tb_interview_participant_rel.c.interview_id.in_(interview_ids),
                tb_interview_participant_rel.c.is_delete == 0
            )
        ).order_by(
            tb_interview_participant_rel.c.add_dt.desc()
        ).select_from(tbs)

        engine = await db.default_db
        res = await db_executor.fetch_all_data(engine, stmt)
        participant_id2interviews = {}
        for item in res:
            if item.interview_id in participant_id2interviews:
                participant_id2interviews[item.interview_id].append(item)
            else:
                participant_id2interviews[item.interview_id] = [item]

        return participant_id2interviews
