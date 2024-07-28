from __future__ import absolute_import

from configs import config
from services.s_dbs.s_wework import WeWorkService
from services.s_https.s_candidate import CandidateService
from services.s_https.s_employee import EmployeeService
from services.s_https.s_ucenter import get_company_source
from services.s_https.s_wework import WeWorkExternalContactService


class WeWorkBusiness(object):
    @classmethod
    async def get_company_app_id(cls, company_id: str) -> int:
        """
        根据企业id，获取app_id
        :param company_id:
        :return:
        """
        source = await get_company_source(company_id)
        if source == 'wework':
            return 2010
        elif source == 'saas':
            return 2013
        else:
            raise Exception("不存在应用app_id")

    @classmethod
    async def get_by_external_id_first(cls, company_id: str, external_id: str):
        return await WeWorkService.get_by_external_id(company_id, external_id)

    @classmethod
    async def add_external_contact(cls, external_user_id, company_id):

        app_id = await WeWorkBusiness.get_company_app_id(company_id)
        wework_service = WeWorkExternalContactService(
            app_id=app_id,
            company_id=company_id
        )

        external_contact_info = await wework_service.get(external_user_id)
        if external_contact_info:
            external_contact = external_contact_info.get('external_contact')
            name = external_contact.get('name')
            external_type = external_contact.get('type')
            unionid = external_contact.get('unionid')
            follow_user = external_contact_info.get('follow_user')
            follow_user_for_employee = []
            if len(follow_user) > 0:
                user_ids = [user.get('userid') for user in follow_user]
                corp_users = await wework_service.get_corp_users(user_ids=user_ids)
                follow_user_for_employee = [{
                    'employee_id': corp_user.get('employee_id'),
                    'user_id': corp_user.get('user_id')
                } for corp_user in corp_users]

            model = await WeWorkService.get_external_by_unionid(company_id, unionid)
            if model:
                await WeWorkService.update_external_contact(
                    company_id, unionid, name=name, external_type=external_type,
                    external_id=external_user_id)

                await WeWorkService.create_or_update_external_contact_data(company_id, model.get('id'), follow_user_for_employee)

                # 更新候选人外部联系人类型
                candidate_id = model.get('candidate_id', None)
                if candidate_id:
                    await CandidateService.update_wework_external_contact(
                        company_id=company_id,
                        candidate_id=candidate_id,
                        wework_external_contact=external_type
                    )
            else:
                _id = await WeWorkService.create_obj(
                    company_id, unionid, name, external_type, external_id=external_user_id,
                    follow_user=follow_user_for_employee
                )

                await WeWorkService.create_or_update_external_contact_data(company_id, _id, follow_user_for_employee)
        else:
            model = await WeWorkService.get_by_external_id(company_id, external_user_id)
            if model:
                await WeWorkService.update_external_contact(
                    company_id, model.get('unionid'), external_type=0, external_id="")
                await WeWorkService.create_or_update_external_contact_data(company_id, model.get('id'), [])
                candidate_id = model.get('candidate_id', None)
                if candidate_id:
                    await CandidateService.update_wework_external_contact(
                        company_id=company_id,
                        candidate_id=candidate_id,
                        wework_external_contact=0
                    )

    @classmethod
    async def get_external_contact_employee(cls, company_id, candidate_id):
        """
        获取外部联系人员工信息
        :param company_id:
        :param candidate_id:
        :return:
        """
        model = await WeWorkService.get_by_candidate_id(company_id, candidate_id)
        if not model:
            return []

        model2 = await WeWorkService.get_data_by_wework_external_contact_id(company_id, model.get('id'))
        if not model2:
            return []

        follow_user = model2.get('follow_user')
        if len(follow_user) == 0:
            return []

        employee_ids = [user.get('employee_id') for user in follow_user]
        employee_info_list = await EmployeeService.get_employee_info_by_ids(company_id, employee_ids, head_fields=None)
        return [info.get('emp_name', '') for info in employee_info_list]
