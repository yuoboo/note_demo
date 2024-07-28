from configs import config
from utils.client import HttpClient
from utils.strutils import uuid2str


class PersonUCenterService(object):
    @classmethod
    async def wework_get_corp_accesstoken(cls, app_id, company_id):
        """
        通过应用id获取企业凭证
        """
        data = {
            'app_id': app_id,
            'company_id': company_id
        }

        http_url = '%s%s' % (config.PERSON_UCENTER_HOST, 'qyweixin/get_corp_accesstoken/')

        res = await HttpClient.get(http_url, params=data)
        if res and res['resultcode'] == 200:
            ret = res['data'] or {}
        else:
            ret = {}
        return ret.get('access_token', None)

    @classmethod
    async def wework_get_corp_users(cls, app_id, company_id, user_ids=[], employee_ids=[]):
        """
        获取授权企业员工信息
        注：如果有企业id则会取出指定企业的授权企业员工信息， 如果没有， 则会返回所有企业的授权企业员工信息
        """
        if not user_ids and not employee_ids:
            return []

        data = {
            'app_id': app_id,
            'company_id': company_id
        }

        if user_ids:
            data.update({
                'user_ids': user_ids
            })

        if employee_ids:
            data.update({
                'employee_ids': employee_ids
            })

        http_url = '%s%s' % (config.PERSON_UCENTER_HOST, 'qyweixin/get_corp_users/')

        res = await HttpClient.post(http_url, json_body=data)
        if res and res['resultcode'] == 200:
            ret = res['data'] or []
            if ret:
                for item in ret:
                    item['id'] = uuid2str(item.get('id', None))
                    item['employee_id'] = uuid2str(item.get('employee_id', None))
                    item['company_id'] = uuid2str(item.get('company_id', None))
        else:
            ret = []
        return ret

    @classmethod
    async def wework_get_suite_corp(cls, app_id, company_id):
        """
        获取企业应用授权信息
        """
        data = {
            'app_id': app_id,
            'company_id': company_id
        }

        http_url = '%s%s' % (config.PERSON_UCENTER_HOST, 'qyweixin/get_suite_corp/')

        res = await HttpClient.get(http_url, params=data)
        if res and res['resultcode'] == 200:
            ret = res['data'] or {}
        else:
            ret = {}
        return ret

    @classmethod
    async def wework_get_core_suite_info(cls, suite_id, corp_id):
        """
        获取企业微信应用信息
        """
        data = {
            'suite_id': suite_id,
            'corp_id': corp_id
        }

        http_url = '%s%s' % (config.PERSON_UCENTER_HOST, 'qyweixin/get_core_suite_info/')

        res = await HttpClient.get(http_url, params=data)
        if res and res['resultcode'] == 200:
            ret = res['data'] or {}
        else:
            ret = {}
        return ret
