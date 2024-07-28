# coding: utf-8
from configs import config
from business.configs.b_common import CommonBusiness
from kits.exception import APIValidationError
from utils.api_auth import BaseView


class ShareShortUrlView(BaseView):
    """
    生成分享短链接
    """
    async def post(self, request):
        allow_urls = [
            config.get('EMPLOY_ASSISTANT_URL'),
            '2haohr.com/',
            '2haohr.cn/'
        ]
        url = request.json.get('url')
        allow = [allow_url in url for allow_url in allow_urls]
        if not any(allow):
            raise APIValidationError(101201, msg="链接不合法")

        short_url = await CommonBusiness.get_share_short_url(url)
        return self.data(short_url)


class ShareMiniQrCode(BaseView):
    """
    生成分享小程序码
    """
    async def post(self, request):
        path = request.json.get('path')
        width = request.json.get('width', 280)
        key = CommonBusiness.make_key("%s/%s" % (path, width))
        qr_code = await CommonBusiness.get_share_mini_qrcode(key, path, width=width)
        return self.data(qr_code)
