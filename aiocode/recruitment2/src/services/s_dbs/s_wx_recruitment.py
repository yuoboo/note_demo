import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy import join
from sqlalchemy.sql.elements import and_
from drivers.mysql import db
from models.m_candidate_record import tb_candidate_record
from models.m_portals import tb_recruitment_portal_record
from utils.sa_db import db_executor
from utils.strutils import uuid2str
from utils.table_util import TableUtil

portal_record_tbu = TableUtil(tb_recruitment_portal_record)


class RecruitmentPageRecord(object):

    @classmethod
    async def get_company_pages(cls, company_id: str, fields: list = None):
        """查询企业所有的招聘网页信息"""
        _keys = portal_record_tbu.filter_keys(fields)
        exp = select(
            [tb_recruitment_portal_record.c[key].label(key) for key in _keys]
        ).where(
            and_(
                tb_recruitment_portal_record.c.company_id == company_id,
                tb_recruitment_portal_record.c.is_delete == 0
            )
        )
        engine = await db.default_db
        items = await db_executor.fetch_all_data(engine, exp)
        return [dict(item) for item in items]

    @classmethod
    async def get_all(cls, company_id: str, ids: list) -> list:
        """
        获取企业指定id的招聘网页信息
        @param company_id:
        @param ids:
        @return:
        """
        company_id = uuid2str(company_id)
        engine = await db.default_db
        stmt = select(
            [tb_recruitment_portal_record.c.get(field).label(field) for field in tb_recruitment_portal_record.c.keys()]).where(
            and_(
                tb_recruitment_portal_record.c.company_id == company_id,
                tb_recruitment_portal_record.c.is_delete == 0,
                tb_recruitment_portal_record.c.id.in_(ids)
            )
        )
        results = await db_executor.fetch_all_data(engine, stmt)
        return results

    @classmethod
    async def get_one_page(cls, company_id: str, pk: str, fields: list = None):
        """
        获取单个招聘网页信息
        :param company_id:
        :param pk:
        :param fields:
        :return:
        """
        _keys = portal_record_tbu.filter_keys(fields)
        engine = await db.default_db
        exp = select(
            [tb_recruitment_portal_record.c[key].label(key) for key in _keys]
        ).where(
            and_(
                tb_recruitment_portal_record.c.company_id == company_id,
                tb_recruitment_portal_record.c.id == pk,
                tb_recruitment_portal_record.c.is_delete == 0
            )
        )

        return await db_executor.fetch_one_data(engine, exp)

    @classmethod
    async def get_many_pages(cls, company_id: str, ids: list, fields: list = None):
        _keys = portal_record_tbu.filter_keys(fields)
        engine = await db.default_db
        exp = select(
            [tb_recruitment_portal_record.c[key].label(key) for key in _keys]
        ).where(
            and_(
                tb_recruitment_portal_record.c.company_id == company_id,
                tb_recruitment_portal_record.c.id.in_(ids),
                tb_recruitment_portal_record.c.is_delete == 0
            )
        )
        items = await db_executor.fetch_all_data(engine, exp)
        return [dict(item) for item in items]

    @classmethod
    async def get(cls, pk: str, fields: list = None):
        """
        获取单个招聘网页信息
        :param company_id:
        :param pk:
        :param fields:
        :return:
        """
        _keys = portal_record_tbu.filter_keys(fields)
        engine = await db.default_db
        exp = select(
            [tb_recruitment_portal_record.c[key].label(key) for key in _keys]
        ).where(
            and_(
                tb_recruitment_portal_record.c.id == pk,
                tb_recruitment_portal_record.c.is_delete == 0
            )
        )

        return await db_executor.fetch_one_data(engine, exp)


    @classmethod
    async def get_candidate_record_all(cls, company_id: str, cnadidate_record_ids: list) -> list:
        tbs = join(
            tb_candidate_record, tb_recruitment_portal_record,
            tb_candidate_record.c.recruitment_page_id == tb_recruitment_portal_record.c.id,
        )
        stmt = sa.select(
            [
                tb_recruitment_portal_record.c.id.label("id"),
                tb_recruitment_portal_record.c.name.label("name"),
                tb_candidate_record.c.id.label("candidate_record_id")
            ]
        ).where(
            and_(
                tb_recruitment_portal_record.c.company_id == uuid2str(company_id),
                tb_recruitment_portal_record.c.is_delete == 0,
                tb_candidate_record.c.id.in_(cnadidate_record_ids)
            )
        ).select_from(tbs)

        engine = await db.default_db
        results = await db_executor.fetch_all_data(engine, stmt)
        return results
