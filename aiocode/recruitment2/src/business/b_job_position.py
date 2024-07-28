# coding: utf-8
import asyncio

from kits.exception import APIValidationError
from services import svc
from services.s_dbs.s_common import DistrictService
from services.s_dbs.s_job_position import JobPositionSelectService, JobPositionUpdateService, JobPositionTypeService, \
    PositionParticipantService, job_position_tbu
from services.s_https.s_employee import DepartmentService
from utils.age import get_age_range
from utils.range_text import get_position_salary_range
from utils.strutils import uuid2str, create_tree
from constants import WorkType, WorkExperience, JobPositionEducation, ParticipantType


class JobPositionBusiness(object):

    @classmethod
    async def set_positions_referral_bonus(
            cls, company_id: str, user_id: str, job_position_ids: list, referral_bonus: str
    ) -> dict:
        """
        设置招聘职位为内推职位
        """
        job_position_ids = [uuid2str(p_id) for p_id in job_position_ids]
        valid_position_ids = await JobPositionSelectService.valid_position_ids(company_id, job_position_ids)
        if valid_position_ids:
            await asyncio.gather(
                JobPositionUpdateService.set_position_referral_bonus(
                    company_id, user_id, valid_position_ids, referral_bonus
                ),
                # 同步内推奖金到招聘门户关联职位
                svc.portal_position.update_portal_position_bonus(
                    company_id, user_id, position_ids=valid_position_ids, referral_bonus=referral_bonus
                )
            )

        result = {
            "total": len(job_position_ids),
            "failed_count": len(job_position_ids) - len(valid_position_ids)
        }

        return result

    @classmethod
    async def _format_query(cls, company_id: str, user_id: str, **kwargs):
        """
        @desc 格式话查询参数
        """
        dep_ids = kwargs.get("dep_ids", "")
        if dep_ids:
            if ',' in dep_ids:
                dep_ids = dep_ids.split(',')
            else:
                dep_ids = [dep_ids]
            dep_ids, manager_data = await asyncio.gather(
                DepartmentService.get_all_dep_ids(company_id, dep_ids),
                svc.manage_scope.hr_manage_scope(company_id, user_id)
            )
        else:
            dep_ids = []
            manager_data = await svc.manage_scope.hr_manage_scope(company_id, user_id)

        query_params = kwargs
        query_params.update({
            "keyword": kwargs.get("keyword", ""),
            "dep_ids": dep_ids,
            "permission_ids": manager_data.get("position_ids"),
            "status": kwargs.get('status', 1),
        })
        return query_params

    @classmethod
    def _format_position_data(cls, data: list, job_position_type_map: dict):
        """
        @desc 格式化返回数据
        1. 枚举类型格式化，增加文本字段，后缀为_text字段
        2. 年龄，增加age_range字段
        3. 职位类型，增加职位类型文本
        """
        for item in data:
            position_type = job_position_type_map.get(item['job_position_type_id']) or {}
            position_type = position_type.get("name", "")
            item['job_position_type_name'] = position_type
            item['secondary_cate'] = position_type

            if "age_min" in item:
                item['age_range'] = get_age_range(item['age_min'], item['age_max'], job_position=False) or "年龄不限"
            if "salary_min" in item:
                item['salary_range'] = get_position_salary_range(
                    item['salary_min'], item['salary_max'], item['salary_unit']
                ) or "薪资面议"
            if "work_type" in item:
                item['work_type_text'] = WorkType.attrs_[item["work_type"] or 0]
            if "work_experience" in item:
                item['work_experience_text'] = WorkExperience.attrs_[item['work_experience'] or 0]
            if "education" in item:
                item['education_text'] = JobPositionEducation.attrs_[item['education'] or 0]

            if "welfare_tag" in item:
                item["welfare_tag"] = item["welfare_tag"].split(",") if item["welfare_tag"] else []

        return data

    @classmethod
    async def _fill_job_position_participant_hr(cls, data):
        """
        填充招聘职位的招聘hr数据
        :param data:
        :return:
        """
        items = data.get('objects', [])
        job_position_ids = list(set([item.get('id') for item in items]))
        results = await PositionParticipantService.get_participant_by_position_ids(
            job_position_ids, ["id", "name", "participant_refer_id"]
        )
        for idx, item in enumerate(list(items)):
            result = results.get(item.get('id', None), {})
            item['participants_hr'] = [{
                    'id': r.get('id', None),
                    'name': r.get('name', None),
                    'participant_refer_id': r.get('participant_refer_id', None)
                } for r in result]
        data['objects'] = items

    @classmethod
    async def get_portals_position_list(cls, company_id: str, user_id: str, validated_data: dict) -> list:
        """
        获取内推 - 职位列表
        :param company_id:
        :param user_id:
        :param validated_data: 搜索条件
        """
        fields = [
            "id", "name", "dep_id", "dep_name", "job_title_id", "job_title_name", "status",
            "province_id", "province_name", "city_id", "city_name", "town_id", "town_name",
            "work_type", "referral_bonus"
        ]
        query_params = await cls._format_query(company_id, user_id, **validated_data)

        data = await JobPositionSelectService.search_positions_with_page(
            company_id, validated_data.get('p', 1), fields, query_params, validated_data.get('limit', 10)
        )
        await cls._fill_job_position_participant_hr(data)

        return data

    @classmethod
    async def get_position_list(cls, company_id: str, user_id: str, keyword: str = None, dep_id: str = None):
        fields = [
            "id", "name", "dep_id", "dep_name", "position_total", "salary_min", "salary_max",
            "emergency_level", "salary_unit", "age_min", "age_max", "job_position_type_id",
            "work_type", "province_id", "province_name", "city_id", "city_name", "town_id",
            "town_name", 'work_place_name', 'work_experience', 'education', 'status', 'position_description'
        ]
        query_params = await cls._format_query(company_id, user_id, dep_ids=dep_id, keyword=keyword)

        data_list, type_map = await asyncio.gather(
            JobPositionSelectService.search_positions(
                company_id, fields, query_params
            ),
            JobPositionSelectService.get_position_type_referral_map()
        )

        data = cls._format_position_data(data_list, type_map)

        return data

    @classmethod
    async def position_city_list(cls, company_id: str, user_id: str):
        """
        获取用户管理范围内的职位工作城市
        @param company_id:
        @param user_id:
        @return:
        """
        result = await svc.manage_scope.hr_manage_scope(company_id, user_id)
        position_ids = result.get("position_ids")
        city_list = set()
        if position_ids:
            data = await JobPositionSelectService.search_positions(
                company_id, ["province_id", "city_id"], {"permission_ids": position_ids}
            )
            for item in data:
                if item["city_id"]:
                    city_list.add(item["city_id"])
        res = {}
        if city_list:
            res = await DistrictService.get_district(list(city_list))
        result = []
        for city_id, city in res.items():
            result.append(
                {
                    "city_id": city_id,
                    "city_name": city["name"]
                }
            )
        return result

    @staticmethod
    async def get_position_type_tree() -> list:
        """
        获取所有的招聘职位类型(树形)
        """
        _types = await JobPositionTypeService.get_position_types()
        return create_tree(_types, children_key="children", parent_key="parent_id")

    @classmethod
    async def get_position_menu(
            cls, company_id: str, user_id: str, user_type: int = ParticipantType.HR, query_params: dict = None
    ) -> list:
        """
        获取下拉筛选职位数据（需要根据管理范围过滤）
        @param company_id:
        @param user_id:
        @param user_type:
        @param query_params:
        @return:
        """
        res = []
        is_page = query_params.get("is_page")
        if user_type == ParticipantType.HR:
            scope_res = await svc.manage_scope.hr_manage_scope(company_id, user_id)
        else:
            scope_res = await svc.manage_scope.emp_manage_scope(company_id, user_id)
        position_ids = scope_res.get("position_ids")
        if position_ids:
            if not is_page:
                res = await JobPositionSelectService.get_positions_by_ids(
                    company_id, ids=position_ids, fields=["id", "name", "dep_id", "dep_name"], query_params=query_params
                )
            else:
                query_params["ids"] = position_ids
                res = await JobPositionSelectService.get_positions_with_paging(
                    company_id, fields=["id", "name", "dep_id", "dep_name"], query_params=query_params
                )

        return res


class IntranetJobPositionBusiness:

    @classmethod
    async def get_job_position_info(cls, company_id: str, ids: list, fields: list = None) -> list:
        """
        获取指定招聘需求信息
        如果没有ids返回企业所有数据
        """
        if fields:
            diff = set(fields) - set(job_position_tbu.tb_keys)
            if diff:
                raise APIValidationError(msg=f"不支持的字段:{diff}")

        return await JobPositionSelectService.get_job_positions_bys(
            company_id=company_id, ids=ids, fields=fields
        )
