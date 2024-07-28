# coding: utf-8
from utils.ehr_request import EhrRequest
from utils.strutils import uuid2str


class InterviewService(object):

    @classmethod
    async def get_latest_interview_info(
            cls, company_id: str,
            candidate_record_ids: list,
            is_interview_pariticipant: bool = False,
            is_interview_information: bool = False
    ) -> dict:
        """
        获取面试日程信息
        """
        params = {
            "company_id": uuid2str(company_id),
            "candidate_record_ids": candidate_record_ids,
            "is_interview_pariticipant": is_interview_pariticipant,
            'is_interview_information': is_interview_information
        }

        res = await EhrRequest("recruitment").intranet("latest_interview_info").post(data=params)
        if res and res['resultcode'] == 200:
            ret = res['data'] or {}
        return ret
