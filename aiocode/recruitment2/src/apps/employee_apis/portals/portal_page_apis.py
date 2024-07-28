from business import biz
from configs import config
from services.s_https.s_ucenter import get_company_for_id
from utils.api_auth import EmployeeBaseView
from utils.strutils import uuid2str


class EmpPortalPageBasicView(EmployeeBaseView):
    """
    获取招聘门户网页基础信息，用于前端筛选
    """
    async def get(self, request):
        company_id = uuid2str(request.ctx.user.company_id)

        data = await biz.portal_page.find_portal_page_basic(company_id)
        return self.data(data)


class EmpPortalCompanyIntroView(EmployeeBaseView):
    """
    招聘门户企业介绍
    """

    async def get(self, request):
        portal_id = request.args.get("portal_id")
        if not portal_id:
            return self.error("参数缺失")
        data = await biz.portal_page.portal_company_intro(
            request.ctx.user.company_id, portal_id
        )
        return self.data(data)


class ReferralEmployeeDetailView(EmployeeBaseView):
    """
    @desc 获取内推人信息
    """
    async def get(self, request):
        company_id = request.ctx.user.company_id
        employee_id = request.ctx.user.emp_id
        res = await biz.portal_page.get_referral_employee_info(company_id, employee_id)
        return self.data(res)


class ReferralEmployeeUpdateView(EmployeeBaseView):
    """
    @desc 修改内推人信息（联系二维码等）
    """
    async def post(self, request):
        company_id = request.ctx.user.company_id
        employee_id = request.ctx.user.emp_id

        data = {
            "employee_id": employee_id,
            "qrcode_type": request.json.get("qrcode_type", 0),
            "qrcode_url": request.json.get("qrcode_url", "")
        }
        res = await biz.portal_page.update_referral_employee_info(company_id, data)
        return self.data(res)


class EmpReferralConfigView(EmployeeBaseView):
    """
    内推说明信息View
    """
    async def get(self, request):
        """
        获取内推说明信息
        @param request:
        @return:
        """
        data = await biz.referral_config.get_referral_config(request.ctx.user.company_id)
        company = await get_company_for_id(request.ctx.user.company_id)
        logo_key = company.get("logo_key")
        logo_url = config.get("QINIU_PUBLIC_DOMAIN") + logo_key if logo_key else ""
        data.update(
            {
                "employee_id": request.ctx.user.emp_id,
                "com_share_id": company.get("share_id"),
                "com_fullname": company.get("fullname"),
                "com_shortname": company.get("shortname"),
                "com_logo_url": logo_url
            }
        )

        return self.data(data)
