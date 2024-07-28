# coding: utf-8
import asyncio

import ujson

from constants import redis_keys
from drivers.redis import redis_db
from utils.ehr_request import EhrRequest
from utils.strutils import uuid2str


class BasicCompany(dict):
    def __getattr__(self, key):
        return self.get(key, None)


class BasicCompanyUser(dict):
    def __getattr__(self, key):
        return self.get(key, None)


async def get_company_for_share_id(share_id: str):
    """
    通过分享id获取企业信息
    :param share_id: 企业编码列表
    :return:
    """
    data = {
        'share_id': str(share_id)
    }
    res = await EhrRequest("ucenter").intranet("company/get_share").post(data=data)
    if not res or res['resultcode'] != 200:
        raise Exception('用户中心通过分享id获取企业信息错误，对接返回错误码 %s' % res.status_code)

    return BasicCompany(res.get("data") or {})


async def get_company_for_id(company_id: str) -> dict:
    """
    获取企业信息
    :param company_id: 企业id
    :return:
    """
    company_list = await get_company_for_ids([company_id])
    if company_list:
        return company_list[0]
    return {}


async def get_company_source(company_id: str):
    """
    版本
    :param company_id:
    :return:
    """
    company = await get_company_for_id(company_id)
    if company:
        source = company.get('source', 0)
        if source == 7:
            return 'feishu'
        elif source == 8:
            return 'wework'
        else:
            return 'saas'
    return None


async def get_company_for_ids(company_ids: list) -> list:
    """
    批量获取企业列表信息
    :param company_ids: 企业id列表
    :return:
    """
    if len(company_ids) > 100 or len(company_ids) == 0:
        raise Exception('用户中心批量获取企业列表信息接口最大100条数据且不能为空， 当前 %s 条' % len(company_ids))
    data = {
        'ids': list(set([uuid2str(c_id) for c_id in company_ids]))
    }
    res = await EhrRequest("ucenter").intranet("company/batch").post(data=data)
    if not res or res["resultcode"] != 200:
        raise Exception(f'用户中心批量获取企业列表信息错误，对接返回错误码{res["resultcode"]}')

    data_list = res.get("data") or []
    return [BasicCompany(row) for row in data_list]


async def get_company_user(company_id, user_id=None, hr_id=None):
    """
    批量获取企业用户信息
    """
    company_id = uuid2str(company_id)
    user_id = uuid2str(user_id)
    hr_id = uuid2str(hr_id)

    params = {
        "user_id": user_id or "",
        "company_id": company_id or "",
        "hr_id": hr_id or ""
    }
    res = await EhrRequest("ucenter").intranet("company_user").get(data=params)

    if not res or res["resultcode"] != 200:
        raise Exception(f'用户中心批量获取企业列表信息错误，对接返回错误码{res}')

    data = res.get("data", [])
    res = []
    for row in data:
        obj = BasicCompanyUser(row)
        obj.__setattr__("company_id", obj.company)
        obj.__setattr__("user_id", obj.user)
        res.append(obj)
    return res


async def get_users(ids):
    """
    批量获取用户列表信息
    :param ids: 用户id列表
    :return:
    """
    ids = [user_id for user_id in ids if user_id]

    if not ids:
        return []

    results = []
    new_ids = []

    client = await redis_db.common_redis
    res = await client.hmget(redis_keys.RECRUIT_UCENTER_USER_INFO, *ids)

    for idx, item in enumerate(res):
        if item:
            results.append(ujson.loads(item))
        else:
            new_ids.append(ids[idx])

    if new_ids:
        data = {
            'ids': new_ids
        }
        res = await EhrRequest("ucenter").intranet("user/batch").post(data=data)
        if not res or res["resultcode"] != 200:
            raise Exception(f'用户中心批量获取企业列表信息错误，对接返回错误码{res}')

        redis_params = []
        for item in res.get("data", []):
            results.append(item)
            redis_params.append(uuid2str(item.get('id')))
            redis_params.append(ujson.dumps(item))
        if redis_params:
            await client.hmset(redis_keys.RECRUIT_UCENTER_USER_INFO, *redis_params)

    return results


async def get_user(user_id):
    users = await get_users([uuid2str(user_id)])
    return users[0] if users else dict()
