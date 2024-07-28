from services import svc
from services.s_dbs.config.s_recruitment_team import participant_tbu


class RecruitmentTeamBiz:
    @staticmethod
    async def get_participants_for_intranet(
            company_id: str, participant_type: int = None, fields: list = None
    ) -> list:
        """参与者内部接口"""
        if fields:
            tb_keys = participant_tbu.tb_keys
            fields = set(fields) & set(tb_keys)
        else:
            fields = ["id", "participant_type", "participant_refer_id", "participant_refer_status", "name",
                      "avatar", "mobile", "email", "department_id", "department_name", "job_id", "job_name"]
        return await svc.recruit_team.get_all_participants(company_id, participant_type, fields)

