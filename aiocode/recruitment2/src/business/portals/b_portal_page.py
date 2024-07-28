# coding: utf-8
import asyncio

from business.b_wework import WeWorkBusiness
from constants.redis_keys import EMPLOYEE_NAME_KEY
from drivers.redis import redis_db
from error_code import Code
from kits.exception import APIValidationError
from constants import ParticipantType, WorkType, WorkExperience, JobPositionEducation, EmpQrCodeType, QrCodeSignType
from services.s_dbs.portals.s_portal_delivery import DeliveryRecordService
from services.s_dbs.s_recruitment_channel import RecruitmentChannelService
from services.s_https.s_employee import DepartmentService, EmployeeService
from services.s_https.s_ucenter import get_company_for_id
from services.s_https.s_wework import WeWorkExternalContactService
from services.s_dbs.portals.s_portal_page import PortalPositionsService, PortalPageService, \
    tb_recruitment_portal_record_tbu
from services.s_dbs.s_job_position import JobPositionSelectService
from utils.range_text import get_salary_range
from utils.strutils import uuid2str
from utils.age import get_age_range
from business.portals.b_portal_wework import PortalWeWorkBusiness
from services import svc


class PortalPageBusiness(object):
    """
    招聘门户网页配置业务类
    """

    def _get_portal_position_fields(self):
        fields = [
            "id", "work_type", "name", "position_total", "salary_min", "salary_max", "salary_unit",
            "province_id", "province_name", "city_id", "city_name", "town_id", "town_name",
            "age_min", "age_max", "poster_position_desc", "first_cate", "secondary_cate", "position_desc",
            "category_name", "education", "work_experience", "work_address", "job_position_id",
            "welfare_tag", "address_longitude", "address_latitude", "recruitment_page_id"
        ]
        return sorted(fields)

    def _format_position_data(self, data: list):
        """
        @desc 格式化返回数据
        1. 枚举类型格式化，增加文本字段，后缀为_text字段
        2. 年龄，增加age_range字段
        3. 职位类型，增加职位类型文本
        """
        for item in data:
            if "first_cate" in item:
                cate_full_name = item["first_cate"]
                if cate_full_name and item["secondary_cate"]:
                    cate_full_name += r"/{}".format(item["secondary_cate"])
                if cate_full_name and item["category_name"]:
                    cate_full_name += r"/{}".format(item["category_name"])
                item['cate_full_name'] = cate_full_name
            if "age_min" in item:
                item['age_range'] = get_age_range(item['age_min'], item['age_max'], job_position=False)
            if "salary_min" in item:
                item['salary_range'] = get_salary_range(
                    item['salary_min'], item['salary_max'], item['salary_unit']
                )
            if "work_type" in item:
                item['work_type_text'] = WorkType.attrs_[item["work_type"]] if item["work_type"] is not None else ""
            if "work_experience" in item:
                ep_text = WorkExperience.attrs_[item['work_experience']] if item['work_experience'] is not None else ""
                item['work_experience_text'] = ep_text
            if "education" in item:
                ed_text = JobPositionEducation.attrs_[item['education']] if item['education'] is not None else ""
                item['education_text'] = ed_text

            if "welfare_tag" in item:
                item["welfare_tag"] = item["welfare_tag"].split(",") if item["welfare_tag"] else []

        return data

    @classmethod
    async def find_portal_page_basic(cls, company_id: str) -> list:
        """
        获取招聘门户网页列表（基础信息，用于前端筛选）
        @param company_id:
        @return:
        """
        page_fields = [
            "id", "name"
        ]
        page = await svc.portal_page.find_by_company(company_id, page_fields)
        return page

    async def _format_postion_type_ids(self, position_type_id: list):
        """
        @desc 获取职位类别的子孙类别id
        """
        if not position_type_id:
            return []

        job_position_type_map = await svc.job_position_type.get_job_position_type_ids_map()
        return job_position_type_map.get(position_type_id, [])

    async def get_position_list(
            self, company_id: str, page_id: str, query: dict, fields: list, position_fields: list):
        """
        @desc 获取职位列表
        """
        is_page = query.get("is_page", False)
        if not is_page:
            position_list = await svc.portal_position.get_portal_positions(
                company_id, page_id, fields, position_fields, query
            )
            position_list = self._format_position_data(position_list)
        else:
            position_info = await svc.portal_position.get_portal_positions_by_paging(
                company_id, page_id, fields, position_fields,
                query.get("p", 1), query.get("limit", 20), query
            )
            list_data = position_info["objects"]
            if list_data:
                position_info["objects"] = self._format_position_data(list_data)
            position_list = position_info

        return position_list

    async def get_portal_position_list(
            self, company_id: str, query: dict, page_id: str,
            is_page: bool = False, select_data: bool = False
    ):
        """
        获取指定网页的职位列表信息
        @param company_id:
        @param query:
        @param page_id:
        @param is_page: 是否分页
        @param select_data: 是否下拉数据
        @return:
        """
        if not page_id:
            raise APIValidationError(msg="门户网页ID缺失")
        query.update({
            "is_page": is_page
        })
        fields = ["id", "job_position_id", "name"] if select_data else self._get_portal_position_fields()
        position_fields = ["referral_bonus", "dep_id", "dep_name"]

        position_list = await self.get_position_list(company_id, page_id, query, fields, position_fields)
        return position_list

    @classmethod
    async def get_portal_position_for_menu(
            cls, company_id: str, user_id: str, user_type=ParticipantType.EMPLOYEE
    ) -> list:
        """
        查询参与内推的职位列表(下拉列表):
        员工：当前员工内推记录中职位的并集
        HR: 内推记录中职位的并集, 且要根据管理范围过滤
        @param company_id:
        @param user_id:
        @param user_type:
        @return:
        """
        res = []
        if user_type == ParticipantType.EMPLOYEE:
            records = await DeliveryRecordService.get_referral_records(
                company_id, referee_id=user_id, fields=["position_record_id"]
            )
            job_position_ids = None
        else:
            records = await DeliveryRecordService.get_referral_records(
                company_id, fields=["position_record_id"]
            )
            scope_data = await svc.manage_scope.hr_manage_scope(company_id, user_id)
            job_position_ids = scope_data.get("position_ids")
        if records:
            position_record_ids = list(set([item.get("position_record_id") for item in records]))
            res = await PortalPositionsService.get_portal_positions_by_ids(
                company_id, position_record_ids, ["id", "job_position_id", "name"], job_position_ids,
                need_join=True, position_fields=["status"]
            )

        return res

    async def get_portal_position_detail(self, company_id: str, record_id: str):
        """
        @desc 获取网页职位详情
        """
        position_fields = self._get_portal_position_fields()
        position = await svc.portal_position.get_portal_position_by_id(
            company_id, record_id, position_fields
        )
        position_data = self._format_position_data([position])
        return position_data[0]

    async def _create_position_qrcode(
            self, share_id: str, employee_id: str, record_id: str, channel_id: str
    ):
        """
        @desc 生成内推职位小程序码
        """
        qrcode_params = {
            "channel_id": uuid2str(channel_id),
            "referee_id": uuid2str(employee_id),
            "share_id": uuid2str(share_id),
            "record_id": uuid2str(record_id)
        }
        qrcode_url = await svc.http_common.create_qr_code(qrcode_params, QrCodeSignType.RECRUIT_PORTAL)
        return qrcode_url

    async def get_portal_position_qrcode_url(
            self, employee_id: str, portal_position_id: str, company_info: dict, channel_id: str
    ):
        """
        @desc 获取指定员工(或渠道)，指定职位的小程序码。包括员工内推分享和HR分享，
        用employee_id和channel_id进行区分，二者不同时存在。
        @param employee_id:
        @param portal_position_id:
        @param company_info:
        @param channel_id:
        @return:
        """
        qrcode_url = ""
        # 为了兼容历史
        if not employee_id and not channel_id:
            position = await PortalPositionsService.get_portal_position_by_id_only(
                portal_position_id, ["company_id", "job_position_id", "qrcode_url"]
            )
            if position:
                qrcode_url = position.get("qrcode_url")
                if not qrcode_url:
                    company = await get_company_for_id(str(position.get("company_id")))
                    if company:
                        share_id = company.get("share_id")
                        qrcode_params = {
                            "id": str(position.get("job_position_id")),
                            "share_id": str(share_id),
                            "record_id": str(portal_position_id)
                        }
                        qrcode_url = await svc.http_common.create_qr_code(
                            qrcode_params, sign_type=QrCodeSignType.WX_RECRUITMENT
                        )

        else:
            company_id = company_info["company_id"]
            refer_id = employee_id or channel_id
            # 员工分享的时候，渠道为固定渠道"内推"，后端自行查询，HR分享，渠道由前端传递
            if not channel_id:
                channel_id = await RecruitmentChannelService.find_channel_by_name(company_id, "内推")
            qrcode_url = await svc.portal_position.get_position_qrcode(company_id, refer_id, portal_position_id)
            if not qrcode_url:
                qrcode_url = await self._create_position_qrcode(
                    company_info["share_id"], employee_id, portal_position_id, channel_id
                )
                await svc.portal_position.create_position_qrcode(
                    company_id, refer_id, portal_position_id, qrcode_url
                )

        return {"qrcode_url": qrcode_url}

    async def get_company_introduction_by_id(self, company_id:  str, company_introduction_id: str):
        """
        @desc 获取企业介绍信息
        """
        introduction = {}
        if company_introduction_id:
            company_info, introduction = await asyncio.gather(
                svc.http_ucenter.get_company_for_id(company_id),
                svc.com_intro.get_company_intro_by_id(company_id, company_introduction_id)
            )

            introduction.update({
                "company_fullname": company_info.fullname,
                "company_shortname": company_info.shortname,
                "share_id": uuid2str(company_info.share_id)
            })
        return introduction

    async def portal_company_intro_by_id(self, portal_id: str):
        """
        根据网页id获取对应的企业介绍
        @param company_id:
        @param portal_id:
        @return:
        """
        page_info = await svc.portal_page.page_detail_by_id(portal_id, ['company_id', 'company_introduction_id'])
        introduction = await self.get_company_introduction_by_id(
            page_info.get('company_id'),
            page_info.get("company_introduction_id")
        )
        return introduction

    async def portal_company_intro(self, company_id: str, portal_id: str):
        """
        根据网页id获取对应的企业介绍
        @param company_id:
        @param portal_id:
        @return:
        """
        page_info = await svc.portal_page.page_detail(company_id, portal_id, ['company_introduction_id'])
        introduction = await self.get_company_introduction_by_id(
            company_id, page_info.get("company_introduction_id")
        )
        return introduction

    async def _get_employee_name(self, company_id: str, employee_id: str):
        """
        获取员工姓名
        @param company_id:
        @param employee_id:
        @return:
        """
        redis_cli = await redis_db.default_redis
        redis_key = EMPLOYEE_NAME_KEY[0].format(company_id=uuid2str(company_id), employee_id=uuid2str(employee_id))
        emp_name = await redis_cli.get(redis_key)
        if not emp_name:
            employee_list = await EmployeeService.get_employee_info_by_ids(
                company_id, [employee_id], ["emp_name"]
            )
            emp_name = employee_list[0].get("emp_name", None) if employee_list else None
            if emp_name:
                await redis_cli.setex(redis_key, EMPLOYEE_NAME_KEY[1], emp_name)
        return emp_name

    async def get_referral_employee_info(self, company_id: str, employee_id: str, emp_site=True):
        """
        获取内推人配置等信息
        @param company_id:
        @param employee_id:
        @param emp_site: 是否员工端
        @return:
        """
        employee_config = await svc.referral_emp.get_employee(company_id, employee_id)
        emp_name = await self._get_employee_name(company_id, employee_id)
        employee_config['referee_name'] = emp_name
        # 员工端增加是否可以使用企业微信的逻辑判断
        if emp_site:
            app_id = await WeWorkBusiness.get_company_app_id(company_id)
            ww_svc = WeWorkExternalContactService(app_id=app_id, company_id=company_id)
            emp_user, all_emp_list = await asyncio.gather(
                ww_svc.get_corp_users(employee_ids=[employee_id]),
                ww_svc.get_follow_user_list()
            )
            if emp_user:
                emp_user = emp_user[0]["user_id"]
            else:
                emp_user = ""

            employee_config.update({
                "can_use_wework": emp_user in set(all_emp_list)
            })
        return employee_config

    async def _check_referral_employee_data(self, company_id: str, employee_data: dict):
        """
        @desc 检查内推人信息
        """
        employee_id = employee_data.get("employee_id", "")
        if not employee_id:
            raise APIValidationError(Code.FORBIDDEN)

        qrcode_type = employee_data.get("qrcode_type", 0)
        qrcode_url = employee_data.get("qrcode_url", "")

        # 企业微信二维码
        if qrcode_type == EmpQrCodeType.CopWeiXin:
            app_id = await WeWorkBusiness.get_company_app_id(company_id)
            qrcode_url = await PortalWeWorkBusiness.get_external_contact_qr_code(
                app_id=app_id,
                company_id=company_id,
                employee_id=employee_id
            )
            employee_data["qrcode_url"] = qrcode_url

        if not qrcode_url or qrcode_type == 0:
            employee_data["qrcode_type"] = 0
            employee_data["qrcode_url"] = ""
        return employee_data

    async def update_referral_employee_info(self, company_id: str, employee_data: dict):
        """
        @desc 更新内推人信息
        1. 先检查是否存在
        2. 如果不存在，则创建
        3. 如果存在，则更新
        """
        employee_id = employee_data.get("employee_id", "")

        employee_data, employee = await asyncio.gather(
            self._check_referral_employee_data(company_id, employee_data),
            self.get_referral_employee_info(company_id, employee_id)
        )

        if not employee.get("id"):
            await svc.referral_emp.create_employee(company_id, employee_data)
        else:
            await svc.referral_emp.update_employee(company_id, employee_data)
        return {"employee_id": employee_id}

    async def get_position_type_and_city(self, company_id: str, page_id: str = None) -> dict:
        """
        获取招聘网页中招聘职位对应的城市/职位类型筛选源
        传page_id 则获取对应page_id网页关联职位的数据，不传page_id 则获取企业所有职位上的数据
        """
        ret = {"city": [], "position_type": []}
        if page_id:
            # 兼容历史分享链接无share_id
            if not company_id:
                page = await PortalPageService.get_page_by_id(page_id, ["id", "company_id"])
                if not page:
                    return ret
                company_id = page.get("company_id")
            portal_positions = await PortalPositionsService.get_positions_by_page_id(
                company_id, page_id, fields=["job_position_id", "city_id", "city_name", "secondary_cate"]
            )
            if not portal_positions:
                return ret

            # 招聘网页的数据在网页数据上
            _city_dict = dict()
            _type_dict = dict()
            _type_map = await JobPositionSelectService.get_position_type_second_map()
            for _p in portal_positions:
                if _p["city_name"]:
                    _city_dict[_p["city_id"]] = {
                        "city_id": _p["city_id"],
                        "city_name": _p["city_name"]
                    }
                if _p["secondary_cate"]:
                    _type_dict[_p["secondary_cate"]] = {
                        "type_id": _type_map.get(_p["secondary_cate"]),
                        "type_name": _p["secondary_cate"]
                    }
            ret["city"] = list(_city_dict.values())
            ret["position_type"] = list(_type_dict.values())

        return ret

    @classmethod
    async def get_position_department_tree(cls, company_id: str, scene_type: int = None) -> list:
        """
        获取招聘职位上用人部门树 前端选择组件
        scene_type: 1.内推职位用人部门
        """
        if scene_type == 1:
            # 获取企业内推招聘职位信息
            deps = await JobPositionSelectService.get_referral_position_by_filter(
                company_id=company_id, fields=["dep_id"]
            )
        else:
            deps = await JobPositionSelectService.get_positions_by_ids(
                company_id=company_id, fields=["dep_id"]
            )

        dep_ids = [d["dep_id"] for d in deps]
        return await DepartmentService.get_dep_parent_tree(company_id, dep_ids)


class IntranetPortalPageBusiness:
    @classmethod
    async def get_portal_page(cls, company_id: str, ids: list = None, fields: list = None) -> list:
        if fields:
            diff = set(fields) - set(tb_recruitment_portal_record_tbu.tb_keys)
            if diff:
                raise APIValidationError(msg=f"不支持的字段: {diff}")

        return await svc.portal_page.get_portal_page(
            company_id=company_id, ids=ids, fields=fields
        )
