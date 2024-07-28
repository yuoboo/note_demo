import hashlib
from urllib.parse import parse_qsl

from constants import QrCodeSignType
from services import svc
from services.s_dbs.s_common import ShareShortUrlService, ShareMiniQrCodeService
from services.s_https.s_common import create_short_url, create_qr_code


class CommonBusiness(object):
    @classmethod
    def make_key(cls, key):
        return hashlib.md5(key.encode('utf-8')).hexdigest()

    @classmethod
    async def has_hr(cls, company_id: str, emp_id: str) -> bool:
        """
        验证员工是否存在招聘HR身份
        @param company_id: 企业id
        @param emp_id: 员工id
        @return:
        """
        hr_id = await svc.manage_scope._get_user_id_by_emp_id(company_id, emp_id)
        return bool(hr_id)

    @classmethod
    async def get_hr_by_emp_id(cls, company_id: str, emp_id: str) -> str:
        """
        通过员工id获取hr id
        @param company_id:
        @param emp_id:
        @return:
        """
        return await svc.manage_scope._get_user_id_by_emp_id(company_id, emp_id)

    @classmethod
    async def get_share_short_url(cls, url):
        """
        获取分享链接的短链接
        :param url:
        :return:
        """
        key = hashlib.md5(url.encode('utf-8')).hexdigest()
        result = await ShareShortUrlService.get_by_key(key)
        if result:
            return result.get('short_url', None)

        short_url = await create_short_url(url)
        await ShareShortUrlService.create(key, url, short_url)
        return short_url

    @classmethod
    async def get_share_mini_qrcode(cls, key, path, app_id=1010, width=280, sign_type=QrCodeSignType.RECRUIT_PORTAL):
        """
        获取分享小程序码
        :param key:
        :param path:
        :param width: 二维码宽度
        :param sign_type: 类型QrCodeSignType
        :return:
        """
        result = await ShareMiniQrCodeService.get_by_key(key)
        if result:
            return result.get('qr_code', None)

        data = {}

        if '?' in path:
            path, params = path.split('?')
            data = dict(parse_qsl(params))

        qr_code = await create_qr_code(data, sign_type, app_id=app_id, page=path, width=width)
        await ShareMiniQrCodeService.create(key, path, qr_code)
        return qr_code
