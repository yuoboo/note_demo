# coding: utf-8
import asyncio
import hashlib
import json

import aiohttp
from constants import QrCodeSignType, BgCheckStatus, TalentAssessmentStatus
from drivers.redis import redis_db
from utils.client import HttpClient
from utils.ehr_request import EhrRequest
from utils.logger import app_logger


async def create_qr_code(
        scene_data: dict, sign_type=QrCodeSignType.EMPLOYMENT_FORM, app_id=1010, page='pages/home/index', width=None
) -> str:
    """
    生成小程序码
    由于历史的设计，sign分别为0 1 2 3时， scene_data的数据结构应为{'id': "", 'share_id': "","record_id": ""}，
    具体各字段意义见各使用场景， 后期新加的场景建议字段名为有意义的变量，具体应包含什么样的参数，由自己的业务自行决定。
    app_id和page默认参数为应聘助手小程序的参数， 如果需要生成其他小程序码需要自行传相应参数过来
    """

    scene_data["sign"] = sign_type
    params_data = {
        "app_id": app_id,
        "params": {
            'scene': scene_data,
            'page': page
        }
    }
    if width:
        params_data['params']['width'] = width

    count = 1
    while count <= 3:
        res = await EhrRequest("person_ucenter").intranet(
            "wechat_central_control/create_miniprogram_qrcode"
        ).post(data=params_data)
        if not res or res["resultcode"] != 200:
            app_logger.error(f"生成小程序码失败啦，返回{res}")
            count += 1
        else:
            url, _ = res.get('data')
            return url
    raise Exception(f"生成小程序码失败了，请求参数：{params_data}")


async def create_short_url(url: str, remark='') -> str:
    data = {
        'url': url,
        'remark': remark
    }
    http_url = 'http://2haohr.cn/api/v1/shorturl.json'

    res = await HttpClient.post(http_url, data=json.dumps(data))
    if not res or not res.get("result"):
        return url

    return res['data']['url']


async def get_bg_check_status(company_id, datas):
    """
    获取背调状态
    :@param datas: 格式 {'id': 'candidate_record_id', 'name': name, 'credentials_no': credentials_no}
    """
    if not datas:
        return {}

    keys = []
    for data in datas:
        key = '{}{}{}'.format(company_id, data.get('name', ''), data.get('credentials_no', None))
        keys.append('ehr:api:background_check:{}'.format(hashlib.md5(key.encode()).hexdigest()))

    client = await redis_db.default_redis
    pipe = client.pipeline()
    for key in keys:
        pipe.get(key)
    results = await pipe.execute()
    bg_check_status = {}
    for idx, value in enumerate(results):
        if value:
            bg_check_status[datas[idx].get('id')] = value
        else:
            bg_check_status[datas[idx].get('id')] = BgCheckStatus.unsent
    return bg_check_status


async def get_talent_assessment_status(company_id, datas):
    """
    获取人才测评状态
    @param datas: 格式{'id': 'candidate_record_id', 'name': name, 'mobile': mobile}
    @return:
    """
    keys = []
    for data in datas:
        key = '{}{}{}'.format(company_id, data.get('name', ''), data.get('mobile', None))
        keys.append('ehr:api:assessment:{}'.format(hashlib.md5(key.encode()).hexdigest()))

    client = await redis_db.default_redis
    pipe = client.pipeline()
    for key in keys:
        pipe.get(key)
    results = await pipe.execute()
    talent_assessment_status = {}
    for idx, value in enumerate(results):
        if value:
            talent_assessment_status[datas[idx].get('id')] = int(value)
        else:
            talent_assessment_status[datas[idx].get('id')] = TalentAssessmentStatus.unsent
    return talent_assessment_status


async def check_sensitive_word(word: str):
    """
    @desc 检查敏感词汇
    """
    data = {
        "text": word,
        "type": 1
    }

    res = await EhrRequest("sensitive").intranet("hasSensitiveWordsWithType").post(data=data)

    if not res or res["resultcode"] != 200:
        return []

    weak_words = [item["name"] for item in res.get("data")]
    return weak_words


async def get_user_qrcode(company_id: str, user_id: str):
    """
    @desc 获取二维码
    """
    if not (company_id and user_id):
        return ""

    url = ""
    return url


async def get_ip():
    async with aiohttp.ClientSession() as client:
        async with client.get('https://checkip.amazonaws.com') as resp:
            return await resp.text()


async def get_sms_platfor_company_sms_balance(company_id: str):
    """
    获取企业短信余额接口
    :param company_id: 企业id
    :return:
    """
    data = {
        'company_id': str(company_id)
    }
    res = await EhrRequest("sms_platform").intranet("company_sms_balance").get(data=data)
    if not res or res['resultcode'] != 200:
        raise Exception('短信平台 - 通过企业id获取企业短信余额接口，对接返回错误码 %s' % res.status_code)

    return res.get("data", {}).get('balance', 0)


async def get_qiniu_file_info(file_keys: list):
    """
    获取七牛文件信息
    @param file_keys:
    @return:
    """
    params = {
        "keys": file_keys
    }
    res = await EhrRequest("store_service").intranet("qiniu/get_view_url").post(data=params)
    if not res or res["resultcode"] != 200:
        raise Exception("获取七牛文件信息失败")

    return res.get("data")

if __name__ == "__main__":
    async def helper():
        res = await create_qr_code({"id": "12345567890"})
        print(res)

        r = await create_short_url('http://h5.2haohr.com/browser/static-recruitment.html?id=c3feb6fb31014d6fa37ed7b356cef6d5')
        print(r)

    asyncio.get_event_loop().run_until_complete(helper())
