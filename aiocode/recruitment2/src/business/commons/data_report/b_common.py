from constants import ParticipantType
from services import svc


class CommonBusiness(object):
    @classmethod
    async def field_convert(cls, company_id, data):
        """
        字段转换接口
        hr_participant_ids：招聘HR id
        job_position_ids： 职位id
        channel_ids：渠道id
        emp_participant_ids：面试官id
        portal_page_ids：招聘门户id
        """
        results = {}

        if "hr_participant_ids" in data.keys() and data.get("hr_participant_ids", []):
            results["hr_participant_ids"] = await svc.recruitment_team.get_participants(
                company_id, ParticipantType.HR, fields=["id", "name"],
                participant_ids=data.get("hr_participant_ids", []))
        if "emp_participant_ids" in data.keys() and data.get("emp_participant_ids", []):
            results["emp_participant_ids"] = await svc.recruitment_team.get_participants(
                company_id, ParticipantType.EMPLOYEE, fields=["id", "name"],
                participant_ids=data.get("emp_participant_ids", []))
        if "job_position_ids" in data.keys() and data.get("job_position_ids", []):
            results["job_position_ids"] = await svc.job_position_search.get_positions_by_ids(
                company_id, data.get("job_position_ids", []), fields=["id", "name"]
            )
        if "channel_ids" in data.keys() and data.get("channel_ids", []):
            results["channel_ids"] = [dict(data) for data in await svc.recruit_channel.get_channel_list(
                company_id, ["id", "name"], ids=data.get("channel_ids", []))]
        if "portal_page_ids" in data.keys() and data.get("portal_page_ids", []):
            results["portal_page_ids"] = await svc.portal_page.get_portal_page(
                company_id, data.get("portal_page_ids", []), fields=["id", "name"])

        return results
