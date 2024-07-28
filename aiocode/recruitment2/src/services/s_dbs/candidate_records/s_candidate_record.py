# coding=utf-8
import asyncio
import typing
from datetime import datetime, timedelta

from sqlalchemy import select, func, and_, or_

from constants import CrStatus, CandidateRecordSource, CandidateRecordStatus
from constants.commons import null_uuid
from drivers.mysql import db
from kits.exception import APIValidationError
from models.m_candidate_record import tb_candidate_record, t_status_log, tb_candidate_record_forwards
from services.s_es.s_candidate_record_es import CandidateRecordESService
from utils.sa_db import db_executor
from utils.strutils import uuid2str, gen_uuid
from utils.table_util import TableUtil


candidate_record_tbu = TableUtil(tb_candidate_record)


class CandidateRecordService:
    def __init__(self, company_id: str = None):
        self.company_id = company_id

    async def get_count_by_recruitment_channel(self, channel_id: str, statuses: typing.List[int] = None,
                                               add_dt: str = None, referee_id: str = None) -> int:
        """
        指定渠道的应聘记录数量
        """
        engine = await db.default_db
        async with engine.acquire() as conn:
            exp = select([
                func.count()
            ]).where(
                and_(
                    tb_candidate_record.c.recruitment_channel_id == channel_id,
                    tb_candidate_record.c.company_id == self.company_id,
                    tb_candidate_record.c.is_delete == False
                )
            )
            if statuses:
                exp = exp.where(tb_candidate_record.c.status.in_(statuses))

            if add_dt:
                exp = exp.where(tb_candidate_record.c.add_dt >= add_dt)

            if referee_id:
                exp = exp.where(tb_candidate_record.c.referee_id == referee_id)

            result = await conn.execute(exp)
            count = await result.scalar()
            return count

    async def employed_count(self, job_position_id: str) -> int:
        """
        指定职位已入职人数
        """
        engine = await db.default_db
        async with engine.acquire() as conn:
            exp = select([
                func.count()
            ]).where(
                and_(
                    tb_candidate_record.c.company_id == self.company_id,
                    tb_candidate_record.c.is_delete == False,
                    tb_candidate_record.c.job_position_id == job_position_id,
                    tb_candidate_record.c.status == CrStatus.EMPLOYED
                )
            )
            result = await conn.execute(exp)
            count = await result.scalar()
            return count

    async def employed_map_by_jp_id(self, position_ids: list = None):
        """
        已入职数量的按职位group
        """
        stmt = select(
            [
                tb_candidate_record.c.job_position_id.label("job_position_id"),
                func.count(tb_candidate_record.c.id).label('employed_count')
            ]
        ).where(
            and_(
                tb_candidate_record.c.company_id == self.company_id,
                tb_candidate_record.c.is_delete == 0,
                tb_candidate_record.c.status == CrStatus.EMPLOYED
            )
        )
        if position_ids:
            stmt = stmt.where(tb_candidate_record.c.job_position_id.in_(position_ids))
        stmt = stmt.group_by("job_position_id")
        engine = await db.default_db
        rows = await db_executor.fetch_all_data(engine, stmt)
        ret = {row.job_position_id: row.employed_count for row in rows}

        return ret

    @classmethod
    async def check_candidate_record(cls, company_id: str, job_position_id: str, candidate_id: str) -> str:
        engine = await db.default_db
        exp = select(
            [tb_candidate_record.c.id.label("id")]
        ).where(
            and_(
                tb_candidate_record.c.company_id == uuid2str(company_id),
                tb_candidate_record.c.candidate_id == uuid2str(candidate_id),
                tb_candidate_record.c.job_position_id == uuid2str(job_position_id),
                tb_candidate_record.c.is_delete == 0
            )
        )
        res = await db_executor.fetch_one_data(engine, exp)
        return res["id"] if res else ""

    @classmethod
    async def get_candidate_records_by_positions(
            cls, company_id: str, position_ids: list, fields: list, **kwargs
    ) -> list:
        """
        根据职位获取应聘记录信息
        @param company_id:
        @param position_ids:
        @param fields:
        @return:
        """
        query = select(
            [tb_candidate_record.c.get(field).label(field) for field in fields]
        ).where(
            and_(
                tb_candidate_record.c.company_id == company_id,
                tb_candidate_record.c.job_position_id.in_(position_ids),
                tb_candidate_record.c.is_delete == 0
            )
        )
        start_dt = kwargs.get("start_dt")  # type: datetime.date
        if start_dt:
            query = query.where(tb_candidate_record.c.add_dt >= start_dt)
        end_dt = kwargs.get("end_dt")  # type: datetime.date
        if end_dt:
            end_dt = (datetime.strptime(end_dt, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
            query = query.where(tb_candidate_record.c.add_dt < end_dt)
        engine = await db.default_db
        ret = await db_executor.fetch_all_data(engine, query)

        return [dict(item) for item in ret]

    @classmethod
    async def get_candidate_record_ids_by_positions(
            cls, company_id: str, position_ids: list, status: list = None
    ) -> dict:
        """查询应聘记录id"""
        query = select([
            tb_candidate_record.c.id, tb_candidate_record.c.job_position_id
        ]).where(
            and_(
                tb_candidate_record.c.company_id == company_id,
                tb_candidate_record.c.job_position_id.in_(position_ids),
                tb_candidate_record.c.is_delete == 0
            )
        )
        if status:
            query = query.where(
                tb_candidate_record.c.status.in_(status)
            )

        engine = await db.default_db
        async with engine.acquire() as conn:
            cur = await conn.execute(query)
            ret = await cur.fetchall()
        return {r[0]: r[1] for r in ret}

    @classmethod
    async def get_candidate_record_status_by_positions(cls, company_id: str, position_ids: list) -> list:
        """查询待入职应聘记录id"""
        query = select([
            tb_candidate_record.c.id,
        ]).where(
            and_(
                tb_candidate_record.c.company_id == company_id,
                tb_candidate_record.c.status == CandidateRecordStatus.EMPLOY_STEP3,
                tb_candidate_record.c.job_position_id.in_(position_ids),
                tb_candidate_record.c.is_delete == 0
            )
        )
        engine = await db.default_db
        res = await db_executor.fetch_all_data(engine=engine, stmt=query)
        return [r[0] for r in res if r]

    @classmethod
    async def count_to_entry(cls, company_id: str, position_ids: list) -> dict:
        """统计总览待入职数量"""

        query = select([
            tb_candidate_record.c.job_position_id,
            func.count(1)
        ]).where(
            and_(
                tb_candidate_record.c.company_id == company_id,
                tb_candidate_record.c.job_position_id.in_(position_ids),
                tb_candidate_record.c.status == CandidateRecordStatus.EMPLOY_STEP3,
                tb_candidate_record.c.is_delete == 0
            )
        ).group_by(
            tb_candidate_record.c.job_position_id
        )
        engine = await db.default_db
        res = await db_executor.fetch_all_data(engine=engine, stmt=query)
        return {r[0]: r[1] for r in res}

    @classmethod
    async def get_eliminated_records_by_positions(
            cls, company_id: str, position_ids: list, fields: list, **kwargs
    ) -> list:
        """
        根据职位获取淘汰应聘记录
        @param company_id:
        @param position_ids:
        @param fields:
        @return:
        """
        eliminated_status_list = [
            CandidateRecordStatus.PRIMARY_STEP3,
            CandidateRecordStatus.INTERVIEW_STEP4,
            CandidateRecordStatus.EMPLOY_STEP5
        ]
        query = select(
            [tb_candidate_record.c.get(field).label(field) for field in fields]
        ).where(
            and_(
                tb_candidate_record.c.company_id == company_id,
                tb_candidate_record.c.job_position_id.in_(position_ids),
                tb_candidate_record.c.is_delete == 0
            )
        )
        # 导出场景不需要指定此参数， 可以一次性查出来
        eliminated_status = kwargs.get("eliminated_status")
        if eliminated_status and eliminated_status not in eliminated_status_list:
            raise APIValidationError(msg="淘汰原因参数错误")
        if eliminated_status:
            query = query.where(tb_candidate_record.c.status == eliminated_status)
        else:
            query = query.where(tb_candidate_record.c.status.in_(eliminated_status_list))

        start_dt = kwargs.get("start_dt")  # type: datetime.date
        if start_dt:
            query = query.where(tb_candidate_record.c.eliminated_dt >= start_dt)
        end_dt = kwargs.get("end_dt")  # type: datetime.date
        if end_dt:
            end_dt = (datetime.strptime(end_dt, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
            query = query.where(tb_candidate_record.c.eliminated_dt < end_dt)
        engine = await db.default_db
        ret = await db_executor.fetch_all_data(engine, query)

        return [dict(item) for item in ret]

    @classmethod
    async def get_candidate_records(
            cls, company_id: str, fields: list, **kwargs
    ) -> list:
        """
        @param company_id:
        @param fields:
        @return:
        """
        query = select(
            [tb_candidate_record.c.get(field).label(field) for field in fields]
        ).where(
            and_(
                tb_candidate_record.c.company_id == company_id,
                tb_candidate_record.c.is_delete == 0
            )
        )
        position_ids = kwargs.get("position_ids")
        if position_ids:
            query = query.where(tb_candidate_record.c.job_position_id.in_(position_ids))
        add_by_ids = kwargs.get("add_by_ids")
        if add_by_ids:
            query = query.where(tb_candidate_record.c.add_by_id.in_(add_by_ids))
        start_dt = kwargs.get("start_dt")
        if start_dt:
            query = query.where(tb_candidate_record.c.add_dt >= start_dt)
        end_dt = kwargs.get("end_dt")
        if end_dt:
            end_dt = (datetime.strptime(end_dt, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
            query = query.where(tb_candidate_record.c.add_dt < end_dt)

        engine = await db.default_db
        ret = await db_executor.fetch_all_data(engine, query)

        return [dict(item) for item in ret]

    @classmethod
    async def get_employed_records_by_positions(
            cls, company_id: str, position_ids: list, fields: list, **kwargs
    ) -> list:
        """
        根据职位获取已入职应聘记录信息
        @param company_id:
        @param position_ids:
        @param fields:
        @return:
        """
        query = select(
            [tb_candidate_record.c.get(field).label(field) for field in fields]
        ).where(
            and_(
                tb_candidate_record.c.company_id == company_id,
                tb_candidate_record.c.status == CandidateRecordStatus.EMPLOY_STEP4,
                tb_candidate_record.c.job_position_id.in_(position_ids),
                tb_candidate_record.c.is_delete == 0
            )
        )
        start_dt = kwargs.get("start_dt")  # type: datetime.date
        if start_dt:
            query = query.where(tb_candidate_record.c.entry_dt >= start_dt)
        end_dt = kwargs.get("end_dt")  # type: datetime.date
        if end_dt:
            end_dt = (datetime.strptime(end_dt, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
            query = query.where(tb_candidate_record.c.entry_dt < end_dt)
        engine = await db.default_db
        ret = await db_executor.fetch_all_data(engine, query)

        return [dict(item) for item in ret]

    @classmethod
    async def get_candidate_record_by_referee(
            cls, company_id: str, status: list = None, candidate_ids: list = None, referee: str = None,
            job_position_ids: list = None, fields: list = None
    ) -> list:
        """
        根据条件查询应聘记录
        :param company_id:
        :param status: 应聘记录状态
        :param candidate_ids: 候选人ids
        :param referee: 内推人姓名/手机号 支持模糊查询
        :param job_position_ids: 招聘职位ids
        :param fields: 需要返回的字段
        """
        query_keys = candidate_record_tbu.filter_keys(fields)

        _and_sql = [
            tb_candidate_record.c.company_id == company_id,
            tb_candidate_record.c.is_delete == 0
        ]

        if status:
            _and_sql.append(tb_candidate_record.c.status.in_(status))

        if candidate_ids:
            _and_sql.append(
                tb_candidate_record.c.candidate_id.in_(candidate_ids)
            )

        if referee:
            _and_sql.append(
                or_(
                    tb_candidate_record.c.referee_name == referee,
                    tb_candidate_record.c.referee_mobile == referee,
                )
            )

        if job_position_ids:
            _and_sql.append(
                tb_candidate_record.c.job_position_id.in_(job_position_ids)
            )

        exp = select(
            [tb_candidate_record.c[key].label(key) for key in query_keys]
        ).where(and_(*_and_sql)).order_by(tb_candidate_record.c.add_dt.desc())

        engine = await db.default_db
        ret = await db_executor.fetch_all_data(engine, exp)
        return [dict(r) for r in ret]

    @classmethod
    async def get_candidate_records_by_ids(cls, company_id: str, candidate_record_ids: list,
                                           status: list = None, fields: list = None) -> list:
        fields = candidate_record_tbu.filter_keys(fields)
        exp = select(
            [tb_candidate_record.c[key].label(key) for key in fields]
        ).where(
            and_(
                tb_candidate_record.c.company_id == company_id,
                tb_candidate_record.c.id.in_(candidate_record_ids),
                tb_candidate_record.c.is_delete == 0
            )
        )
        if status:
            exp = exp.where(tb_candidate_record.c.status.in_(status))

        engine = await db.default_db
        items = await db_executor.fetch_all_data(engine, exp)
        return [dict(item) for item in items]

    @classmethod
    async def get_candidate_record_by_channel_id(cls, company_id: str, channel_ids: list, fields: list = None):
        exp = select(
            [tb_candidate_record.c[key].label(key) for key in fields]
        ).where(
            and_(
                tb_candidate_record.c.company_id == company_id,
                tb_candidate_record.c.is_delete == 0,
                tb_candidate_record.c.recruitment_channel_id.in_(channel_ids),
                tb_candidate_record.c.status == CandidateRecordStatus.EMPLOY_STEP4
            )
        )
        engine = await db.default_db
        items = await db_executor.fetch_all_data(engine, exp)
        return [dict(item) for item in items]

    @classmethod
    async def get_recruiting_records_by_candidate_ids(
            cls, company_id: str, candidate_ids: list, fields: list = None
    ):
        """
        根据候选人查询招聘中应聘记录
        @param company_id:
        @param candidate_ids:
        @param fields:
        @return:
        """
        recruiting_status = [
            CandidateRecordStatus.PRIMARY_STEP1, CandidateRecordStatus.PRIMARY_STEP2,
            CandidateRecordStatus.INTERVIEW_STEP1, CandidateRecordStatus.INTERVIEW_STEP2,
            CandidateRecordStatus.INTERVIEW_STEP3, CandidateRecordStatus.EMPLOY_STEP1,
            CandidateRecordStatus.EMPLOY_STEP2, CandidateRecordStatus.EMPLOY_STEP3
        ]
        fields = fields or ["id"]
        exp = select(
            [tb_candidate_record.c[key].label(key) for key in fields]
        ).where(
            and_(
                tb_candidate_record.c.company_id == company_id,
                tb_candidate_record.c.is_delete == 0,
                tb_candidate_record.c.candidate_id.in_(candidate_ids),
                tb_candidate_record.c.status.in_(recruiting_status)
            )
        )
        engine = await db.default_db
        items = await db_executor.fetch_all_data(engine, exp)
        return [dict(item) for item in items]


class CandidateRecordCreateService(object):
    """
    应聘记录创建服务类
    """
    @classmethod
    async def create_candidate_record(
            cls, company_id, user_id,
            candidate_id,
            candidate_record_id,
            job_position_id,
            recruitment_channel_id,
            record_status,
            source=CandidateRecordSource.HR,
            referee_id=None,
            referee_name=None,
            referee_mobile=None
    ):
        """
        创建候选人应聘记录
        :param company_id:
        :param user_id:
        :param candidate_id:
        :param candidate_record_id:
        :param job_position_id:
        :param recruitment_channel_id:
        :param record_status:
        :param source:
        :param referee_id:
        :param referee_name:
        :param referee_mobile:
        :return:
        """
        interview_count = 0
        if record_status in [
            CrStatus.INTERVIEW_ARRANGED, CrStatus.INTERVIEWED,
            CrStatus.INTERVIEW_PASSED, CrStatus.INTERVIEW_ELIMINATE
        ]:
            interview_count = 1
        eliminated_dt = None
        eliminated_by_id = None
        if record_status in [
            CrStatus.PRELIMINARY_SCREEN_ELIMINATE,
            CrStatus.INTERVIEW_ELIMINATE,
            CrStatus.EMPLOYMENT_CANCELED
        ]:
            eliminated_dt = datetime.now()
            eliminated_by_id = uuid2str(user_id)
        engine = await db.default_db
        async with engine.acquire() as conn:
            await conn.execute(
                tb_candidate_record.insert().values(
                    id=uuid2str(candidate_record_id),
                    company_id=uuid2str(company_id),
                    candidate_id=uuid2str(candidate_id),
                    job_position_id=uuid2str(job_position_id),
                    recruitment_channel_id=uuid2str(recruitment_channel_id) if recruitment_channel_id else None,
                    status=record_status,
                    source=source,
                    interview_count=interview_count,
                    referee_id=uuid2str(referee_id) if referee_id else None,
                    referee_name=referee_name,
                    referee_mobile=referee_mobile,
                    add_by_id=uuid2str(user_id),
                    add_dt=datetime.now(),
                    update_by_id=uuid2str(user_id),
                    update_dt=datetime.now(),
                    eliminated_by_id=eliminated_by_id,
                    eliminated_dt=eliminated_dt
                )
            )

            # 记录统计用的日志
            await conn.execute(
                t_status_log.insert().values(
                    id=gen_uuid(),
                    company_id=uuid2str(company_id),
                    candidate_id=uuid2str(candidate_id),
                    candidate_record_id=uuid2str(candidate_record_id),
                    job_position_id=uuid2str(job_position_id),
                    status_before=0,
                    status_after=record_status,
                    add_dt=datetime.now(),
                    add_by_id=uuid2str(user_id)
                )
            )

        candidate_records = await CandidateRecordService.get_candidate_records_by_ids(
            company_id=company_id, candidate_record_ids=[candidate_record_id])
        if len(candidate_records) == 1:
            await CandidateRecordESService.save_candidate_record(candidate_records[0])

    @classmethod
    async def create_obj(cls, company_id: str, user_id: str, candidate_id: str, job_position_id: str, **kwargs) -> str:
        user_id = user_id or null_uuid,
        _values = {
            "company_id": company_id,
            "candidate_id": candidate_id,
            "job_position_id": job_position_id,
            "add_by_id": user_id,
            "update_by_id": user_id
        }
        _other = candidate_record_tbu.check_and_pop_fields(kwargs)
        if _other:
            _values.update(_other)
        engine = await db.default_db
        return await db_executor.single_create(engine, tb_candidate_record, _values)


class CandidateRecordForwards(object):
    @classmethod
    async def get_forward_records_for_me(cls, company_id, candidate_record_ids, my_ids):
        """
        获取我转发的应聘记录信息
        @param company_id:
        @param candidate_record_ids:
        @param my_ids:
        @return:
        """
        stmt = select(
            [
                tb_candidate_record_forwards.c.candidate_record_id.label("candidate_record_id"),
                tb_candidate_record_forwards.c.comment.label("comment"),
                tb_candidate_record_forwards.c.log_desc.label("log_desc"),
            ]
        ).where(
            and_(
                tb_candidate_record_forwards.c.company_id == company_id,
                tb_candidate_record_forwards.c.candidate_record_id.in_(candidate_record_ids),
                tb_candidate_record_forwards.c.add_by_id.in_(my_ids)
            )
        )

        engine = await db.default_db
        result_list = await db_executor.fetch_all_data(engine, stmt)

        id2info = {}
        for item in result_list:
            id2info[item.candidate_record_id] = dict(item)
        return id2info


if __name__ == "__main__":

    async def helper():
        res = await CandidateRecordService('ec9ab455f91c46c9abaf47d508182972').employed_map_by_jp_id(
            ['8ceea40d6fcf4d948d4aee3ea2ff530e', '1865346c95bf48d3946b06604ae62748']
        )
        print(res)


    asyncio.run(helper())
