from __future__ import absolute_import

import asyncio
import datetime
import uuid

from error_code import Code
from kits.exception import ParamsError
from constants import CandidateRecordStatus
from services import svc
from services.s_dbs.s_job_position import JobPositionSelectService
from services.s_dbs.s_offer_record import OfferRecordQueryService
from services.s_es.s_candidate_record_es import OldCandidateRecordESService
from services.s_es.s_interview_es import OldInterviewESService
from utils.strutils import uuid2str

from utils import time_cal
from services.s_dbs.s_work_bench import WorkBenchService
from services.s_dbs.candidate_records.s_candidate_record import CandidateRecordService


class WorkBenchBusiness(object):

    @classmethod
    async def _last_position_ids(cls, company_id: str, user_id: str, index: int = 3) -> list:
        """
        获取最近职位 3个
        :return:
        """
        # 获取管理范围
        scope = await svc.manage_scope.hr_manage_scope(company_id=company_id, user_id=user_id)
        position_ids = scope.get("position_ids", [])

        # 缓存获取最近职位ids
        last_position_dict = await WorkBenchService.get_last_position_ids(
            company_id=company_id, user_id=user_id
        )

        set_position_ids = set(position_ids) & set(last_position_dict.keys())
        position_ids = sorted(list(set_position_ids), key=lambda x: last_position_dict[x], reverse=True)

        # return {p: last_position_dict[p] for p in list(set_position_ids)[:index]}
        return position_ids[:index]

    @classmethod
    async def get_last_position(cls, company_id: str, user_id: str) -> list:
        """
        最近职位卡片信息
        """
        company_id = uuid2str(company_id)
        user_id = uuid2str(user_id)

        # cache_key = redis_keys.LAST_POSITION_API[0].format(
        #     company_id=company_id, user_id=user_id
        # )
        # cache_data = await WorkBenchService.get_cache_for_bench_api(cache_key=cache_key)
        # if cache_data:
        #     return cache_data

        # 获取前3个职位的数据
        last_position_ids = await cls._last_position_ids(company_id=company_id, user_id=user_id)
        position_data_task = WorkBenchService.get_last_position_list(
            company_id=company_id, ids=last_position_ids
        )
        # 统计招聘中候选人总数
        candidate_map_task = OldCandidateRecordESService.get_job_position_total(
            company_id=company_id, permission_job_position_ids=last_position_ids,
            job_position_ids=last_position_ids,
            permission_candidate_record_ids=[], status=[30, 31, 40, 41, 42, 50, 51, 52]
        )

        # 待入职人数
        to_entry_map_task = CandidateRecordService.count_to_entry(
            company_id=company_id, position_ids=last_position_ids
        )

        # 已入职人数
        hired_count_task = OldCandidateRecordESService.get_job_position_total(
            company_id=company_id, permission_job_position_ids=last_position_ids, job_position_ids=last_position_ids,
            permission_candidate_record_ids=[], status=[CandidateRecordStatus.EMPLOY_STEP4]
        )
        _tasks = (position_data_task, candidate_map_task, to_entry_map_task, hired_count_task)
        position_data, candidate_map, to_entry_map, hired_map = await asyncio.gather(*_tasks)

        position_data = sorted(position_data, key=lambda x: last_position_ids.index(x["id"]))
        for position in position_data:
            _id = position["id"]
            position["to_entry"] = to_entry_map.get(_id, 0)
            # 统计招聘中人数
            position["candidate_total"] = candidate_map.get(_id, 0)
            position["dep_last_name"] = position["dep_name"].rsplit("/", 1)[-1] if position["dep_name"] else ""
            position["id"] = str(uuid.UUID(_id))
            # 剩余招聘人数
            if position["position_total"]:
                position["to_position_count"] = position["position_total"] - hired_map.get(_id, 0)
            else:
                position["to_position_count"] = 0

        # if position_data:
        #     await WorkBenchService.set_cache_for_bench_api(
        #         cache_key=cache_key, data=position_data, expire=redis_keys.LAST_POSITION_API[-1]
        #     )

        return position_data

    @classmethod
    async def get_position_today_add(cls, company_id: str, user_id: str) -> dict:
        """
        最近职位今日新增
        """
        company_id = uuid2str(company_id)
        user_id = uuid2str(user_id)

        # cache_key = redis_keys.POSITION_TODAY_ADD_API[0].format(
        #     company_id=company_id, user_id=user_id
        # )
        # cache_data = await WorkBenchService.get_cache_for_bench_api(cache_key)
        # if cache_data:
        #     return cache_data

        last_position_ids = await cls._last_position_ids(company_id=company_id, user_id=user_id)

        now = datetime.datetime.now()
        today_max_time = time_cal.get_date_max_datetime(now).strftime("%Y-%m-%d %H:%M:%S")
        today_time = time_cal.get_date_min_datetime(now).strftime("%Y-%m-%d")

        candidate_record_list = await CandidateRecordService.get_candidate_record_status_by_positions(
            company_id=company_id, position_ids=last_position_ids
        )

        # 今日待入职
        to_entry_map_task = OfferRecordQueryService.count_today_to_entry(
            company_id=company_id, candidate_record_ids=candidate_record_list
        )

        # 待面试
        to_interview_task = OldInterviewESService.get_job_position_total(
            company_id=company_id, permission_job_position_ids=[], permission_candidate_record_ids=[],
            job_position_ids=last_position_ids, interview_dt=[now.strftime("%Y-%m-%d %H:%M:%S"), None]
        )
        # 今日待面试
        today_to_interview_task = OldInterviewESService.get_job_position_total(
            company_id=company_id, permission_candidate_record_ids=[], permission_job_position_ids=[],
            job_position_ids=last_position_ids, interview_dt=[now.strftime("%Y-%m-%d %H:%M:%S"), today_max_time]
        )
        # 获取新增数据 新增候选人
        candidate_map_task = OldCandidateRecordESService.get_job_position_total(
            company_id=company_id, permission_job_position_ids=[], permission_candidate_record_ids=[],
            job_position_ids=last_position_ids, status=[], add_date=[today_time, today_time]
        )

        _tasks = (to_entry_map_task, to_interview_task, today_to_interview_task, candidate_map_task)
        to_entry_map, to_interview, today_to_interview, candidate_map = await asyncio.gather(*_tasks)

        ret = {}
        for position_id in last_position_ids:
            ret[str(uuid.UUID(position_id))] = {
                "today_candidate": candidate_map.get(position_id, 0),
                "today_to_entry": to_entry_map.get(position_id, 0),
                "to_interview": to_interview.get(position_id, 0),
                "today_to_interview": today_to_interview.get(position_id, 0)
            }

        # if ret:
        #     await WorkBenchService.set_cache_for_bench_api(
        #         cache_key=cache_key, data=ret, expire=redis_keys.POSITION_TODAY_ADD_API[-1]
        #     )
        return ret


class WorkBenchFlowBusiness(object):
    @classmethod
    async def _get_permission_position_ids(cls, company_id: str, user_id: str) -> list:
        scope = await svc.manage_scope.hr_manage_scope(company_id=company_id, user_id=user_id)
        return scope.get("position_ids") or []

    @classmethod
    async def get_recruitment_trends(cls, company_id: str, user_id: str) -> dict:
        """
        统计招聘工作台总览数据
        计划招聘 剩余招聘 今日新增 今日待入职 今日待面试
        """
        company_id = uuid2str(company_id)
        user_id = uuid2str(user_id)

        # cache_key = redis_keys.RECRUITMENT_TREND_API[0].format(
        #     company_id=company_id, user_id=user_id
        # )
        # cache = await WorkBenchService.get_cache_for_bench_api(cache_key=cache_key)
        # if cache:
        #     return cache

        permission_ids = await cls._get_permission_position_ids(company_id=company_id, user_id=user_id)

        # 计划招聘职位 不包括已停职位
        position_total_task = JobPositionSelectService.query_position_total(
            company_id=company_id, position_ids=permission_ids
        )
        candidate_record_task = CandidateRecordService.get_candidate_record_status_by_positions(
            company_id=company_id, position_ids=permission_ids
        )
        position_total_list, candidate_record_ids = await asyncio.gather(position_total_task, candidate_record_task)

        position_total = sum([p["position_total"] for p in position_total_list if p["position_total"]])

        # 今日待入职
        today_to_entry_task = OfferRecordQueryService.count_today_to_entry(
            company_id=company_id, candidate_record_ids=candidate_record_ids
        )

        # 今日新增候选人
        today_time = datetime.datetime.today().strftime("%Y-%m-%d")
        today_candidates_task = OldCandidateRecordESService.get_count(
            company_id=company_id, permission_job_position_ids=permission_ids, permission_candidate_record_ids=[],
            job_position_ids=[], status=[], add_date=[today_time, today_time]
        )
        # 今日待面试
        now = datetime.datetime.now()
        today_max_time = time_cal.get_date_max_datetime(now).strftime("%Y-%m-%d %H:%M:%S")
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        today_to_interview_task = OldInterviewESService.get_count(
            company_id=company_id, permission_job_position_ids=permission_ids,
            permission_candidate_record_ids=[], interview_dt=[now, today_max_time]
        )

        # 剩余招聘人数 = 计划招聘人数 - 已入职人数
        if position_total == 0:
            to_position_count = 0
            today_to_entry_map, today_candidates_count, today_to_interview = await asyncio.gather(
                today_to_entry_task, today_candidates_task, today_to_interview_task
            )

        else:
            position_ids = [p["job_position_id"] for p in position_total_list if p["position_total"]]
            hired_count_task = OldCandidateRecordESService.get_count(
                company_id=company_id, permission_job_position_ids=permission_ids, permission_candidate_record_ids=[],
                job_position_ids=position_ids, status=[CandidateRecordStatus.EMPLOY_STEP4]
            )
            hired_count, today_to_entry_map, today_candidates_count, today_to_interview = await asyncio.gather(
                hired_count_task, today_to_entry_task, today_candidates_task, today_to_interview_task
            )
            to_position_count = position_total - hired_count

        ret = {
            "position_total": position_total,
            "to_position_count": to_position_count,
            "today_candidates": today_candidates_count,
            "today_to_entry": sum(today_to_entry_map.values()),
            "today_to_interview": today_to_interview,
        }
        # await WorkBenchService.set_cache_for_bench_api(
        #     cache_key=cache_key, data=ret, expire=redis_keys.RECRUITMENT_TREND_API[-1]
        # )
        return ret

    @classmethod
    async def get_recruitment_flow_count(cls, company_id: str, user_id: str) -> dict:
        """
        统计招聘流程应聘记录数量
        初筛统计: 待初筛 和 初筛通过
        面试统计: 已安排面试, 已面试 和 面试通过
        录用统计: 拟录用 ， 已发Offer 和 待入职
        """
        company_id = uuid2str(company_id)
        user_id = uuid2str(user_id)

        if not (company_id and user_id):
            raise ParamsError(Code.PARAM_ERROR)

        # cache_key = redis_keys.RECRUITMENT_FLOW_API[0].format(
        #     company_id=company_id, user_id=user_id
        # )
        # cache_data = await WorkBenchService.get_cache_for_bench_api(cache_key=cache_key)
        # if cache_data:
        #     return cache_data

        _status = [
            CandidateRecordStatus.PRIMARY_STEP1, CandidateRecordStatus.PRIMARY_STEP2,
            CandidateRecordStatus.INTERVIEW_STEP1, CandidateRecordStatus.INTERVIEW_STEP2,
            CandidateRecordStatus.INTERVIEW_STEP3, CandidateRecordStatus.EMPLOY_STEP1,
            CandidateRecordStatus.EMPLOY_STEP2, CandidateRecordStatus.EMPLOY_STEP3
        ]

        # 获取管理范围

        position_ids = await cls._get_permission_position_ids(company_id=company_id, user_id=user_id)
        ret = await OldCandidateRecordESService.get_status_total(
            company_id=company_id, permission_job_position_ids=position_ids,
            permission_candidate_record_ids=[], status=_status
        )

        # await WorkBenchService.set_cache_for_bench_api(
        #     cache_key=cache_key, data=ret, expire=redis_keys.RECRUITMENT_FLOW_API[-1]
        # )
        return ret
