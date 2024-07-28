# coding: utf-8
import asyncio

from business.b_wework import WeWorkBusiness
from constants import QrCodeType
from kits.exception import APIValidationError
from business.portals.b_portal_wework import PortalWeWorkBusiness
from services import svc
import time

from services.s_dbs.config.s_recruitment_team import RecruitmentTeamService
from services.s_https.s_ucenter import get_users
from utils.strutils import uuid2str


class CompanyIntroductionBusiness(object):

    async def check_sensitive_word(self, data: dict):
        verify_str = "{}{}{}{}{}{}".format(
            data.get("company_address", ""),
            data.get("welfare_tag", ""),
            data.get("company_desc", ""),
            data.get("contacts", ""),
            data.get("contact_email", ""),
            data.get("company_page", "")
        )

        weak_words = await svc.http_common.check_sensitive_word(verify_str)
        if weak_words:
            raise APIValidationError(msg="内容存在敏感字符")
        return data

    async def check_qrcode_url(self, company_id: str, data: dict):
        """
        @desc 判断二维码信息，如果是企业微信，需要调用第三接口获取二维码
        """
        qrcode_type = data.get("qrcode_type", 0)
        if qrcode_type == QrCodeType.CopWeiXin:
            qrcode_user_id = data.get("qrcode_user_id", "")
            app_id = await WeWorkBusiness.get_company_app_id(company_id)
            data["qrcode_url"] = await PortalWeWorkBusiness.get_external_contact_qr_code(
                app_id=app_id,
                company_id=company_id,
                employee_id=qrcode_user_id
            )

        if not data["qrcode_url"]:
            data["qrcode_type"] = 0
        return data

    async def create_company_intro(
            self, company_id: str, user_id: str, data: dict
    ) -> dict:
        """
        创建企业介绍
        1. 检查敏感词汇
        2. 判断二维码类型，如果是企业微信，需要调用接口获取二维码地址
        3. 保存信息
        """

        # data = await self.check_sensitive_word(data)

        data = await self.check_qrcode_url(company_id, data)

        u_id = await svc.com_intro.create_company_info(
            company_id, user_id, data
        )
        return {"id": u_id}

    async def company_intro_detail(self, company_id: str, record_id: str):
        """
        @desc 检查记录是否存在
        """
        if not record_id:
            raise APIValidationError(msg="企业介绍不存在")

        result = await svc.com_intro.get_company_intro_by_id(
            company_id, record_id
        )
        if not result:
            raise APIValidationError(msg="企业介绍不存在")
        return result

    async def update_company_intro(
            self, company_id: str, user_id: str, data: dict
    ) -> dict:
        """
        更新企业介绍信息
        """
        record_id = data.pop("id", "")
        await self.company_intro_detail(company_id, record_id)

        # data = await self.check_sensitive_word(data)

        data = await self.check_qrcode_url(company_id, data)

        record_id = await svc.com_intro.update_company_intro(
            company_id, user_id, record_id, data
        )
        return {"id": record_id}

    async def _check_company_intro_used(self, company_id: str, record_id: str) -> list:
        """
        @desc 获取被使用的页面信息
        """
        is_used = await svc.portal_page.is_used_intro(company_id, record_id)
        return is_used

    @classmethod
    async def sort_company_intro(cls, company_id: str, user_id: str, record_ids: list):
        """
        企业介绍排序
        """
        change_fun = []
        for index, record_id in enumerate(record_ids):
            data = {
                "order_no": index + 1
            }
            change_fun.append(
                svc.com_intro.update_company_intro(company_id, user_id, record_id, data)
            )

        await asyncio.gather(*change_fun)
        return {"success": True, "msg": "操作完成"}

    async def delete_company_intro(self, company_id: str, user_id: str, record_id: str):
        """
        删除企业介绍
        """
        record, is_used = await asyncio.gather(
            self.company_intro_detail(company_id, record_id),
            self._check_company_intro_used(company_id, record_id)
        )

        if record.get("is_default"):
            raise APIValidationError(msg='默认企业介绍不可删除')

        if is_used:
            raise APIValidationError(msg="企业介绍已经被使用，不可以删除")

        await svc.com_intro.update_company_intro(
            company_id, user_id, record_id, {"is_delete": True}
        )
        return {"id": record_id}

    async def get_introduction_list(self, company_id: str, query_params: dict, **kwargs) -> dict:
        """
        获取企业介绍列表
        """
        page = query_params.get("p") or 1
        limit = query_params.get("limit") or 100
        result = await svc.com_intro.company_intro_list(
            company_id, page, limit
        )
        data_list = result.get("objects") or []
        emp_ids = [item["qrcode_user_id"] for item in data_list if item["qrcode_user_id"]]
        emp_id2hr_id = {}
        hr_id2emp_id = {}
        if emp_ids:
            hr_emp_list = await RecruitmentTeamService.get_hr_emp_rel_hr_list(company_id)
            for item in hr_emp_list:
                emp_id2hr_id[item["emp_id"]] = item["hr_id"]
                hr_id2emp_id[item["hr_id"]] = item["emp_id"]
        emp_id2user = {}
        if emp_id2hr_id:
            users = await get_users(emp_id2hr_id.values())
            for user in users:
                emp_id2user[hr_id2emp_id[uuid2str(user.get("id"))]] = user

        for item in data_list:
            user = emp_id2user.get(item["qrcode_user_id"])
            item.update(
                {
                    "image_url": item.get("image_url").split(',') if item.get("image_url") else [],
                    "welfare_tag": item.get("welfare_tag").split(',') if item.get("welfare_tag") else [],
                    "company_fullname": kwargs.get("fullname", ""),
                    "company_shortname": kwargs.get("shortname", ""),
                    "qrcode_user_name": user.get("nickname") if user else ""
                }
            )
        result["objects"] = data_list

        return result
