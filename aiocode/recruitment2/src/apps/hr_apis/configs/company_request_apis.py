# coding: utf-8
from business.configs.b_company_request import CompanyRequestBusiness
from utils.api_auth import HRBaseView


class CompanyRequestView(HRBaseView):
    async def get(self, request):
        """
        获取企业开通信息
        """
        data = await CompanyRequestBusiness.get_info(request.ctx.company_id)
        return self.data(data)

    async def post(self, request):
        """
        创建企业开通
        """
        await CompanyRequestBusiness.open(request.ctx.company_id, request.ctx.user_id)
        return self.data({"result": True})
