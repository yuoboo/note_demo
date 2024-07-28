from business import biz
from services.s_https.s_ucenter import get_company_for_share_id
from utils.api_auth import BaseView
from utils.strutils import uuid2str


class ActivateLinkReadView(BaseView):
    """
    激活链接访问
    """
    async def get(self, request):
        share_id = uuid2str(request.args.get("share_id"))
        activate_record_id = uuid2str(request.args.get("activate_record_id"))

        if not all([share_id, activate_record_id]):
            return self.error("参数错误")

        company = await get_company_for_share_id(share_id)
        if not company:
            return self.error("企业不存在")
        data = await biz.activate_record.activate_link_view(
            uuid2str(company.id), activate_record_id
        )

        return self.data(data)
