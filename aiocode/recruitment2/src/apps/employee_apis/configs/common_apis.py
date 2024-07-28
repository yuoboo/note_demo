# coding: utf-8
from business.commons import com_biz
from business.configs.b_common import CommonBusiness
from utils.api_auth import EmployeeBaseView


class HasHrView(EmployeeBaseView):
    async def get(self, request):
        data = await CommonBusiness.has_hr(
            request.ctx.user.company_id,
            request.ctx.user.emp_id
        )
        return self.data(data)


class SmsPlatformGetBalanceView(EmployeeBaseView):
    """
    获取企业短信余额接口
    """
    async def get(self, request):
        data = await com_biz.sms_platform.get_balance(request.ctx.user.company_id)
        return self.data({
            'balance': data
        })


class EmpShareShortUrlView(EmployeeBaseView):
    """
    生成分享短链接
    """
    async def post(self, request):
        url = request.json.get('url')
        short_url = await CommonBusiness.get_share_short_url(url)
        return self.data(short_url)


class EmpShareMiniQrCode(EmployeeBaseView):
    """
    生成分享小程序码
    """
    async def post(self, request):
        path = request.json.get('path')
        width = request.json.get('width', 280)
        key = CommonBusiness.make_key("%s/%s" % (path, width))
        qr_code = await CommonBusiness.get_share_mini_qrcode(key, path, width=width)
        return self.data(qr_code)


class HrPermissionView(EmployeeBaseView):
    """
    获取部分hr权限
    """
    async def get(self, request):
        company_id = request.ctx.user.company_id
        hr_id = await self.get_hr_id(request)

        try:
            interview_following = await self.has_hr_permission(company_id, hr_id, 'recruitment:interview_following')
        except:
            interview_following = False

        try:
            employed_following = await self.has_hr_permission(company_id, hr_id, 'recruitment:employed_following')
        except:
            employed_following = False

        try:
            common_operation = await self.has_hr_permission(company_id, hr_id, 'recruitment:common_operation')
        except:
            common_operation = False

        try:
            screen_resume = await self.has_hr_permission(company_id, hr_id, 'recruitment:screen_resume')
        except:
            screen_resume = False

        return self.data(
            {
                'interview_following': interview_following,
                'employed_following': employed_following,
                'common_operation': common_operation,
                'screen_resume': screen_resume
            }
        )
