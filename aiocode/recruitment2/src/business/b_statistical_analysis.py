# coding: utf-8
from asyncio import gather
from collections import defaultdict, Counter
from functools import reduce
from hashlib import md5
from operator import add

import ujson

from constants import JobPositionStatus, CandidateRecordStatus, JobPositionEmergencyLevel, ParticipantType, \
    RecruitStatsType
from constants.redis_keys import RECRUIT_PROGRESS_POSITION, RECRUIT_PROGRESS_POSITION_SHEET, RECRUIT_TRANSFER_STATS, \
    ELIMINATED_REASON_STATS, POSITION_WORKLOAD_STATS, HR_WORKLOAD_STATS, EMP_WORKLOAD_STATS
from drivers.redis import redis_db
from services import svc
from services.s_dbs.config.s_eliminated_reason import EliminatedReasonService
from services.s_dbs.config.s_recruitment_team import RecruitmentTeamService
from services.s_dbs.candidate_records.s_candidate_record import CandidateRecordService
from services.s_dbs.s_interview import InterviewQueryService, InterViewParticipantService
from services.s_dbs.s_job_position import JobPositionSelectService, PositionParticipantService
from services.s_dbs.s_offer_record import OfferRecordQueryService
from services.s_dbs.s_recruitment_channel import RecruitmentChannelService
from services.s_dbs.s_status_log import CandidateStatusLog
from services.s_https.s_employee import DepartmentService, JobGroupService
from utils.api_auth import validate_permission
from utils.number_cal import to_decimal
from utils.strutils import uuid2str
from utils.time_cal import get_date_min_datetime, get_date_max_datetime

STATUS_KEY_MAP = {
    CandidateRecordStatus.EMPLOY_STEP4: 'employed',
    CandidateRecordStatus.EMPLOY_STEP3: 'to_be_employed',
    CandidateRecordStatus.EMPLOY_STEP2: 'offer_issued',
    CandidateRecordStatus.EMPLOY_STEP1: 'proposed_employment',
    CandidateRecordStatus.PRIMARY_STEP2: 'preliminary_screen_passed',
    CandidateRecordStatus.PRIMARY_STEP1: 'to_be_preliminary_screen',
    CandidateRecordStatus.INTERVIEW_STEP1: 'interview_arranged',
    CandidateRecordStatus.INTERVIEW_STEP2: 'interviewed',
    CandidateRecordStatus.INTERVIEW_STEP3: 'interview_passed'
}

RECRUITING_STATUS = [
    CandidateRecordStatus.PRIMARY_STEP1, CandidateRecordStatus.PRIMARY_STEP2,
    CandidateRecordStatus.INTERVIEW_STEP1, CandidateRecordStatus.INTERVIEW_STEP2,
    CandidateRecordStatus.INTERVIEW_STEP3, CandidateRecordStatus.EMPLOY_STEP1,
    CandidateRecordStatus.EMPLOY_STEP2, CandidateRecordStatus.EMPLOY_STEP3
]


async def get_position_list(company_id: str, user_id: str, validated_data: dict, fields: list, base_scope=True) -> list:
    """
    根据搜索条件获取职位列表(包括管理范围筛选)
    @param company_id:
    @param user_id:
    @param validated_data:
    @param fields:
    @param base_scope: 是否基于管理范围
    @return:
    """
    if base_scope:
        permission_data = await svc.manage_scope.hr_manage_scope(company_id, user_id)
        validated_data["permission_ids"] = permission_data.get("position_ids") or []
    participant_ids = validated_data.get("participant_ids")
    if participant_ids:
        position_ids = []
        p_id2position_ids = await PositionParticipantService.get_position_ids_by_participants(
            company_id, participant_ids=participant_ids
        )
        for _, p_ids in p_id2position_ids.items():
            position_ids.extend(p_ids)
        validated_data["position_ids"] = position_ids

    dep_id = validated_data.get("dep_id")
    dep_ids = validated_data.get("dep_ids")
    # 允许dep_ids由调用方获取
    if dep_id and dep_ids is None:
        dep_ids = await DepartmentService.get_all_dep_ids(company_id, [dep_id])
        validated_data["dep_ids"] = dep_ids

    position_list = await JobPositionSelectService.search_positions(
        company_id, fields, validated_data
    )
    return position_list


def get_stats_params_md5(params: dict, stats_type: int = RecruitStatsType.progress) -> str:
    """
    获取统计报表请求参数md5
    @param params:
    @param stats_type:
    @return:
    """
    participant_ids = params.get('participant_ids', []).sort()
    city_ids = params.get('city_ids', []).sort()
    param_str = "{}{}{}".format(params.get('dep_id'), city_ids, participant_ids)
    if stats_type == RecruitStatsType.progress:
        param_str = "{}{}{}".format(
            param_str, params.get('status'), params.get('filter_full')
        )
    else:
        param_str = "{}{}{}".format(
            param_str, params.get("start_dt"), params.get("end_dt")
        )
        if stats_type == RecruitStatsType.eliminated_reason:
            param_str = "{}{}".format(param_str, params.get("eliminated_status", "all"))
        if stats_type == RecruitStatsType.position_workload:
            param_str = "{}{}{}".format(
                param_str, params.get('status'), params.get('filter_none_workload')
            )
        if stats_type == RecruitStatsType.team_workload:
            param_str = "{}{}".format(
                param_str, params.get('filter_none_workload')
            )
        if stats_type == RecruitStatsType.channel_transfer:
            param_str = "{}{}".format(
                param_str, params.get("filter_forbidden")
            )
    md5_has = md5()
    md5_has.update(param_str.encode(encoding='utf-8'))
    return md5_has.hexdigest()


def get_max_interview_count_by_records(record_list: list) -> int:
    """
    获取最大面试轮次
    @param record_list:
    @return:
    """
    max_interview_count = 1
    for cr in record_list:
        if cr["interview_count"] > 10:
            continue
        if cr["interview_count"] > max_interview_count:
            max_interview_count = cr["interview_count"]

    return max_interview_count


async def get_first_level_dept_list(company_id: str, dep_id: str = None):
    """
    获取企业一级部门相关信息
    @param company_id:
    @param dep_id:
    @return:
    """
    dept_list = await DepartmentService.get_com_list(company_id)
    first_level_dept_list = []
    dep_info = {}
    dep_id2sub_dep_id = {}
    for dep in dept_list:
        _id = uuid2str(dep["id"])
        sup_dep_id = uuid2str(dep["sup_department_id"]) if dep.get("sup_department_id") else None
        if dep_id:
            if _id == uuid2str(dep_id):
                dep_info = {"id": _id, "name": dep["name"]}
            if sup_dep_id and sup_dep_id == uuid2str(dep_id):
                first_level_dept_list.append(
                    {"id": _id, "name": dep["name"]}
                )
        else:
            if dep["level"] == 1:
                first_level_dept_list.append(
                    {"id": _id, "name": dep["name"]}
                )
        dep_id2sub_dep_id[_id] = sup_dep_id
    if not first_level_dept_list:
        first_level_dept_list.append(dep_info)

    def get_child_ids(sub_dep_ids, all_ids):
        for _sub_id in sub_dep_ids:
            sub_ids = dep_id2sub_ids.get(_sub_id)
            if sub_ids:
                all_ids.extend(sub_ids)
                get_child_ids(sub_ids, all_ids)
            else:
                continue

    first_level_dep_ids = [item["id"] for item in first_level_dept_list]
    # 处理各个部门的子部门对应关系
    dep_id2sub_ids = defaultdict(list)
    first_level_id2child_ids = {}
    for dep_id, sup_dep_id in dep_id2sub_dep_id.items():
        if sup_dep_id:
            dep_id2sub_ids.setdefault(sup_dep_id, []).append(dep_id)
    for dep_id in first_level_dep_ids:
        all_children_ids = [dep_id]
        s_dep_ids = dep_id2sub_ids.get(dep_id)
        if s_dep_ids:
            all_children_ids.extend(s_dep_ids)
            get_child_ids(s_dep_ids, all_children_ids)
        first_level_id2child_ids[dep_id] = all_children_ids

    return first_level_dept_list, first_level_id2child_ids


class RecruitProgressBusiness(object):

    def __init__(self, company_id: str, user_id: str):
        self.company_id = uuid2str(company_id)
        self.user_id = uuid2str(user_id)

    async def _position_progress(self, validated_data: dict, fields=None) -> list:
        """
        招聘职位招聘进度
        """
        p_md5 = get_stats_params_md5(validated_data, RecruitStatsType.progress)
        cache_key = RECRUIT_PROGRESS_POSITION[0].format(
            company_id=self.company_id, user_id=self.user_id, params_md5=p_md5
        )
        redis_cli = await redis_db.default_redis
        data = await redis_cli.get(cache_key)
        if data:
            return ujson.loads(data)

        if not fields:
            fields = [
                'id', 'name', 'position_total', 'status', 'dep_name',
                'dep_id', 'job_title_id', 'job_title_name'
            ]

        position_list = await get_position_list(self.company_id, self.user_id, validated_data, fields)
        if not position_list:
            return []
        position_ids = [item["id"]for item in position_list]
        record_sv = CandidateRecordService(self.company_id)
        id2employed_count = await record_sv.employed_map_by_jp_id(
            position_ids
        )
        result = []
        filter_full = validated_data.get("filter_full")  # 是否过滤招满的职位
        for item in position_list:
            employed_count = id2employed_count.get(item["id"]) or 0
            item["employed_count"] = employed_count
            if item["status"] == JobPositionStatus.STOP:
                item["name"] = f'{item["name"]}(停止招聘)'
            if filter_full and employed_count >= item["position_total"]:
                continue
            result.append(item)
        await redis_cli.setex(cache_key, RECRUIT_PROGRESS_POSITION[1], ujson.dumps(result))
        return result

    async def department_progress(self, validated_data: dict):
        """
        用人部门招聘进度
        """
        dep_id = validated_data.get("dep_id")
        first_level_dept_list, first_level_id2child_ids = await get_first_level_dept_list(
            self.company_id, dep_id
        )
        if dep_id:
            dep_ids = [dep_id]
            for _, ids in first_level_id2child_ids.items():
                dep_ids.extend(ids)
            validated_data["dep_ids"] = dep_ids
        ret = []
        position_list = await self._position_progress(validated_data)
        for dep_item in first_level_dept_list:
            employed_count = 0
            position_total = 0

            all_child_ids = first_level_id2child_ids.get(dep_item["id"])
            for p_item in position_list:
                if p_item["dep_id"] in all_child_ids:
                    employed_count += p_item["employed_count"]
                    position_total += p_item["position_total"]
            if position_total > 0:
                dep_item["employed_count"] = employed_count
                dep_item["position_total"] = position_total
                dep_item["to_be_recruit"] = position_total - employed_count if (position_total - employed_count) > 0 else 0
                dep_item["progress_rate"] = f'{to_decimal(employed_count/position_total, 2)*100}%'
                ret.append(dep_item)

        # 处理没有部门和为当前所选部门
        none_dep_employed_count = 0
        none_dep_position_total = 0
        total_employed_count = 0
        total_position_total = 0
        for p_item in position_list:
            # 这个总数包括用人部门就是为所选的筛选部门
            total_employed_count += p_item["employed_count"]
            total_position_total += p_item["position_total"]
            if not p_item["dep_id"]:
                none_dep_employed_count += p_item["employed_count"]
                none_dep_position_total += p_item["position_total"]

        if not dep_id and none_dep_position_total:
            to_be_recruit = none_dep_position_total - none_dep_employed_count
            ret.append(
                {
                    "id": None,
                    "name": "未知部门",
                    "employed_count": none_dep_employed_count,
                    "position_total": none_dep_position_total,
                    "to_be_recruit": to_be_recruit if to_be_recruit > 0 else 0,
                    "progress_rate": f'{to_decimal(none_dep_employed_count/none_dep_position_total, 2)*100}%'
                }
            )
        data = {
            "total_employed_count": total_employed_count,
            "total_position_total": total_position_total,
            "position_count": len(position_list),
            "list": ret
        }
        return data

    async def title_group_progress(self, validated_data):
        """
        岗位类别招聘进度
        """
        position_list = await self._position_progress(validated_data)
        job_title_ids = list(set([item["job_title_id"] for item in position_list if item["job_title_id"]]))
        job_title_id2name = await JobGroupService.get_job_group_by_job_title(
            self.company_id, job_title_ids
        )
        group_name2job_title_ids = defaultdict(list)
        for job_title_id, name in job_title_id2name.items():
            if name:
                group_name2job_title_ids.setdefault(name, []).append(uuid2str(job_title_id))

        ret = []
        all_title_ids = []
        for group_name, title_ids in group_name2job_title_ids.items():
            item = {
                "id": None,
                "name": group_name,
                "employed_count": 0,
                "position_total": 0
            }
            all_title_ids.extend(title_ids)
            for data in position_list:
                if data["job_title_id"] and data["job_title_id"] in title_ids:
                    item["employed_count"] += data["employed_count"]
                    item["position_total"] += data["position_total"]
            if item["position_total"] > 0:
                to_be_recruit = item["position_total"] - item["employed_count"]
                progress_rate = f'{to_decimal(item["employed_count"]/item["position_total"], 2) * 100}%'
                item["to_be_recruit"] = to_be_recruit if to_be_recruit > 0 else 0
                item["progress_rate"] = progress_rate
                ret.append(item)

        total_employed_count = 0
        total_position_total = 0
        none_group_employed_count = 0
        none_group_position_total = 0
        for position in position_list:
            total_employed_count += position["employed_count"]
            total_position_total += position["position_total"]
            if position["job_title_id"]:
                if position["job_title_id"] not in all_title_ids:
                    none_group_employed_count += position["employed_count"]
                    none_group_position_total += position["position_total"]
            else:
                none_group_employed_count += position["employed_count"]
                none_group_position_total += position["position_total"]
        if none_group_position_total:
            to_be_recruit = none_group_position_total - none_group_employed_count
            ret.append(
                {
                    "id": None,
                    "name": "未知岗位类型",
                    "employed_count": none_group_employed_count,
                    "position_total": none_group_position_total,
                    "to_be_recruit": to_be_recruit if to_be_recruit > 0 else 0,
                    "progress_rate": f'{to_decimal(none_group_employed_count/none_group_position_total, 2)*100}%'
                }
            )
        data = {
            "total_employed_count": total_employed_count,
            "total_position_total": total_position_total,
            "position_count": len(position_list),
            "list": ret
        }
        return data

    async def position_progress_chart(self, validated_data: dict):
        """
        职位招聘进度（chart)
        """
        position_list = await self._position_progress(validated_data)
        total_employed_count = 0
        total_position_total = 0
        for position in position_list:
            total_employed_count += position["employed_count"]
            total_position_total += position["position_total"]

        data = {
            "total_employed_count": total_employed_count,
            "total_position_total": total_position_total,
            "position_count": len(position_list),
            "list": position_list
        }

        return data

    @staticmethod
    def _get_count(position_id2status_item, jp_id, status):
        """
        """
        jp_res = position_id2status_item.get(jp_id)
        if not jp_res:
            return 0
        return jp_res.get(status) or 0

    async def position_progress_sheet(self, validated_data):
        """
        职位招聘进度（sheet)
        """
        p_md5 = get_stats_params_md5(validated_data, RecruitStatsType.progress)
        cache_key = RECRUIT_PROGRESS_POSITION_SHEET[0].format(
            company_id=self.company_id, user_id=self.user_id, params_md5=p_md5
        )
        redis_cli = await redis_db.default_redis
        data = await redis_cli.get(cache_key)
        if data:
            return ujson.loads(data)

        fields = [
            'id', 'name', 'position_total', 'status', 'dep_name',
            'emergency_level', 'start_dt', 'deadline'
        ]
        position_list = await get_position_list(self.company_id, self.user_id, validated_data, fields)
        if not position_list:
            return {}
        position_ids = [item["id"] for item in position_list]
        candidate_records, position_id2participants = await gather(
            CandidateRecordService.get_candidate_records_by_positions(
                self.company_id, position_ids, ["id", "interview_count", 'status', 'job_position_id']
            ),
            PositionParticipantService.get_participant_by_position_ids(position_ids, ["name"])
        )
        max_interview_count = 0
        position_id2status_item = defaultdict(dict)
        position_id2interview_count_item = defaultdict(dict)
        for record in candidate_records:
            interview_count = record["interview_count"] or 0
            jp_id = uuid2str(record["job_position_id"])
            status = record["status"]
            if interview_count > max_interview_count:
                max_interview_count = interview_count
            if status in [
                CandidateRecordStatus.INTERVIEW_STEP1,
                CandidateRecordStatus.INTERVIEW_STEP3,
                CandidateRecordStatus.INTERVIEW_STEP4
            ]:
                position_id2interview_count_item[jp_id].setdefault(
                    interview_count, dict()
                ).setdefault(status, []).append(record)
            position_id2status_item[jp_id].setdefault(status, []).append(record)

        for jp_id, status_map in position_id2status_item.items():
            for k, v in status_map.items():
                status_map[k] = len(v)

        for jp_id, count_map in position_id2interview_count_item.items():
            for _, count_res in count_map.items():
                for k, v in count_res.items():
                    count_res[k] = len(v)
        ret = []
        filter_full = validated_data.get("filter_full")  # 是否过滤招满的职位
        for position in position_list:
            jp_id = position["id"]
            position_total = position["position_total"]
            name = '{}(停止招聘)'.format(position["name"]) if position["status"] == JobPositionStatus.STOP else position["name"]
            employed = self._get_count(
                position_id2status_item, jp_id, CandidateRecordStatus.EMPLOY_STEP4
            )
            if filter_full and employed >= position_total:
                continue
            participants = position_id2participants.get(jp_id) or []
            hr_participants = "、".join([participant["name"] for participant in participants])
            position.update(
                {
                    "preliminary_screen_passed": self._get_count(
                        position_id2status_item, jp_id, CandidateRecordStatus.PRIMARY_STEP2
                    ),
                    "proposed_employment": self._get_count(
                        position_id2status_item, jp_id, CandidateRecordStatus.EMPLOY_STEP1
                    ),
                    "offer_issued": self._get_count(
                        position_id2status_item, jp_id, CandidateRecordStatus.EMPLOY_STEP2
                    ),
                    "to_be_employed": self._get_count(
                        position_id2status_item, jp_id, CandidateRecordStatus.EMPLOY_STEP3
                    ),
                    "employed_count": employed,
                    "start_dt": position["start_dt"].strftime('%Y-%m-%d') if position["start_dt"] else None,
                    "deadline": position["deadline"].strftime('%Y-%m-%d') if position["deadline"] else None,
                    "name": name,
                    "emergency_level": JobPositionEmergencyLevel.attrs_.get(position["emergency_level"]) or '',
                    "to_bo_recruit": position_total - employed if (position_total - employed) > 0 else 0,
                    "progress_rate": f'{to_decimal(employed / position_total, 2) * 100}%',
                    "hr_participants": hr_participants
                }
            )
            jp_interview_count_map = position_id2interview_count_item.get(jp_id) or dict()
            for interview_count in range(1, max_interview_count + 1):
                count_map = jp_interview_count_map.get(interview_count) or dict()
                position['interview_arranged_{}'.format(interview_count)] = count_map.get(
                    CandidateRecordStatus.INTERVIEW_STEP1
                ) or 0
                position['interview_passed_{}'.format(interview_count)] = count_map.get(
                    CandidateRecordStatus.INTERVIEW_STEP3
                ) or 0

            ret.append(position)
        data = {"max_interview_count": max_interview_count, "list": ret}
        await redis_cli.setex(cache_key, RECRUIT_PROGRESS_POSITION_SHEET[1], ujson.dumps(data))

        return data


class RecruitTransferBusiness(object):

    def __init__(self, company_id: str, user_id: str):
        self.company_id = company_id
        self.user_id = user_id

    @staticmethod
    def _get_status_reverse_map(max_interview_count):
        """
        {
         30: [8, 30],
         31: [8, 30, 31],
         32: [8, 30, 31, 32],
         40: [8, 30, 31, 32, 40],
         41: [8, 30, 31, 32, 40, 41],
         42: [8, 30, 31, 32, 40, 41, 42],
         43: [8, 30, 31, 32, 40, 41, 42, 43],
         50: [8, 30, 31, 32, 40, 41, 42, 43, 50],
         51: [8, 30, 31, 32, 40, 41, 42, 43, 50, 51],
         52: [8, 30, 31, 32, 40, 41, 42, 43, 50, 51, 52],
         53: [8, 30, 31, 32, 40, 41, 42, 43, 50, 51, 52, 53],
         54: [8, 30, 31, 32, 40, 41, 42, 43, 50, 51, 52, 53, 54]
         }
        """
        interview_statuses = []

        for interview_count in range(1, max_interview_count + 1):
            for status in [
                CandidateRecordStatus.INTERVIEW_STEP1,
                CandidateRecordStatus.INTERVIEW_STEP2,
                CandidateRecordStatus.INTERVIEW_STEP3
            ]:
                interview_statuses.append((interview_count, status))

        ret = dict()
        all_statuses = [
                           CandidateRecordStatus.PRIMARY_STEP1, CandidateRecordStatus.PRIMARY_STEP2,
                       ] + interview_statuses + [
                           CandidateRecordStatus.EMPLOY_STEP1, CandidateRecordStatus.EMPLOY_STEP2,
                           CandidateRecordStatus.EMPLOY_STEP3, CandidateRecordStatus.EMPLOY_STEP4,
                       ]
        for index, status in enumerate(all_statuses):
            ret[status] = all_statuses[:index + 1]
        return ret

    async def _cal_record_data(self, validated_data: dict) -> dict:
        """
        根据搜搜条件查询符合条件的应聘记录及相关信息
        @param validated_data:
        @return:
        """
        redis_cli = await redis_db.default_redis
        p_md5 = get_stats_params_md5(validated_data, RecruitStatsType.channel_transfer)
        redis_key = RECRUIT_TRANSFER_STATS[0].format(
            company_id=self.company_id, user_id=self.user_id, params_md5=p_md5
        )
        data = await redis_cli.get(redis_key)
        if data:
            return ujson.loads(data)

        position_list = await get_position_list(
            self.company_id, self.user_id, validated_data, ["id", "name", "dep_name"]
        )
        if not position_list:
            return {}

        position_ids = [item["id"] for item in position_list]
        record_fields = ["id", "interview_count", 'status', 'job_position_id', 'recruitment_channel_id']
        recruiting_total = 0
        record_ids = []
        candidate_records = await CandidateRecordService.get_candidate_records_by_positions(
            self.company_id, position_ids, record_fields, **validated_data
        )
        for candidate in candidate_records:
            record_ids.append(candidate["id"])
            if candidate["status"] in RECRUITING_STATUS:
                recruiting_total += 1

        offer_records = await OfferRecordQueryService.get_offer_records_by_cdr_ids(
            self.company_id, record_ids, ["candidate_record_id"]
        )
        interviews = await InterviewQueryService.get_interviews_by_cdr_ids(
            self.company_id, record_ids, ['is_sign', 'interview_way', 'candidate_record_id']
        )
        max_interview_count = get_max_interview_count_by_records(candidate_records)
        data = {
            "position_list": position_list,
            "total": len(candidate_records),
            "max_interview_count": max_interview_count,
            "r_offer_list": offer_records,
            "r_interview_list": interviews,
            "candidate_records": candidate_records,
            "recruiting_total": recruiting_total
        }
        await redis_cli.setex(redis_key, RECRUIT_TRANSFER_STATS[1], ujson.dumps(data))

        return data

    def _handle_record_data(
            self, max_interview_count: int, candidate_records: list, r_offer_list: list, r_interview_list: list
    ) -> dict:
        """
        处理应聘记录的数据
        @param max_interview_count:
        @param candidate_records:
        @param r_offer_list: 应聘记录相关的offer列表
        @param r_interview_list: 应聘记录相关的面试列表
        @return:
        """
        record_id2status_list = defaultdict(list)
        position_id2status_list = defaultdict(list)
        position_id2record_ids = defaultdict(list)
        channel_id2status_list = defaultdict(list)
        channel_id2record_ids = defaultdict(list)
        exist_offer_record_ids = [offer["candidate_record_id"] for offer in r_offer_list]
        status2status_lines = self._get_status_reverse_map(max_interview_count)
        record_id2interview = {interview["candidate_record_id"]: interview for interview in r_interview_list}

        for record in candidate_records:
            record_id = record["id"]
            status = record["status"]
            position_id = record["job_position_id"]
            channel_id = record["recruitment_channel_id"]
            if status == CandidateRecordStatus.FORM_CREATE:  # 状态不对的应聘记录跳过
                continue
            if status == CandidateRecordStatus.EMPLOY_STEP4:  # 放弃录用状态
                if record_id in exist_offer_record_ids:  # 有offer记录
                    status_key = CandidateRecordStatus.EMPLOY_STEP2
                else:  # 没有offer记录
                    status_key = CandidateRecordStatus.EMPLOY_STEP1
            elif status == CandidateRecordStatus.PRIMARY_STEP3:  # 初筛淘汰
                status_key = CandidateRecordStatus.PRIMARY_STEP1  # 待初筛
            elif status == CandidateRecordStatus.INTERVIEW_STEP4:  # 面试淘汰
                interview_count = record["interview_count"] or 1
                interview = record_id2interview.get(record_id)
                if interview:  # 有面试轮次且有面试
                    if interview["is_sign"]:  # 已签到->"已面试(第x轮)及之前每个状态"
                        status_key = (interview_count, CandidateRecordStatus.INTERVIEW_STEP2)
                    else:  # 没有签到->"已安排面试(第x轮)及之前每个状态"
                        status_key = (interview_count, CandidateRecordStatus.INTERVIEW_STEP1)
                else:  # 有面试轮次但是没有面试(算未签到)
                    status_key = (interview_count, CandidateRecordStatus.INTERVIEW_STEP1)
            else:
                if status in [
                    CandidateRecordStatus.INTERVIEW_STEP1,
                    CandidateRecordStatus.INTERVIEW_STEP2,
                    CandidateRecordStatus.INTERVIEW_STEP3
                ]:
                    interview_count = record["interview_count"] or 1
                    status_key = (interview_count, status)
                else:
                    status_key = status  # 当前状态以及之前每个状态

            record_id2status_list[record_id] = status2status_lines[status_key]
            position_id2status_list.setdefault(position_id, []).extend(status2status_lines[status_key])
            position_id2record_ids.setdefault(position_id, []).append(record_id)
            if channel_id:
                channel_id2status_list.setdefault(channel_id, []).extend(status2status_lines[status_key])
                channel_id2record_ids.setdefault(channel_id, []).append(record_id)
        data = {
            "record_id2status_list": record_id2status_list,
            "position_id2status_list": position_id2status_list,
            "position_id2record_ids": position_id2record_ids,
            "channel_id2status_list": channel_id2status_list,
            "channel_id2record_ids": channel_id2record_ids
        }

        return data

    @staticmethod
    def default_candidate_transfer_chart():
        status_list = [
            CandidateRecordStatus.PRIMARY_STEP2, CandidateRecordStatus.INTERVIEW_STEP3,
            CandidateRecordStatus.EMPLOY_STEP2, CandidateRecordStatus.EMPLOY_STEP4
        ]
        default_item = {"num": 0, "name": "新增候选人", "relative_rate": 0, "absolute_rate": 0}
        ret = [default_item]
        for status in status_list:
            item = default_item
            name = f'{CandidateRecordStatus.attrs_[status]}(第1轮)' \
                if status == CandidateRecordStatus.INTERVIEW_STEP3 \
                else CandidateRecordStatus.attrs_[status]
            item["name"] = name
            ret.append(item)

        return ret

    @staticmethod
    def get_all_transfer_status(max_interview_count, detail_sheet=False):
        """
        获取转换率展示的状态
        @param max_interview_count:
        @param detail_sheet: 是否是详细sheet
        @return:
        """
        interview_status_list = [CandidateRecordStatus.INTERVIEW_STEP3]
        employed_status_list = [
            CandidateRecordStatus.EMPLOY_STEP2, CandidateRecordStatus.EMPLOY_STEP4
        ]
        if detail_sheet:
            interview_status_list = [
                CandidateRecordStatus.INTERVIEW_STEP1,
                CandidateRecordStatus.INTERVIEW_STEP2,
                CandidateRecordStatus.INTERVIEW_STEP3
            ]
            employed_status_list = [
                CandidateRecordStatus.EMPLOY_STEP1,
                CandidateRecordStatus.EMPLOY_STEP2,
                CandidateRecordStatus.EMPLOY_STEP3,
                CandidateRecordStatus.EMPLOY_STEP4
            ]
        all_status = [CandidateRecordStatus.PRIMARY_STEP2]
        for interview_count in range(1, max_interview_count + 1):
            for interview_status in interview_status_list:
                all_status.append((interview_count, interview_status))
        all_status.extend(employed_status_list)

        return all_status

    async def candidate_transfer_chart(self, validated_data: dict):
        """
        新增候选人转换率chart报表
        @param validated_data:
        @return:
        """
        null_data = self.default_candidate_transfer_chart()
        record_data = await self._cal_record_data(validated_data)
        if not record_data or not record_data.get("total"):
            return {"series": null_data, "recruiting_total": 0, "total_rate": 0}

        max_interview_count = record_data.get("max_interview_count")
        handled_record_data = self._handle_record_data(
            max_interview_count, record_data.get("candidate_records"),
            record_data.get("r_offer_list"), record_data.get('r_interview_list')
        )
        record_id2status_list = handled_record_data.get("record_id2status_list")
        all_status_list = []
        for _, status_list in record_id2status_list.items():
            all_status_list.extend(status_list)
        status2total = Counter(all_status_list)

        stats_status_list = self.get_all_transfer_status(max_interview_count)
        previous_count = record_data.get("total")
        data_list = [
            {"num": record_data.get("total"), "name": "新增候选人", "relative_rate": 100, "absolute_rate": 100}
        ]
        employed_total = status2total.get(CandidateRecordStatus.EMPLOY_STEP4, 0)
        for status in stats_status_list:
            name = CandidateRecordStatus.attrs_[status] if isinstance(status, int) else \
                f'{CandidateRecordStatus.attrs_[status[1]]}(第{status[0]}轮)'
            status_total = status2total.get(status) or 0
            if status_total == 0:
                relative_rate, absolute_rate = '0', '0'
            else:
                relative_rate = f'{to_decimal(status_total/previous_count, 1)*100}'
                absolute_rate = f'{to_decimal(status_total/record_data.get("total"), 1)*100}'
            data_list.append(
                {
                    "num": status_total,
                    "name": name,
                    "relative_rate": relative_rate,
                    "absolute_rate": absolute_rate
                }
            )
            previous_count = status_total
        result = {
            "series": data_list,
            "recruiting_total": record_data["recruiting_total"],
            "total_rate": f'{to_decimal(employed_total/record_data["total"], 1)*100}'
        }
        return result

    async def candidate_transfer_sheet(self, validated_data: dict):
        """
        新增候选人转化率sheet报表
        @param validated_data:
        @return:
        """
        record_data = await self._cal_record_data(validated_data)
        max_interview_count = record_data.get("max_interview_count") or 1
        stats_status_list = self.get_all_transfer_status(max_interview_count, detail_sheet=True)
        res = {"max_interview_count": max_interview_count, "list": []}
        if not record_data:
            return res
        ret = []
        position_list = record_data.get("position_list")
        handled_record_data = self._handle_record_data(
            max_interview_count, record_data.get("candidate_records"),
            record_data.get("r_offer_list"), record_data.get('r_interview_list')
        )
        position_id2status_list = handled_record_data.get("position_id2status_list")
        position_id2record_ids = handled_record_data.get("position_id2record_ids")
        for position in position_list:
            position_id = position["id"]
            status_list = position_id2status_list.get(position_id)
            if not status_list:
                continue
            new_add = len(position_id2record_ids.get(position_id, []))
            previous_count = new_add
            previous_key = "new_add"
            status2total = Counter(status_list)
            for status in stats_status_list:
                if isinstance(status, int):
                    status_key = STATUS_KEY_MAP[status]
                else:
                    status_key = f'{STATUS_KEY_MAP[status[1]]}_{status[0]}'
                status_total = status2total.get(status) or 0
                absolute_rate = f'{to_decimal(status_total/new_add, 2) * 100}%' if status_total != 0 else '-'
                relative_rate = f'{to_decimal(status_total/previous_count, 2)*100}%' if status_total != 0 else '-'
                position.update(
                    {
                        status_key: status_total,
                        f'ab_{status_key}_rate': absolute_rate,
                        f're_{previous_key}_{status_key}_rate': relative_rate,
                    }
                )
                previous_count = status_total
                previous_key = status_key

            position["new_add"] = len(position_id2record_ids.get(position_id, []))
            ret.append(position)
        res["list"] = ret

        return res

    @staticmethod
    def _cal_channel_relative_rate(data_list: list) -> list:
        """
        计算招聘渠道相同阶段间的占比
        @param data_list:
        @return:
        """
        for data in data_list:
            total = data.get("total") or 0
            primary_passed = data.get(STATUS_KEY_MAP[CandidateRecordStatus.PRIMARY_STEP2]) or 0
            total2primary_passed_rate = f'{to_decimal(primary_passed/total, 1) * 100}%' if \
                total else '-'
            interview_passed = data.get(
                f'{STATUS_KEY_MAP[CandidateRecordStatus.INTERVIEW_STEP3]}'
            ) or 0
            primary_passed2interview_passed_rate = f'{to_decimal(interview_passed/primary_passed, 1) * 100}%' if \
                primary_passed else '-'
            total2interview_passed_rate = f'{to_decimal(interview_passed/total, 1) * 100}%' if total else '-'
            offer_issued = data.get(STATUS_KEY_MAP[CandidateRecordStatus.EMPLOY_STEP2]) or 0
            interview_passed2offer_issued_rate = f'{to_decimal(offer_issued/interview_passed, 1) * 100}%' if \
                interview_passed else '-'
            total2offer_issued_rate = f'{to_decimal(offer_issued/total, 1) * 100}%' if total else '-'
            employed = data.get(STATUS_KEY_MAP[CandidateRecordStatus.EMPLOY_STEP3]) or 0
            offer_issued2employed_rate = f'{to_decimal(employed/offer_issued, 1) * 100}%' if \
                offer_issued else '-'
            total2employed_rate = f'{to_decimal(employed / total, 1) * 100}%' if total else '-'
            data.update(
                {
                    "total2primary_passed_rate": total2primary_passed_rate,
                    "primary_passed2interview_passed_rate": primary_passed2interview_passed_rate,
                    "total2interview_passed_rate": total2interview_passed_rate,
                    "interview_passed2offer_issued_rate": interview_passed2offer_issued_rate,
                    "total2offer_issued_rate": total2offer_issued_rate,
                    "offer_issued2employed_rate": offer_issued2employed_rate,
                    "total2employed_rate": total2employed_rate,
                }
            )
        return data_list

    async def channel_transfer_data(self, validated_data: dict) -> dict:
        """
        招聘渠道候选人转化率报表
        @param validated_data:
        @return:
        """
        record_data = await self._cal_record_data(validated_data)
        max_interview_count = record_data.get("max_interview_count") or 1
        stats_status_list = self.get_all_transfer_status(max_interview_count)
        if not record_data:
            return {"recruiting_total": 0, "list": []}

        ret_list = []
        handled_record_data = self._handle_record_data(
            max_interview_count, record_data.get("candidate_records"),
            record_data.get("r_offer_list"), record_data.get('r_interview_list')
        )
        channel_id2status_list = handled_record_data.get("channel_id2status_list")
        channel_id2record_ids = handled_record_data.get("channel_id2record_ids")
        for channel_id, status_list in channel_id2status_list.items():
            total_candidates = len(channel_id2record_ids.get(channel_id, []))
            item = {"id": channel_id, "total": total_candidates}
            status2total = Counter(status_list)
            for status in stats_status_list:
                status_total = status2total.get(status) or 0
                if isinstance(status, int):
                    status_key = STATUS_KEY_MAP[status]
                    item[status_key] = status_total
                else:
                    status_key = f'{STATUS_KEY_MAP[status[1]]}'
                    # 面试通过只算最大轮次通过的候选人数
                    if status[0] == max_interview_count:
                        item[status_key] = status_total
            ret_list.append(item)

        filter_forbidden = validated_data.get("filter_forbidden")
        channel_list = await RecruitmentChannelService.get_channel_list(
            self.company_id, ["id", "name"], filter_forbidden=filter_forbidden
        )
        channel_id2name = {item["id"]: item["name"] for item in channel_list}
        data = []
        for ret in ret_list:
            name = channel_id2name.get(ret["id"])
            if name:
                ret["name"] = name
                data.append(ret)
        data = self._cal_channel_relative_rate(data)

        return {"recruiting_total": record_data.get("recruiting_total"), "list": data}

    async def channel_transfer_export(self):
        pass


class EliminatedReasonStatsBusiness(object):

    def __init__(self, company_id: str, user_id: str):
        self.company_id = uuid2str(company_id)
        self.user_id = uuid2str(user_id)

    @staticmethod
    def _cal_eliminated_rate(data_map, eliminated_reason_map):
        """
        计算
        @param data_map: {原因ID: 数量}
        @param eliminated_reason_map:
        @return:
        """

        ret = []
        if data_map:
            all_count = reduce(add, data_map.values())
            for reason_id, count in data_map.items():
                percent = '{}%'.format(str(to_decimal(count / all_count * 100, 1)))
                ret.append(dict(
                    reason_id=reason_id,
                    reason_name=eliminated_reason_map.get(reason_id),
                    count=count,
                    percent=percent,
                ))
            ret = sorted(ret, key=lambda item: item["count"], reverse=True)
            sum_count = 0
            for data in ret:
                sum_count += data["count"]
                sum_percent_num = str(to_decimal(sum_count / all_count * 100, 1))
                sum_percent_str = '{}%'.format(sum_percent_num)
                data["sum_percent_num"] = sum_percent_num
                data["sum_percent_str"] = sum_percent_str

        return ret

    async def _eliminated_reason_map(self) -> dict:
        """
        获取企业淘汰原因信息
        @return:
        """
        reason_list = await EliminatedReasonService.get_select_data(
            self.company_id, ["id", "reason"], include_deleted=True
        )
        id2name = {item["id"]: item["reason"] for item in reason_list}
        id2name[None] = "未知原因"
        return id2name

    async def eliminated_reason_stats_data(self, validated_data: dict):
        """
        淘汰原因统计数据业务
        @param validated_data:
        @return:
        """
        redis_key = ELIMINATED_REASON_STATS[0].format(
            company_id=self.company_id, user_id=self.user_id,
            params_md5=get_stats_params_md5(validated_data, RecruitStatsType.eliminated_reason)
        )
        redis_cli = await redis_db.default_redis
        data = await redis_cli.get(redis_key)
        if data:
            return ujson.loads(data)
        position_list = await get_position_list(
            self.company_id, self.user_id, validated_data, ["id"]
        )
        position_ids = [position["id"] for position in position_list]
        record_fields = ["id", "status", "eliminated_reason_id"]
        eliminated_records, reason_id2name = await gather(
            CandidateRecordService.get_eliminated_records_by_positions(
                self.company_id, position_ids, record_fields, **validated_data
            ),
            self._eliminated_reason_map()
        )
        status2eliminated_reason = defaultdict(dict)
        for record in eliminated_records:
            reason_id = uuid2str(record["eliminated_reason_id"])
            status2eliminated_reason[record["status"]].setdefault(reason_id, 0)
            status2eliminated_reason[record["status"]][reason_id] += 1

        primary_eliminated_data = self._cal_eliminated_rate(
            status2eliminated_reason.get(CandidateRecordStatus.PRIMARY_STEP3), reason_id2name
        )
        interview_eliminated_data = self._cal_eliminated_rate(
            status2eliminated_reason.get(CandidateRecordStatus.INTERVIEW_STEP4), reason_id2name
        )
        employed_eliminated_data = self._cal_eliminated_rate(
            status2eliminated_reason.get(CandidateRecordStatus.EMPLOY_STEP5), reason_id2name
        )
        data = {
            "primary_eliminated_data": primary_eliminated_data,
            "interview_eliminated_data": interview_eliminated_data,
            "employed_eliminated_data": employed_eliminated_data
        }
        await redis_cli.setex(redis_key, ELIMINATED_REASON_STATS[1], ujson.dumps(data))

        return data

    @classmethod
    async def eliminated_reason_stats_export(cls, validated_data: dict):
        pass


class PositionWorkLoadStatsBusiness(object):

    def __init__(self, company_id, user_id):
        self.company_id = uuid2str(company_id)
        self.user_id = uuid2str(user_id)

    @staticmethod
    def _resume_work_load_map(candidate_records: list, validated_data: dict) -> dict:
        """
        时间范围导入简历的工作量（按添加时间)
        时间范围内确认入职的工作量（按入职时间）
        @param candidate_records:
        @param validated_data:
        @return:
        """
        start_dt = get_date_min_datetime(validated_data.get("start_dt"))
        end_dt = get_date_max_datetime(validated_data.get("end_dt"))
        position_id2employed_list = defaultdict(list)
        position_id2record_list = defaultdict(list)

        for record in candidate_records:
            position_id = record["job_position_id"]
            status = record["status"]
            entry_dt = record["entry_dt"]
            add_dt = record["add_dt"]
            if start_dt <= add_dt <= end_dt:
                position_id2record_list.setdefault(position_id, []).append(
                    record["id"]
                )
            if status == CandidateRecordStatus.EMPLOY_STEP4 and entry_dt:
                entry_dt = get_date_min_datetime(entry_dt)
                if start_dt <= entry_dt <= end_dt:
                    position_id2employed_list.setdefault(position_id, []).append(
                        record["id"]
                    )

        p_id2resume_count = {}
        p_id2employed_count = {}
        for position_id, record_list in position_id2record_list.items():
            p_id2resume_count[position_id] = len(record_list)
        for position_id, employed_list in position_id2employed_list.items():
            p_id2employed_count[position_id] = len(employed_list)
        data = {
            "p_id2resume_count": p_id2resume_count,
            "p_id2employed_count": p_id2employed_count
        }
        return data

    async def _offered_work_load_map(self, record_ids: list, validated_data: dict) -> dict:
        """
        时间范围内发送offer的工作量（发送时间）
        @param record_ids:
        @param validated_data:
        @return:
        """
        position_id2offer_list = defaultdict(set)
        offer_records = await OfferRecordQueryService.get_offer_records_by_cdr_ids(
            self.company_id, record_ids, ["candidate_record_id", "job_position_id"], **validated_data
        )
        for record in offer_records:
            position_id = record["job_position_id"]
            candidate_record_id = record["candidate_record_id"]
            position_id2offer_list.setdefault(position_id, set()).add(candidate_record_id)
        position_id2offer_count = {}
        for p_id, offer_list in position_id2offer_list.items():
            position_id2offer_count[p_id] = len(offer_list)

        return position_id2offer_count

    async def _interview_work_load_map(self, record_ids: list, validated_data: dict):
        """
        时间范围内跟进面试的工作量（面试时间）
        @param record_ids:
        @param validated_data:
        @return:
        """
        interviews = await InterviewQueryService.get_interviews_by_cdr_ids(
            self.company_id, record_ids, ["candidate_record_id", "count", "is_sign"], **validated_data
        )
        max_interview_count = 1
        interview_count2all_records = defaultdict(list)
        interview_count2signed_records = defaultdict(list)
        for interview in interviews:
            count = interview["count"]
            candidate_record_id = interview["candidate_record_id"]
            is_sign = interview["is_sign"]
            if count > max_interview_count:
                max_interview_count = count
            interview_count2all_records.setdefault(count, []).append(
                candidate_record_id
            )
            if is_sign:
                interview_count2signed_records.setdefault(count, []).append(
                    candidate_record_id
                )
        interview_count2all_record_items = {}
        interview_count2signed_record_items = {}
        for count, record_list in interview_count2all_records.items():
            interview_count2all_record_items[count] = Counter(record_list)

        for count, record_list in interview_count2signed_records.items():
            interview_count2signed_record_items[count] = Counter(record_list)

        data = {
            "max_interview_count": max_interview_count,
            "interview_count2all_record_items": interview_count2all_record_items,
            "interview_count2signed_record_items": interview_count2signed_record_items
        }

        return data

    async def _screen_work_load_map(self, position_ids: list, validated_data: dict):
        """
        时间范围内筛选简历的工作量（操作时间）
        @param position_ids:
        @param validated_data:
        @return:
        """
        log_fields = ["job_position_id", "candidate_record_id", "status_before", "status_after"]
        log_records = await CandidateStatusLog.query_log_by_positions(
            self.company_id, position_ids, log_fields, **validated_data
        )
        p_id2passed_records = defaultdict(set)
        p_id2eliminated_records = defaultdict(set)
        p_id2screen_records = defaultdict(set)
        for record in log_records:
            status_after = record["status_after"]
            p_id = record["job_position_id"]
            record_id = record["candidate_record_id"]
            if status_after in [
                CandidateRecordStatus.PRIMARY_STEP2,
                CandidateRecordStatus.PRIMARY_STEP3
            ]:
                p_id2screen_records.setdefault(p_id, set()).add(record_id)
                if status_after == CandidateRecordStatus.PRIMARY_STEP2:
                    p_id2passed_records.setdefault(p_id, set()).add(record_id)
                if status_after == CandidateRecordStatus.PRIMARY_STEP3:
                    p_id2eliminated_records.setdefault(p_id, set()).add(record_id)
        p_id2screen_total = {}
        p_id2passed_total = {}
        p_id2eliminated_total = {}
        for p_id, record_list in p_id2screen_records.items():
            p_id2screen_total[p_id] = len(record_list)
        for p_id, record_list in p_id2passed_records.items():
            p_id2passed_total[p_id] = len(record_list)
        for p_id, record_list in p_id2eliminated_records.items():
            p_id2eliminated_total[p_id] = len(record_list)
        data = {
            "p_id2screen_total": p_id2screen_total,
            "p_id2passed_total": p_id2passed_total,
            "p_id2eliminated_total": p_id2eliminated_total
        }
        return data

    @staticmethod
    def _handle_workload_rate(data_list: list, max_interview_count: int) -> list:
        """
        处理招聘职位工作量占比
        @param data_list:
        @return:
        """
        record_sum = 0
        screen_sum = 0
        screen_passed_sum = 0
        screen_eliminated_sum = 0
        offered_sum = 0
        employed_sum = 0
        follow_interview_sum = 0
        signed_interview_sum = 0
        follow_interview_count2total = {
            f"follow_interview{count}_total": 0 for count in range(1, max_interview_count + 1)
        }
        signed_interview_count2total = {
            f"signed_interview{count}_total": 0 for count in range(1, max_interview_count + 1)
        }
        for item in data_list:
            record_sum += item.get("record_total")
            screen_sum += item.get("screen_total")
            screen_passed_sum += item.get("screen_passed_total")
            screen_eliminated_sum += item.get("screen_eliminated_total")
            offered_sum += item.get("offered_total")
            employed_sum += item.get("employed_total")
            follow_interview_sum += item.get("follow_interview_total")
            signed_interview_sum += item.get("signed_interview_total")
            for count in range(1, max_interview_count+1):
                follow_interview_count2total[f"follow_interview{count}_total"] += item[f"follow_interview{count}_count"]
                signed_interview_count2total[f"signed_interview{count}_total"] += item[f"signed_interview{count}_count"]
        for item in data_list:
            record_rate = '{}%'.format(str(to_decimal(item.get("record_total") / record_sum * 100, 1))) if record_sum else "-"
            screen_rate = '{}%'.format(str(to_decimal(item.get("screen_total") / screen_sum * 100, 1))) if screen_sum else "-"
            screen_passed_rate = '{}%'.format(str(to_decimal(item.get("screen_passed_total") / screen_passed_sum * 100, 1))) if screen_passed_sum else "-"
            screen_eliminated_rate = '{}%'.format(str(to_decimal(item.get("screen_eliminated_total") / screen_eliminated_sum * 100, 1))) if screen_eliminated_sum else "-"
            offered_rate = '{}%'.format(str(to_decimal(item.get("offered_total") / offered_sum * 100, 1))) if offered_sum else "-"
            employed_rate = '{}%'.format(str(to_decimal(item.get("employed_total") / employed_sum * 100, 1))) if employed_sum else "-"
            follow_interview_rate = '{}%'.format(str(to_decimal(item.get("follow_interview_total") / follow_interview_sum * 100, 1))) if follow_interview_sum else "-"
            signed_interview_rate = '{}%'.format(str(to_decimal(item.get("signed_interview_total") / signed_interview_sum * 100, 1))) if signed_interview_sum else "-"
            for count in range(1, max_interview_count+1):
                follow_count_total = follow_interview_count2total.get(f"follow_interview{count}_total")
                signed_count_total = signed_interview_count2total.get(f"signed_interview{count}_total")
                follow_interview_count_rate = '{}%'.format(str(to_decimal(item.get(f"follow_interview{count}_count") / follow_count_total * 100, 1))) if follow_count_total else "-"
                signed_interview_count_rate = '{}%'.format(str(to_decimal(item.get(f"signed_interview{count}_count") / signed_count_total * 100, 1))) if signed_count_total else "-"
                item.update(
                    {
                        f"follow_interview{count}_rate": follow_interview_count_rate,
                        f"signed_interview{count}_rate": signed_interview_count_rate
                    }
                )
            item.update(
                {
                    "record_rate": record_rate,
                    "screen_rate": screen_rate,
                    "screen_passed_rate": screen_passed_rate,
                    "screen_eliminated_rate": screen_eliminated_rate,
                    "offered_rate": offered_rate,
                    "employed_rate": employed_rate,
                    "follow_interview_rate": follow_interview_rate,
                    "signed_interview_rate": signed_interview_rate
                }
            )

        return data_list

    async def _position_workload(self, validated_data: dict) -> dict:
        redis_cli = await redis_db.default_redis
        redis_key = POSITION_WORKLOAD_STATS[0].format(
            company_id=self.company_id,
            user_id=self.user_id,
            params_md5=get_stats_params_md5(validated_data, RecruitStatsType.position_workload)
        )
        result = await redis_cli.get(redis_key)
        if result:
            return ujson.loads(result)

        position_fields = ["id", "name", "dep_id", "dep_name"]
        position_list = await get_position_list(
            self.company_id, self.user_id, validated_data, position_fields
        )
        position_ids = [position["id"] for position in position_list]
        if not position_ids:
            return {}
        candidate_records = await CandidateRecordService.get_candidate_records_by_positions(
            self.company_id, position_ids, ["id", "job_position_id", "status", "add_dt", "entry_dt"]
        )
        position_id2record_ids = defaultdict(list)
        for record in candidate_records:
            position_id2record_ids.setdefault(record["job_position_id"], []).append(
                record["id"]
            )
        record_ids = [record["id"] for record in candidate_records]
        resume_map = self._resume_work_load_map(candidate_records, validated_data)
        p_id2offered_total = await self._offered_work_load_map(record_ids, validated_data)
        interview_map = await self._interview_work_load_map(record_ids, validated_data)
        screen_map = await self._screen_work_load_map(position_ids, validated_data)
        p_id2resume_count = resume_map.get("p_id2resume_count")
        p_id2employed_count = resume_map.get("p_id2employed_count")
        p_id2screen_total = screen_map.get("p_id2screen_total")
        p_id2passed_total = screen_map.get("p_id2passed_total")
        p_id2eliminated_total = screen_map.get("p_id2eliminated_total")
        max_interview_count = interview_map.get("max_interview_count")
        interview_count2all_record_items = interview_map.get("interview_count2all_record_items")
        interview_count2signed_record_items = interview_map.get("interview_count2signed_record_items")

        ret = []
        for position in position_list:
            position_id = position["id"]
            record_list = position_id2record_ids.get(position_id, [])
            follow_interview_total = 0
            signed_interview_total = 0
            for count in range(1, max_interview_count+1):
                follow_interview_count = 0
                signed_interview_count = 0
                record_id2follow_interview_count = interview_count2all_record_items.get(count, {})
                record_id2signed_interview_count = interview_count2signed_record_items.get(count, {})
                for record_id in record_list:
                    follow_interview_count += record_id2follow_interview_count.get(record_id, 0)
                    signed_interview_count += record_id2signed_interview_count.get(record_id, 0)
                follow_interview_total += follow_interview_count
                signed_interview_total += signed_interview_count
                position.update(
                    {
                        f"follow_interview{count}_count": follow_interview_count,
                        f"signed_interview{count}_count": signed_interview_count
                    }
                )
            filter_none_workload = validated_data.get("filter_none_workload")
            all_workload = sum(
                [
                    p_id2resume_count.get(position_id, 0),
                    p_id2screen_total.get(position_id, 0),
                    p_id2passed_total.get(position_id, 0),
                    p_id2eliminated_total.get(position_id, 0),
                    p_id2offered_total.get(position_id, 0),
                    p_id2employed_count.get(position_id, 0),
                    follow_interview_total,
                    signed_interview_total
                 ]
            )
            if filter_none_workload and not all_workload:
                continue
            position.update(
                {
                    "record_total": p_id2resume_count.get(position_id, 0),
                    "screen_total": p_id2screen_total.get(position_id, 0),
                    "screen_passed_total": p_id2passed_total.get(position_id, 0),
                    "screen_eliminated_total": p_id2eliminated_total.get(position_id, 0),
                    "offered_total": p_id2offered_total.get(position_id, 0),
                    "employed_total": p_id2employed_count.get(position_id, 0),
                    "follow_interview_total": follow_interview_total,
                    "signed_interview_total": signed_interview_total
                }
            )
            ret.append(position)
        result = {"max_interview_count": max_interview_count, "list": ret}
        await redis_cli.setex(redis_key, POSITION_WORKLOAD_STATS[1], ujson.dumps(result))
        return result

    async def position_workload_data(self, validated_data: dict) -> dict:
        """
        招聘职位维度工作量的数据
        @param validated_data:
        @return:
        """

        data = await self._position_workload(validated_data)
        ret = self._handle_workload_rate(data["list"], data["max_interview_count"])
        data["list"] = ret
        return data

    async def department_workload_data(self, validated_data: dict) -> dict:
        """
        用人部门维度的工作量的数据
        @param validated_data:
        @return:
        """
        dep_id = validated_data.get("dep_id")
        first_level_dept_list, first_level_id2child_ids = await get_first_level_dept_list(
            self.company_id, dep_id
        )
        if dep_id:
            dep_ids = [dep_id]
            for _, ids in first_level_id2child_ids.items():
                dep_ids.extend(ids)
            validated_data["dep_ids"] = dep_ids
        data = await self._position_workload(validated_data)
        position_list = data.get("list")
        max_interview_count = data.get("max_interview_count")

        def _handle_position_list_for_dep(item_dep_id=None) -> dict:
            record_total = 0
            screen_total = 0
            screen_passed_total = 0
            screen_eliminated_total = 0
            offered_total = 0
            employed_total = 0
            follow_interview_total = 0
            signed_interview_total = 0
            follow_interview_count2total = {
                f"follow_interview{count}_count": 0 for count in range(1, max_interview_count + 1)
            }
            signed_interview_count2total = {
                f"signed_interview{count}_count": 0 for count in range(1, max_interview_count + 1)
            }
            for p_item in position_list:
                if item_dep_id:
                    all_child_ids = first_level_id2child_ids.get(item_dep_id)
                    if p_item["dep_id"] in all_child_ids:
                        record_total += p_item["record_total"]
                        screen_total += p_item["screen_total"]
                        screen_passed_total += p_item["screen_passed_total"]
                        screen_eliminated_total += p_item["screen_eliminated_total"]
                        offered_total += p_item["offered_total"]
                        employed_total += p_item["employed_total"]
                        follow_interview_total += p_item["follow_interview_total"]
                        signed_interview_total += p_item["signed_interview_total"]
                        for count in range(1, max_interview_count + 1):
                            follow_count_key = f"follow_interview{count}_count"
                            signed_count_key = f"signed_interview{count}_count"
                            follow_interview_count2total[follow_count_key] += p_item[follow_count_key]
                            signed_interview_count2total[signed_count_key] += p_item[signed_count_key]
                else:
                    if not p_item["dep_id"] or p_item["dep_id"] == dep_id:
                        record_total += p_item["record_total"]
                        screen_total += p_item["screen_total"]
                        screen_passed_total += p_item["screen_passed_total"]
                        screen_eliminated_total += p_item["screen_eliminated_total"]
                        offered_total += p_item["offered_total"]
                        employed_total += p_item["employed_total"]
                        follow_interview_total += p_item["follow_interview_total"]
                        signed_interview_total += p_item["signed_interview_total"]
                        for count in range(1, max_interview_count + 1):
                            follow_count_key = f"follow_interview{count}_count"
                            signed_count_key = f"signed_interview{count}_count"
                            follow_interview_count2total[follow_count_key] += p_item[follow_count_key]
                            signed_interview_count2total[signed_count_key] += p_item[signed_count_key]
            all_workload = sum(
                [
                    record_total, screen_total, screen_passed_total, screen_eliminated_total,
                    offered_total, employed_total, follow_interview_total, signed_interview_total
                ]
            )
            res = {
                    "record_total": record_total,
                    "screen_total": screen_total,
                    "screen_passed_total": screen_passed_total,
                    "screen_eliminated_total": screen_eliminated_total,
                    "offered_total": offered_total,
                    "employed_total": employed_total,
                    "follow_interview_total": follow_interview_total,
                    "signed_interview_total": signed_interview_total
                }
            res.update(
                follow_interview_count2total
            )
            res.update(signed_interview_count2total)
            return res if all_workload else {}

        ret_list = []
        for dep_item in first_level_dept_list:
           workload_data = _handle_position_list_for_dep(dep_item["id"])
           if workload_data:
               dep_item.update(workload_data)
               ret_list.append(dep_item)

        # 处理没有部门和为当前所选部门
        none_dept = {"id": None, "name": "未知部门"}
        workload_data = _handle_position_list_for_dep()
        if workload_data:
            none_dept.update(workload_data)
            ret_list.append(none_dept)
        ret_list = self._handle_workload_rate(ret_list, data["max_interview_count"])
        data["list"] = ret_list

        return data


class TeamWorkLoadStatsBusiness(object):

    def __init__(self, company_id: str, user_id: str):
        self.company_id = uuid2str(company_id)
        self.user_id = uuid2str(user_id)

    async def _get_participants(self, participant_type: int, validated_data: dict) -> list:
        """

        @param participant_type:
        @param validated_data:
        @return:
        """

        if participant_type == ParticipantType.HR:
            if not await validate_permission(
                    self.company_id, self.user_id, "recruitment:workload_stats"
            ):
                user_ids = [self.user_id]
                validated_data["user_ids"] = user_ids
        fields = ["id", "name", "mobile", "participant_refer_status", "participant_refer_id"]
        participants = await RecruitmentTeamService.get_participants(
            self.company_id, participant_type, fields, **validated_data
        )
        names_count_map = defaultdict(int)
        for participant in participants:
            names_count_map[participant["name"]] += 1

        ret = []
        for participant in participants:
            name = participant["name"]
            if names_count_map.get(name, 0) > 1:
                name = '{}({})'.format(name, participant["mobile"])
            if participant["participant_refer_status"]:
                name = '{}（已禁用）'.format(name)
            ret.append({
                'id': participant["id"],
                'participant_refer_id': participant["participant_refer_id"],
                'name': name
            })
        return ret

    async def _other_work_load_map(self, participant_ids: list, validated_data: dict) -> dict:
        """
        跟进的面试及相关入职
        @param participant_ids:
        @param validated_data:
        @return:
        """
        validated_data.pop("participant_ids", [])
        participant_id2position_ids = await PositionParticipantService.get_position_ids_by_participants(
            self.company_id, participant_ids, **validated_data
        )
        position_ids = []
        for _, p_ids in participant_id2position_ids.items():
            position_ids.extend(p_ids)
        position_ids = list(set(position_ids))
        position_id2follow_interviews = defaultdict(list)
        position_id2employed_records = defaultdict(list)
        if position_ids:
            validated_data.pop("position_ids", [])
            follow_interviews = await InterviewQueryService.get_interviews_by_positions(
                self.company_id, position_ids, **validated_data
            )
            for item in follow_interviews:
                position_id2follow_interviews.setdefault(item["job_position_id"], []).append(item["id"])

            employed_records = await CandidateRecordService.get_employed_records_by_positions(
                self.company_id, position_ids, ["id", "job_position_id"], **validated_data
            )
            for item in employed_records:
                position_id2employed_records.setdefault(item["job_position_id"], []).append(item["id"])
        p_id2interview_count = {}
        p_id2employed_count = {}
        for participant_id, position_ids in participant_id2position_ids.items():
            follow_interview_count = 0
            employed_record_count = 0
            for position_id in position_ids:
                follow_interview_count += len(position_id2follow_interviews.get(position_id, []))
                employed_record_count += len(position_id2employed_records.get(position_id, []))
            p_id2interview_count[participant_id] = follow_interview_count
            p_id2employed_count[participant_id] = employed_record_count

        data = {"p_id2employed_count": p_id2employed_count, "p_id2interview_count": p_id2interview_count}

        return data

    async def _resume_work_load_map(self, validated_data: dict) -> dict:
        """
        时间范围导入简历的工作量（按添加时间)
        @param validated_data:
        @return:
        """
        add_by_id2record_list = defaultdict(list)
        add_by_id2resume_count = {}
        candidate_records = await CandidateRecordService.get_candidate_records(
            self.company_id, ["id", "add_by_id"], **validated_data
        )
        for record in candidate_records:
            add_by_id = record["add_by_id"]
            add_by_id2record_list.setdefault(add_by_id, []).append(record["id"])
        for add_by_id, records in add_by_id2record_list.items():
            add_by_id2resume_count[add_by_id] = len(records)

        return add_by_id2resume_count

    async def _offered_work_load_map(self, validated_data: dict) -> dict:
        """
        时间范围内发送offer的工作量（发送时间）
        @param validated_data:
        @return:
        """
        add_by_id2offer_list = defaultdict(set)
        offer_records = await OfferRecordQueryService.get_offer_records(
            self.company_id, ["candidate_record_id", "add_by_id"], **validated_data
        )
        for record in offer_records:
            add_by_id = record["add_by_id"]
            candidate_record_id = record["candidate_record_id"]
            add_by_id2offer_list.setdefault(add_by_id, set()).add(candidate_record_id)
        add_by_id2offer_count = {}
        for add_by_id, offer_list in add_by_id2offer_list.items():
            add_by_id2offer_count[add_by_id] = len(offer_list)

        return add_by_id2offer_count

    async def _arrange_interview_work_load_map(self, validated_data: dict):
        """
        安排面试工作量
        @param validated_data:
        @return:
        """
        interviews = await InterviewQueryService.get_interviews(
            self.company_id, ["id", "add_by_id"], **validated_data
        )
        add_by_id2interview_list = defaultdict(list)
        for record in interviews:
            add_by_id = record["add_by_id"]
            interview_id = record["id"]
            add_by_id2interview_list.setdefault(add_by_id, []).append(interview_id)
        add_by_id2interview_count = {}
        for add_by_id, interviews in add_by_id2interview_list.items():
            add_by_id2interview_count[add_by_id] = len(interviews)

        return add_by_id2interview_count

    async def _screen_work_load_map(self, validated_data: dict) -> dict:
        """
        时间范围内筛选简历的工作量（操作时间）
        @param validated_data:
        @return:
        """
        log_fields = ["add_by_id", "candidate_record_id", "status_before", "status_after"]
        log_records = await CandidateStatusLog.query_logs(
            self.company_id, log_fields, **validated_data
        )
        add_by_id2passed_records = defaultdict(set)
        add_by_id2eliminated_records = defaultdict(set)
        add_by_id2screen_records = defaultdict(set)
        for record in log_records:
            status_after = record["status_after"]
            add_by_id = record["add_by_id"]
            record_id = record["candidate_record_id"]
            if status_after in [
                CandidateRecordStatus.PRIMARY_STEP2,
                CandidateRecordStatus.PRIMARY_STEP3
            ]:
                add_by_id2screen_records.setdefault(add_by_id, set()).add(record_id)
                if status_after == CandidateRecordStatus.PRIMARY_STEP2:
                    add_by_id2passed_records.setdefault(add_by_id, set()).add(record_id)
                if status_after == CandidateRecordStatus.PRIMARY_STEP3:
                    add_by_id2eliminated_records.setdefault(add_by_id, set()).add(record_id)
        add_by_id2screen_total = {}
        add_by_id2passed_total = {}
        add_by_id2eliminated_total = {}
        for add_by_id, record_list in add_by_id2screen_records.items():
            add_by_id2screen_total[add_by_id] = len(record_list)
        for add_by_id, record_list in add_by_id2passed_records.items():
            add_by_id2passed_total[add_by_id] = len(record_list)
        for add_by_id, record_list in add_by_id2eliminated_records.items():
            add_by_id2eliminated_total[add_by_id] = len(record_list)
        data = {
            "add_by_id2screen_total": add_by_id2screen_total,
            "add_by_id2passed_total": add_by_id2passed_total,
            "add_by_id2eliminated_total": add_by_id2eliminated_total
        }
        return data

    @staticmethod
    def _handle_workload_rate(data_list: list) -> list:
        """
        处理招聘职位工作量占比
        @param data_list:
        @return:
        """
        record_sum = 0
        screen_sum = 0
        screen_passed_sum = 0
        screen_eliminated_sum = 0
        offered_sum = 0
        employed_sum = 0
        follow_interview_sum = 0
        arrange_interview_sum = 0
        for item in data_list:
            record_sum += item.get("record_total", 0)
            screen_sum += item.get("screen_total", 0)
            screen_passed_sum += item.get("screen_passed_total", 0)
            screen_eliminated_sum += item.get("screen_eliminated_total", 0)
            offered_sum += item.get("offered_total", 0)
            employed_sum += item.get("employed_total", 0)
            follow_interview_sum += item.get("follow_interview_total", 0)
            arrange_interview_sum += item.get("arrange_interview_sum", 0)
        for item in data_list:
            record_rate = '{}%'.format(
                str(to_decimal(item.get("record_total") / record_sum * 100, 1))) if record_sum else "-"
            screen_rate = '{}%'.format(
                str(to_decimal(item.get("screen_total") / screen_sum * 100, 1))) if screen_sum else "-"
            screen_passed_rate = '{}%'.format(str(
                to_decimal(item.get("screen_passed_total") / screen_passed_sum * 100, 1))) if screen_passed_sum else "-"
            screen_eliminated_rate = '{}%'.format(str(
                to_decimal(item.get("screen_eliminated_total") / screen_eliminated_sum * 100,
                           1))) if screen_eliminated_sum else "-"
            offered_rate = '{}%'.format(
                str(to_decimal(item.get("offered_total") / offered_sum * 100, 1))) if offered_sum else "-"
            employed_rate = '{}%'.format(
                str(to_decimal(item.get("employed_total") / employed_sum * 100, 1))) if employed_sum else "-"
            follow_interview_rate = '{}%'.format(str(
                to_decimal(item.get("follow_interview_total") / follow_interview_sum * 100,
                           1))) if follow_interview_sum else "-"
            arrange_interview_rate = '{}%'.format(str(
                to_decimal(item.get("arrange_interview_sum") / arrange_interview_sum * 100,
                           1))) if arrange_interview_sum else "-"
            item.update(
                {
                    "record_rate": record_rate,
                    "screen_rate": screen_rate,
                    "screen_passed_rate": screen_passed_rate,
                    "screen_eliminated_rate": screen_eliminated_rate,
                    "offered_rate": offered_rate,
                    "employed_rate": employed_rate,
                    "follow_interview_rate": follow_interview_rate,
                    "arrange_interview_rate": arrange_interview_rate
                }
            )

        return data_list

    async def hr_workload_data(self, validated_data: dict) -> list:
        """
        hr工作量
        @param validated_data:
        @return:
        """
        params_md5 = get_stats_params_md5(validated_data, RecruitStatsType.team_workload)
        redis_key = HR_WORKLOAD_STATS[0].format(
            company_id=self.company_id, user_id=self.user_id, params_md5=params_md5
        )
        redis_cli = await redis_db.default_redis
        result = await redis_cli.get(redis_key)
        if result:
            return ujson.loads(result)

        city_ids = validated_data.get("city_ids")
        dep_id = validated_data.get("dep_id")
        if any([city_ids, dep_id]):
            position_list = await get_position_list(
                self.company_id, self.user_id, {"city_ids": city_ids, "dep_id": dep_id}, ["id"], base_scope=False
            )
            # 一定不会为空
            position_ids = [position["id"] for position in position_list]
            validated_data["position_ids"] = position_ids
        ret = []
        filter_none_workload = validated_data.get("filter_none_workload")
        participants = await self._get_participants(ParticipantType.HR, validated_data)
        if participants:
            participant_ids = [item["id"] for item in participants]
            add_by_id2resume_count = await self._resume_work_load_map(validated_data)
            screen_resume_data = await self._screen_work_load_map(validated_data)
            add_by_id2screen_total = screen_resume_data.get("add_by_id2screen_total")
            add_by_id2passed_total = screen_resume_data.get("add_by_id2passed_total")
            add_by_id2eliminated_total = screen_resume_data.get("add_by_id2eliminated_total")
            add_by_id2arrange_interview_count = await self._arrange_interview_work_load_map(validated_data)
            add_by_id2offer_count = await self._offered_work_load_map(validated_data)
            other_workload_data = await self._other_work_load_map(participant_ids, validated_data)
            participant_id2employed_count = other_workload_data.get("p_id2employed_count")
            participant_id2interview_count = other_workload_data.get("p_id2interview_count")

            for participant in participants:
                add_by_id = participant["participant_refer_id"]
                participant_id = participant["id"]
                all_workload = sum(
                    [
                        add_by_id2resume_count.get(add_by_id, 0),
                        add_by_id2screen_total.get(add_by_id, 0),
                        add_by_id2passed_total.get(add_by_id, 0),
                        add_by_id2eliminated_total.get(add_by_id, 0),
                        add_by_id2offer_count.get(add_by_id, 0),
                        participant_id2interview_count.get(participant_id, 0),
                        participant_id2employed_count.get(participant_id, 0),
                        add_by_id2arrange_interview_count.get(add_by_id, 0)
                    ]
                )
                if filter_none_workload and not all_workload:
                    continue
                participant.update(
                    {
                        "record_total": add_by_id2resume_count.get(add_by_id, 0),
                        "screen_total": add_by_id2screen_total.get(add_by_id, 0),
                        "screen_passed_total": add_by_id2passed_total.get(add_by_id, 0),
                        "screen_eliminated_total": add_by_id2eliminated_total.get(add_by_id, 0),
                        "offered_total": add_by_id2offer_count.get(add_by_id, 0),
                        "employed_total": participant_id2employed_count.get(participant_id, 0),
                        "follow_interview_total": participant_id2interview_count.get(participant_id, 0),
                        "arrange_interview_total": add_by_id2arrange_interview_count.get(add_by_id, 0)
                    }
                )
                ret.append(participant)

            ret = self._handle_workload_rate(ret)
        await redis_cli.setex(redis_key, HR_WORKLOAD_STATS[1], ujson.dumps(ret))
        return ret

    async def emp_workload_data(self, validated_data: dict) -> list:
        """
        emp工作量
        @param validated_data:
        @return:
        """
        params_md5 = get_stats_params_md5(validated_data, RecruitStatsType.team_workload)
        redis_key = EMP_WORKLOAD_STATS[0].format(
            company_id=self.company_id, user_id=self.user_id, params_md5=params_md5
        )
        redis_cli = await redis_db.default_redis
        result = await redis_cli.get(redis_key)
        if result:
            return ujson.loads(result)

        city_ids = validated_data.get("city_ids")
        dep_id = validated_data.get("dep_id")
        if any([city_ids, dep_id]):
            position_list = await get_position_list(
                self.company_id, self.user_id, {"city_ids": city_ids, "dep_id": dep_id}, ["id"], base_scope=False
            )
            # 一定不会为空
            position_ids = [position["id"] for position in position_list]
            validated_data["position_ids"] = position_ids

        ret = []
        filter_none_workload = validated_data.get("filter_none_workload")
        participants = await self._get_participants(ParticipantType.EMPLOYEE, validated_data)
        if participants:
            screen_workload_data = await self._screen_work_load_map(validated_data)
            add_by_id2screen_total = screen_workload_data.get("add_by_id2screen_total")
            add_by_id2passed_total = screen_workload_data.get("add_by_id2passed_total")
            add_by_id2eliminated_total = screen_workload_data.get("add_by_id2eliminated_total")
            participant_id2employed_records = await InterViewParticipantService.get_participant_employed_records(
                self.company_id, **validated_data
            )
            participant_id2interviews = await InterViewParticipantService.get_participant_interviews(
                self.company_id, **validated_data
            )
            for participant in participants:
                add_by_id = participant["participant_refer_id"]
                participant_id = participant["id"]
                all_workload = sum(
                    [
                        add_by_id2screen_total.get(add_by_id, 0),
                        add_by_id2passed_total.get(add_by_id, 0),
                        add_by_id2eliminated_total.get(add_by_id, 0),
                        len(participant_id2interviews.get(participant_id, [])),
                        len(participant_id2employed_records.get(participant_id, [])),
                    ]
                )
                if filter_none_workload and not all_workload:
                    continue
                participant.update(
                    {
                        "screen_total": add_by_id2screen_total.get(add_by_id, 0),
                        "screen_passed_total": add_by_id2passed_total.get(add_by_id, 0),
                        "screen_eliminated_total": add_by_id2eliminated_total.get(add_by_id, 0),
                        "follow_interview_total": len(participant_id2interviews.get(participant_id, [])),
                        "employed_total": len(participant_id2employed_records.get(participant_id, []))
                    }
                )
                ret.append(participant)
        result = self._handle_workload_rate(ret)
        await redis_cli.setex(redis_key, EMP_WORKLOAD_STATS[1], ujson.dumps(result))
        return result
