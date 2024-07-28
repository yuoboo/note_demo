# coding: utf-8
from business import PortalWeWorkBusiness
from business.b_wework import WeWorkBusiness
from business.commons.b_sensitive import SensitiveBusiness
from business.configs.b_common import CommonBusiness
from utils.api_auth import HRBaseView


class ShareShortUrlView(HRBaseView):
    """
    生成分享短链接
    """
    async def post(self, request):
        url = request.json.get('url')
        short_url = await CommonBusiness.get_share_short_url(url)
        return self.data(short_url)


class ShareMiniQrCode(HRBaseView):
    """
    生成分享小程序码
    """
    async def post(self, request):
        path = request.json.get('path')
        width = request.json.get('width', 280)
        key = CommonBusiness.make_key("%s/%s" % (path, width))
        qr_code = await CommonBusiness.get_share_mini_qrcode(key, path, width=width)
        return self.data(qr_code)


class SensitiveView(HRBaseView):
    """
    验证敏感词
    """
    async def post(self, request):
        text = request.json.get('text', None)
        type = request.json.get('type', [])
        sensitive = await SensitiveBusiness.get(text, type)
        return self.data(sensitive)


class MyQrCodeView(HRBaseView):
    """
    获取当前HR的企业微信二维码
    """
    async def get(self, request):
        company_id = request.ctx.company_id
        user_id = request.ctx.user_id
        app_id = await WeWorkBusiness.get_company_app_id(company_id)
        qr_code = await PortalWeWorkBusiness.get_hr_qr_code(app_id, company_id, user_id)
        return self.data({"qr_code": qr_code})
