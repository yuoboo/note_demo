import json
import logging
from hashlib import md5

from constants import redis_keys
from drivers.redis import redis_db
from services.s_https.s_person_ucenter import PersonUCenterService
from utils.client import HttpClient

logger = logging.getLogger('app')


class WeWorkService(object):
    BASE_URL = 'https://qyapi.weixin.qq.com/cgi-bin/'

    def __init__(self, app_id, company_id):
        """
        @param app_id: 应用id
        @param company_id: 企业id
        """
        self.app_id = app_id
        self.company_id = company_id
        self._accesstoken = None

    async def get_token(self):
        """
        获取企业微信accesstoken
        """
        if self._accesstoken:
            return self._accesstoken
        self._accesstoken = await PersonUCenterService.wework_get_corp_accesstoken(
            app_id=self.app_id,
            company_id=self.company_id
        )
        return self._accesstoken

    async def is_app(self):
        """
        是否存在企业微信应用配置
        """
        param_str = '%s%s' % (self.app_id, self.company_id)
        md5_has = md5()
        md5_has.update(param_str.encode(encoding='utf-8'))
        params_md5 = md5_has.hexdigest()
        cache_key = redis_keys.RECRUITMENT_WEWORK_IS_APP[0].format(
            params_md5=params_md5
        )
        redis_cli = await redis_db.default_redis
        is_app = await redis_cli.get(cache_key)
        if is_app is None:
            if await self.get_suite_corp():
                is_app = '1'
                await redis_cli.set(cache_key, is_app, expire=redis_keys.RECRUITMENT_WEWORK_IS_APP[1])
        return is_app == '1'

    async def get_suite_corp(self):
        """
        获取企业应用授权信息
        @return:
        """
        return await PersonUCenterService.wework_get_suite_corp(
            app_id=self.app_id,
            company_id=self.company_id
        )

    async def get_corp_users(self, user_ids=None, employee_ids=None):
        """
        获取授权企业员工信息
        注：如果有企业id则会取出指定企业的授权企业员工信息， 如果没有， 则会返回所有企业的授权企业员工信息
        """
        return await PersonUCenterService.wework_get_corp_users(
            app_id=self.app_id,
            company_id=self.company_id,
            user_ids=user_ids,
            employee_ids=employee_ids
        )


class WeWorkExternalContactService(WeWorkService):
    async def get_follow_user_list(self):
        """
        获取配置了客户联系功能的成员列表
        """
        data = {
            'access_token': await self.get_token()
        }
        http_url = '%s%s' % (self.BASE_URL, 'externalcontact/get_follow_user_list')

        res = await HttpClient.get(http_url, params=data)
        if res and res['errcode'] == 0:
            ret = res.get('follow_user', [])
        else:
            logger.error("企业微信 获取配置了客户联系功能的成员列表错误 %s" % json.dumps(res))
            ret = []
        return ret

    async def add_contact_way(self, data):
        """
        配置客户联系「联系我」方式
        """
        http_url = '%s%s?access_token=%s' % (
            self.BASE_URL,
            'externalcontact/add_contact_way',
            await self.get_token()
        )

        res = await HttpClient.post(http_url, json_body=data)
        if res and res['errcode'] == 0:
            ret = res
        else:
            logger.error("企业微信 配置客户联系「联系我」方式错误 %s" % json.dumps(res))
            ret = {}
        return ret

    async def list(self, userid):
        """
        获取客户列表
        """
        data = {
            'access_token': await self.get_token(),
            'userid': userid
        }
        http_url = '%s%s' % (self.BASE_URL, 'externalcontact/list')

        res = await HttpClient.get(http_url, params=data)
        if res and res['errcode'] == 0:
            ret = res.get('external_userid', [])
        else:
            logger.error("企业微信 获取获取客户列表错误 %s" % json.dumps(res))
            ret = []
        return ret

    async def get(self, external_userid):
        """
        获取客户详情
        """
        data = {
            'access_token': await self.get_token(),
            'external_userid': external_userid
        }
        http_url = '%s%s' % (self.BASE_URL, 'externalcontact/get')

        res = await HttpClient.get(http_url, params=data)
        if res and res['errcode'] == 0:
            ret = res
        else:
            logger.error("企业微信 获取客户详情错误 %s" % json.dumps(res))
            ret = {}
        return ret

    async def get_external_contact(self, external_userid: str) -> dict:
        """
        获取外部联系人基本信息
        :returns {
                    'external_userid': 'wmEKyIDQAAnuhO2rppkTsfnEbmBEw-QQ',
                    'name': 'Joe',
                    'type': 1,
                    'gender': 1,
                    'unionid': 'oJ3FUtxtLH42Fxv9IJ_0SMQ1hvTs'
                }
        """
        external = await self.get(external_userid)
        return external.get("external_contact") or dict()

    async def get_unionid(self, external_userid: str) -> str:
        """
        通过外部联系人id获取微信 unionid
        """
        _ex = await self.get_external_contact(external_userid)
        return _ex.get("unionid") or ""
