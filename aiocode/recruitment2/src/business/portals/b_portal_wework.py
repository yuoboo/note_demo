# coding: utf-8
from business.b_wework import WeWorkBusiness
from configs import config
from constants import WEWORK_2HAOHR_STATE
from kits.exception import APIValidationError
from services.s_dbs.config.s_recruitment_team import RecruitmentTeamService
from services.s_dbs.s_wework import WeWorkExternalContactWay
from services.s_https.s_person_ucenter import PersonUCenterService
from services.s_https.s_ucenter import get_users
from services.s_https.s_wework import WeWorkExternalContactService
from utils.strutils import uuid2str


class PortalWeWorkBusiness(object):
    """
    招聘门户企业微信相关业务
    """
    @classmethod
    async def get_hr_list(cls, company_id: str) -> list:
        """
        获取有"客户联系功能"权限的HR列表
        @param company_id: 企业id
        """
        hr_emp_rel_list = await RecruitmentTeamService.get_hr_emp_rel_hr_list(company_id)
        employee_ids = []
        employee_dict = {}
        hr_dict = {}
        for rel in hr_emp_rel_list:
            emp_id = rel.get('emp_id', None)
            hr_id = rel.get('hr_id', None)
            if emp_id and hr_id:
                employee_ids.append(emp_id)
                employee_dict[emp_id] = hr_id
                hr_dict[hr_id] = emp_id

        if len(employee_ids) == 0:
            return []

        app_id = await WeWorkBusiness.get_company_app_id(company_id)
        wework_service = WeWorkExternalContactService(app_id=app_id, company_id=company_id)
        corp_users = await wework_service.get_corp_users(employee_ids=employee_ids)

        user_list = await wework_service.get_follow_user_list()

        hr_ids = []
        for corp_user in corp_users:
            user_id = corp_user.get('user_id', None)
            emp_id = corp_user.get('employee_id', None)
            if user_id and emp_id and user_id in user_list:
                hr_id = employee_dict.get(emp_id)
                if hr_id:
                    hr_ids.append(hr_id)

        users = await get_users(hr_ids)
        results = []
        for user in users:
            results.append({
                'name': user.get('nickname', ''),
                'qrcode_user_id': hr_dict.get(uuid2str(user.get('id', None)))
            })

        return results

    @classmethod
    async def create_external_contact_qr_code(cls, app_id: int, company_id: str, employee_id: str) -> dict:
        """
        创建外部联系人二维码
        @param app_id:
        @param company_id:
        @param employee_id:
        @return:
        """
        corp_users = await PersonUCenterService.wework_get_corp_users(
            app_id=app_id, company_id=company_id, employee_ids=[employee_id]
        )
        if len(corp_users) != 1:
            raise APIValidationError(msg="设置失败")

        corp_user = corp_users[0]
        user_id = corp_user.get('user_id', None)

        data = {
            "type": 1,
            "scene": 2,
            "user": [user_id],
            "state": WEWORK_2HAOHR_STATE
        }

        service = WeWorkExternalContactService(app_id=app_id, company_id=company_id)
        contact_way = await service.add_contact_way(data)
        if not contact_way:
            raise APIValidationError(msg="设置失败")
        config_id = contact_way.get('config_id', None)
        qr_code = contact_way.get('qr_code', None)
        await WeWorkExternalContactWay.create(app_id, company_id, employee_id, user_id, config_id, qr_code)
        return {
            'qr_code': qr_code
        }

    @classmethod
    async def get_external_contact_qr_code(cls, app_id: int, company_id: str, employee_id: str) -> str:
        """
        获取外部联系人二维码
        @param app_id: 应用id
        @param company_id: 企业id
        @param employee_id: 员工id
        @return: 二维码
        """
        way = await WeWorkExternalContactWay.get(app_id, company_id, employee_id)

        if not way:
            way = await cls.create_external_contact_qr_code(app_id, company_id, employee_id)

        return way.get('qr_code', None)

    @classmethod
    async def get_hr_qr_code(cls, app_id: int, company_id: str, hr_id: str) -> str:
        """
        获取hr的外部联系人二维码
        :param app_id: 应用id
        :param company_id: 企业id
        :param hr_id: hr id
        :return: 二维码
        """
        hr_emp_list = await RecruitmentTeamService.get_hr_emp_rel_hr_list(company_id)
        employee_id = None
        for hr_emp in hr_emp_list:
            if hr_id == hr_emp.get('hr_id'):
                employee_id = hr_emp.get('emp_id')
        if employee_id is None:
            raise APIValidationError(msg="当前管理员未与员工关联")
        return await cls.get_external_contact_qr_code(app_id, company_id, employee_id)
