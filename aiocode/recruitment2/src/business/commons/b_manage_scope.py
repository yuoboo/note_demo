from services import svc


class ManageScopeBusiness(object):

    @classmethod
    async def hr_manage_scope(cls, company_id: str, user_id: str):
        """
        获取指定HR用户的管理范围
        @param company_id:
        @param user_id:
        @return:
        """
        data = await svc.manage_scope.hr_manage_scope(company_id, user_id)

        return data
