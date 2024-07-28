import asyncio

import ujson
from sqlalchemy import select, and_, or_
from drivers.mysql import db
from utils.sa_db import db_executor

from models.m_candidate import tb_candidate_remark, tb_candidate_tag, tb_candidate, tb_stand_resume
from utils.table_util import TableUtil


class CandidateRemarkService(object):
    """
    临时只读服务， 之后要切至redis和http
    """
    @classmethod
    async def get_latest_remark(cls, company_id, candidate_ids):
        """
        获取候选人最后一条备注信息
        @param company_id:
        @param candidate_ids:
        @return:
        """
        stmt = select(
            [
                tb_candidate_remark.c.id.label("id"),
                tb_candidate_remark.c.candidate_id.label("candidate_id"),
                tb_candidate_remark.c.text.label("text")
            ]
        ).where(
            and_(
                tb_candidate_remark.c.company_id == company_id,
                tb_candidate_remark.c.candidate_id.in_(candidate_ids),
                tb_candidate_remark.c.is_delete == 0
            )
        ).order_by(
            tb_candidate_remark.c.add_dt.desc()
        )

        engine = await db.default_db
        result_list = await db_executor.fetch_all_data(engine, stmt)

        latest_remark = {}
        for item in result_list:
            if item.candidate_id in latest_remark:
                continue
            latest_remark[item.candidate_id] = dict(item)
        return latest_remark


class CandidateTagService(object):
    """
    临时只读服务， 之后要切至redis和http
    """

    @classmethod
    async def get_tags(cls, company_id, tag_ids):
        """
        获取候选人标签信息
        @param company_id:
        @param tag_ids:
        @return:
        """
        stmt = select(
            [
                tb_candidate_tag.c.id.label("id"),
                tb_candidate_tag.c.name.label("name")
            ]
        ).where(
            and_(
                tb_candidate_tag.c.company_id == company_id,
                tb_candidate_tag.c.id.in_(tag_ids),
                tb_candidate_tag.c.is_delete == 0
            )
        )

        engine = await db.default_db
        result_list = await db_executor.fetch_all_data(engine, stmt)

        return result_list


candidate_tbu = TableUtil(tb_candidate)


class CandidateService(object):
    """
    临时只读服务， 之后要切至redis和http
    """

    @classmethod
    async def get_candidates(cls, company_id, candidate_ids):
        """
        获取候选人信息
        @param company_id:
        @param candidate_ids:
        @return:
        """
        stmt = select(
            [
                tb_candidate.c.id.label("id"),
                tb_candidate.c.avatar.label("avatar"),
                tb_candidate.c.talent_is_join.label("talent_is_join"),
                tb_candidate.c.talent_join_dt.label("talent_join_dt"),
                tb_candidate.c.talent_join_by_id.label("talent_join_by_id"),
                tb_candidate.c.wework_external_contact.label('wework_external_contact')
            ]
        ).where(
            and_(
                tb_candidate.c.company_id == company_id,
                tb_candidate.c.id.in_(candidate_ids),
                tb_candidate.c.is_delete == 0
            )
        )

        engine = await db.default_db
        result_list = await db_executor.fetch_all_data(engine, stmt)

        return result_list

    @classmethod
    async def get_candidates_by_ids(cls, company_id: str, candidate_ids: list, fields: list = None) -> list:
        """
        请不要加已删除过滤条件：某些关联的业务场景需要能查到姓名和手机号等展示信息
        @param company_id:
        @param candidate_ids:
        @param fields:
        @return:
        """
        res = []
        if candidate_ids:
            query_keys = candidate_tbu.tb_keys
            if fields:
                query_keys = list(filter(lambda x: x in query_keys, fields))
            exp = select(
                [tb_candidate.c[key].label(key) for key in query_keys]
            ).where(
                and_(
                    tb_candidate.c.company_id == company_id,
                    tb_candidate.c.id.in_(candidate_ids)
                )
            )
            engine = await db.default_db
            items = await db_executor.fetch_all_data(engine, exp)
            res = [dict(item) for item in items]

        return res

    @classmethod
    async def filter_talents(cls, company_id: str, keyword: str):
        """
        搜索人才
        @param company_id:
        @param keyword:
        @return:
        """
        stmt = select(
            [
                tb_candidate.c.id.label("id"), tb_candidate.c.name.label("name"),
                tb_candidate.c.mobile.label("mobile"), tb_candidate.c.email.label("email")
            ]
        ).where(
            and_(
                tb_candidate.c.company_id == company_id,
                or_(
                    tb_candidate.c.name.like(f'%{keyword}%'),
                    tb_candidate.c.mobile.like(f'%{keyword}%'),
                    tb_candidate.c.email.like(f'%{keyword}%')
                )
            )
        )
        items = await db_executor.fetch_all_data(db.default, stmt)
        return [dict(item) for item in items]


class CandidateStandResumeService(object):
    """
    临时只读服务， 之后要切至redis和http
    """

    @classmethod
    async def get_stand_resume_data(cls, company_id, candidate_record_ids):
        """
        获取候选人标准简历信息
        @param company_id:
        @param candidate_record_ids:
        @return:
        """
        stmt = select(
            [
                tb_stand_resume.c.candidate_record_id.label("candidate_record_id"),
                tb_stand_resume.c.data.label("data"),
            ]
        ).where(
            and_(
                tb_stand_resume.c.company_id == company_id,
                tb_stand_resume.c.candidate_record_id.in_(candidate_record_ids),
                tb_stand_resume.c.is_delete == 0
            )
        )

        engine = await db.default_db
        result_list = await db_executor.fetch_all_data(engine, stmt)

        results = {}
        for result in result_list:
            results[result.candidate_record_id] = ujson.loads(result.data)

        return results
