# coding: utf-8
import asyncio

from kits.exception import ServiceError
from utils.ehr_request import EhrRequest
from utils.strutils import uuid2str


class CandidateService(object):

    @classmethod
    async def get_candidate_by_name_and_mobile(
            cls, company_id: str, name: str, mobile: str, user_id=None,
            auto_create=True, resume_origin_id=None, raise_exception=True
    ) -> dict:
        """
        根据姓名和手机号获取候选人 基本信息
        :param company_id:
        :param name:
        :param mobile:
        :param user_id:
        :param auto_create:不存在的情况下是否需要自动创建
        :param resume_origin_id
        :param raise_exception
        """
        params = {
            "company_id": uuid2str(company_id),
            "user_id": user_id,
            "name": name,
            "mobile": mobile,
            "auto_create": auto_create
        }
        if resume_origin_id:
            params['resume_origin_id'] = resume_origin_id
        res = await EhrRequest("applicant_center").intranet("candidate_get").post(data=params)
        if res and res['resultcode'] == 200:
            ret = res['data'] or {}
        else:
            if raise_exception:
                raise ServiceError(msg="查询候选人失败")
            ret = {}
        return ret

    @classmethod
    async def create_candidate_by_form_data_and_attach(
            cls, company_id: str, candidate_data: dict,
            candidate_attachments=None,
            file_key=None, origin_url=None, user_id=None,
            resume_origin_id=None, candidate_record_id=None, candidate_id=None,
            update_talent_resume=False
    ) -> dict:
        """
        根据标准简历创建候选人（支持简历文件及其他附件）
        :param company_id:
        :param candidate_data:
        :param candidate_attachments:
        :param file_key:
        :param origin_url:
        :param user_id:
        :param resume_origin_id
        :param candidate_record_id
        :param candidate_id
        :param update_talent_resume: 是否更新候选人简历
        """
        params_data = {
            "company_id": uuid2str(company_id),
            "user_id": uuid2str(user_id) if user_id else None,
            "file_key": file_key,
            "origin_url": origin_url,
            "candidate_data": candidate_data,
            "candidate_attachments": candidate_attachments,
            "candidate_id": uuid2str(candidate_id) if candidate_id else None,
            "update_talent_resume": update_talent_resume
        }
        if candidate_record_id:
            params_data['candidate_record_id'] = uuid2str(candidate_record_id)
        if resume_origin_id:
            params_data['resume_origin_id'] = resume_origin_id
        res = await EhrRequest("applicant_center").intranet("candidate/create/by_resume_assi").post(data=params_data)
        if not res or res["resultcode"] != 200:
            error_msg = "服务器错误" if not res else res["errormsg"]
            raise ServiceError(msg=error_msg)

        return res["data"]

    @classmethod
    async def get_candidates_base_info(cls, company_id: str, candidate_ids: list) -> dict:
        """
        批量获取候选人信息
        :param company_id:
        :param candidate_ids:
        :return:
        """
        params = {
            "company_id": str(company_id),
            "candidate_ids": [str(c_id) for c_id in candidate_ids],
        }
        res = await EhrRequest("applicant_center").intranet("batch_candidate_base_info").post(data=params)
        if not res or res.get("resultcode") != 200:
            return {}

        return res["data"]

    @classmethod
    async def get_std_resume(cls, company_id: str, candidate_record_ids: list) -> dict:
        """
        批量获取候选人信息
        :param company_id:
        :param candidate_record_ids:
        :return:
        """
        params = {
            "company_id": str(company_id),
            "cr_ids": [str(c_id) for c_id in candidate_record_ids],
        }
        res = await EhrRequest("applicant_center").intranet("batch_cr_std_resume").post(data=params)
        if not res or res.get("resultcode") != 200:
            return {}

        return res["data"]

    @classmethod
    async def get_latest_remark(cls, company_id: str, candidate_ids: list) -> dict:
        """
        批量获取候选人最后一条备注信息
        :param company_id:
        :param candidate_ids:
        :return:
        """
        params = {
            "company_id": str(company_id),
            "candidate_ids": [str(c_id) for c_id in candidate_ids],
        }
        res = await EhrRequest("applicant_center").intranet("batch_latest_remark").post(data=params)
        if not res or res.get("resultcode") != 200:
            return {}

        return res["data"]

    @classmethod
    async def get_tags(cls, company_id: str, tag_ids: list) -> dict:
        """
        批量获取候选人标签
        :param company_id:
        :param tag_ids:
        :return:
        """
        params = {
            "company_id": str(company_id),
            "tag_ids": [str(c_id) for c_id in tag_ids],
        }
        res = await EhrRequest("applicant_center").intranet("candidate/tags").post(data=params)
        if not res or res.get("resultcode") != 200:
            return {}

        return res["data"]

    @classmethod
    async def search_candidate(cls, company_id: str, keyword: str) -> dict:
        """
        根据关键字搜索候选人 目前支持 姓名和手机号(不区分大小写)
        """
        params = {
            "company_id": company_id,
            "keyword": keyword
        }
        res = await EhrRequest("applicant_center").intranet("candidate/search").get(data=params)
        if not res or res["resultcode"] != 200:
            return {}
        return res["data"]

    @classmethod
    async def update_wework_external_contact(cls, company_id: str, candidate_id: str, wework_external_contact: int = 0):
        """
        更新候选人的企业微信外部联系人类型
        """
        if not candidate_id:
            return
        params = {
            'company_id': company_id,
            'candidate_id': candidate_id,
            'wework_external_contact': wework_external_contact
        }
        res = await EhrRequest("applicant_center").intranet("candidate/wework_external_contact").post(data=params)
        if not res or res["resultcode"] != 200:
            return {}
        return res["data"]

    @classmethod
    async def update_latest_activate_dt(cls, company_id: str, candidate_ids: list):
        """
        更新候选人的最新激活时间
        @param company_id:
        @param candidate_ids:
        @return:
        """
        candidate_ids = [uuid2str(_id) for _id in candidate_ids]
        params = {
            "company_id": uuid2str(company_id),
            "candidate_ids": candidate_ids
        }
        await EhrRequest("applicant_center").intranet("candidate/update_latest_activate_dt").post(data=params)

    @classmethod
    async def update_latest_follow_dt(cls, company_id: str, candidate_ids: list):
        """
        更新候选人的最新跟进时间
        @param company_id:
        @param candidate_ids:
        @return:
        """
        candidate_ids = [uuid2str(_id) for _id in candidate_ids]
        params = {
            "company_id": uuid2str(company_id),
            "candidate_ids": candidate_ids
        }
        await EhrRequest("applicant_center").intranet("candidate/update_last_follow_dt").post(data=params)


if __name__ == "__main__":
    async def helper():
        res = await CandidateService.get_candidate_by_name_and_mobile(
            "f79b05ee3cc94514a2f62f5cd6aa8b6e", "张力", "18829916141", auto_create=False
        )

        print(res)

    asyncio.get_event_loop().run_until_complete(helper())
