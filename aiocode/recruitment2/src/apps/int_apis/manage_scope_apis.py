from business import biz
from utils.api_auth import BaseView
from utils.strutils import uuid2str


class HrManageScopeView(BaseView):

    async def get(self, request):
        """
        获取HR的管理范围
        """
        company_id = uuid2str(request.args.get("company_id"))
        user_id = uuid2str(request.args.get("user_id"))
        if not all([company_id, user_id]):
            return self.error("参数缺失")

        data = await biz.manage_scope.hr_manage_scope(company_id, user_id)

        return self.data(data)
