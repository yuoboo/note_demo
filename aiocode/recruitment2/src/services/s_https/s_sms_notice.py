from configs import config
from kits.exception import APIValidationError
from utils.client import HttpClient
from utils.ehr_request import EhrRequest
from utils.logger import app_logger
from utils.strutils import uuid2str


async def get_company_sms_action_code(company_id: str) -> str:
    """
    获取企业的短信模板
    """
    res = await EhrRequest("sms_platform").intranet('custom_template').get(
        data={"company_id": uuid2str(company_id)}
    )
    if not res or res.get("resultcode") != 200:
        data = "2haohr_common"
    else:
        data = res.get("data") or "2haohr_common"

    return data


async def send_sms_by_action_code(
        action_code: str, company_id: str, total_amount: int, message_body: list,
        sms_type: int = 0, task_id: str = "", user_id: str = "", module_code: str = "",
        func_module: str = "", biz_func: str = "", func_page: str = ""
):
    """
    根据action_code发送付费短信
    @param action_code:
    @param company_id:
    @param total_amount:
    @param message_body:
    @param sms_type:
    @param task_id:
    @param user_id:
    @param module_code:
    @param func_module:
    @param biz_func:
    @param func_page:
    @return:
    """

    data = {
        "action_code": action_code,
        "company_id": str(company_id),
        "total_amount": total_amount,
        "sms_type": sms_type,
        "messagebody": message_body,
        "task_id": str(task_id) if task_id else task_id,
        "user_id": str(user_id) if user_id else user_id,
        "module_code": module_code,
        "project_name": config.get("PROJECT_NAME") or "eebo.ehr.recruitment2",
        "project_code": "CHR003",
        "function_module": func_module,
        "business_function": biz_func,
        "function_page": func_page
    }
    res = await EhrRequest("sms").bp_inner_gateway("pay/template/system_send").post(data=data)
    if res:
        return res
    raise Exception('短信服务子系统发送系统模板付费短信失败')


async def get_template_by_id(company_id: str, _id: int):
    """
    根据id获取短信模板
    @param company_id:
    @param _id:
    @return:
    """
    api_host = config.get("EHR_API_HOSTS")
    api_url = f'{api_host}v1/blesssms_service/get_template/'
    headers = {
        'x-authkey': "0h!g3i!n)-e@3)^qr4lsr-iqdo3nee@o0k*2!zg!)%%78v4fowfn3^p(y31i0-i3u*9hj&vv*f4cf=1c@t$&qx54v)62jhd^c^sp!nmce2v$%+yq#*a+z_m%l^@8wphd60hj*5u!acxl-b!yhwi5j0"
    }
    data = {"id": _id, "company_id": uuid2str(company_id)}
    res = await HttpClient.post(api_url, json_body=data, headers=headers)
    if not res or res.get("resultcode") != 200:
        app_logger.error(f"获取企业短信模板失败，body:{data},header:{headers}, url:{api_url}, 返回:{res}")
        raise APIValidationError(msg="获取短信模板失败")
    return res.get("data") or {}


async def send_sms_by_action_code_for_free(
        action_code: str, company_id: str, mobile: str, message_body: dict,
        module_code: str = "", event_id: int = None, biz_id: str = ""

):
    """
    根据action_code发送免费短信
    @param action_code:
    @param company_id:
    @param mobile:
    @param message_body:
    @param module_code:
    @param event_id:
    @param biz_id:
    @return:
    """

    data = {
            "mobile": mobile,
            "actioncode": action_code,
            "messagebody": message_body,
            "company_id": uuid2str(company_id),
            "module": module_code,
            "project_name": 'eebo.ehr.recruitment2',
            "event_id": event_id,
            "biz_id": biz_id
    }
    res = await EhrRequest("sms").bp_inner_gateway("single/send").post(data=data)
    if not res or res.get("resultcode") != 200:
        raise Exception('短信服务子系统发送系统模板免费短信失败')
