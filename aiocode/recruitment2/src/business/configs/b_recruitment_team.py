from services import svc


class RecruitmentTeamBusiness(object):

    @classmethod
    async def get_company_team(
            cls, company_id: str, participant_type: int, fields: list = None, participant_ids: list = None
    ):
        """
        获取企业招聘团队数据
        @param company_id:
        @param participant_type:
        @param fields:
        @param participant_ids:
        @return:
        """
        data = await svc.recruitment_team.get_participants(
            company_id, participant_type, fields, participant_ids=participant_ids
        )
        return data
