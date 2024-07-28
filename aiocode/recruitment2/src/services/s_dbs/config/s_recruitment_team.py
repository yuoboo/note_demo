# coding: utf-8
from sqlalchemy import select, join, and_

from drivers.mysql import db
from models.m_recruitment_team import tb_participant, tb_hr_emp_rel
from utils.sa_db import db_executor
from utils.strutils import uuid2str
from utils.table_util import TableUtil

participant_tbu = TableUtil(tb_participant)


class RecruitmentTeamService(object):

    @classmethod
    async def get_participants(cls, company_id: str, participant_type: int, fields: list, **kwargs):
        """
        查询面试官
        @param company_id:
        @param participant_type:
        @param fields:
        @param kwargs:
        @return:
        """
        fields = fields or [col.key for col in tb_participant.columns]
        stmt = select(
            [tb_participant.c.get(field).label(field) for field in fields]
        ).where(
            and_(
                tb_participant.c.company_id == uuid2str(company_id),
                tb_participant.c.participant_type == participant_type
            )
        )
        user_ids = kwargs.get("user_ids")
        if user_ids:
            stmt = stmt.where(tb_participant.c.participant_refer_id.in_(user_ids))
        participant_ids = kwargs.get("participant_ids")
        if participant_ids:
            stmt = stmt.where(tb_participant.c.id.in_(participant_ids))

        engine = await db.default_db
        res = await db_executor.fetch_all_data(engine, stmt)
        return [dict(item) for item in res]

    @classmethod
    async def get_all_participants(cls, company_id: str, participant_type: int = None, fields: list = None) -> list:
        fields = participant_tbu.filter_keys(fields)
        exp = select(
            [tb_participant.c[field].label(field) for field in fields]
        ).where(
            and_(
                tb_participant.c.company_id == uuid2str(company_id),
                tb_participant.c.is_delete == 0
            )
        )
        if participant_type:
            exp = exp.where(tb_participant.c.participant_type == participant_type)

        engine = await db.default_db
        items = await db_executor.fetch_all_data(engine, exp)
        return [dict(item) for item in items]

    @classmethod
    async def get_hr_emp_rel_list(cls, company_id: str):
        """
        获取当前企业的hr和员工关联信息
        @param company_id: 企业id
        @return:
        """
        stmt = select(
            [
                tb_hr_emp_rel.c.hr_id.label("hr_id"),
                tb_hr_emp_rel.c.emp_id.label("emp_id"),
            ]
        ).where(
            and_(
                tb_hr_emp_rel.c.company_id == uuid2str(company_id),
                tb_hr_emp_rel.c.is_delete == 0
            )
        )

        engine = await db.default_db
        res = await db_executor.fetch_all_data(engine, stmt)
        return [dict(item) for item in res]

    @classmethod
    async def get_hr_emp_rel_hr_list(cls, company_id: str):
        """
        获取当前企业的hr和员工关联信息 - hr
        @param company_id: 企业id
        @return:
        """
        stmt = select(
            [
                tb_hr_emp_rel.c.hr_id.label("hr_id"),
                tb_hr_emp_rel.c.emp_id.label("emp_id"),
            ]
        ).where(
            and_(
                tb_hr_emp_rel.c.company_id == uuid2str(company_id),
                tb_hr_emp_rel.c.is_delete == 0
            )
        )

        tbs = join(
            tb_hr_emp_rel, tb_participant,
            tb_hr_emp_rel.c.hr_id == tb_participant.c.participant_refer_id
        )

        stmt = stmt.select_from(tbs).where(
            and_(
                tb_participant.c.company_id == company_id,
                tb_participant.c.participant_type == 1,
                tb_participant.c.is_delete == 0,
                tb_participant.c.participant_refer_status == 0
            )
        )

        engine = await db.default_db
        res = await db_executor.fetch_all_data(engine, stmt)
        return [dict(item) for item in res]
