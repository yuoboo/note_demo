import copy
import logging

from configs import config
from utils.ehr_request import EhrRequest
from utils.strutils import uuid2str

logger = logging.getLogger('app')


async def send_mail_by_company_email(
        send_email_id: str, recipients: list, email_title: str,
        email_content: str, company_id: str, user_id: str, **kwargs
):
    """
    使用企业的邮箱进行邮件发送
    @param send_email_id:
    @param recipients:
    @param email_title:
    @param email_content:
    @param company_id:
    @param user_id:
    @param kwargs:
    @return:
    """
    files = kwargs.get("files") or []
    attachments = [item.get("key") if "key" in item else item.get("file_key") for item in files] if files else []
    env_mode = config.get("APP_ENV")
    if env_mode in ('local', 'dev'):
        origin_recipients = copy.copy(recipients)
        recipients = [
            {'name': '招聘dev收件组', 'address': 'recruitment-dev@eebochina.com'}
        ]
        email_title = '{}[招聘子系统{}环境统一转发], 原收件人: {}'.format(email_title, env_mode, origin_recipients)
        attachments = []
    elif env_mode == 'test':
        origin_recipients = copy.copy(recipients)
        recipients = [
            {'name': '招聘test收件组', 'address': 'recruitment-test@eebochina.com'}
        ]
        email_title = '{}[招聘子系统{}环境统一转发], 原收件人: {}'.format(email_title, env_mode, origin_recipients)

    from_email = None if send_email_id else "service@2haojobs.com"
    data = {
        "record_id": uuid2str(send_email_id),
        "from_email": from_email,
        "subject": email_title,
        "recipients": recipients,
        "cc": kwargs.get('cc_list') or [],
        "bcc": kwargs.get("bcc_list") or [],
        "attachments": attachments,
        "company_id": uuid2str(company_id),
        "user_id": uuid2str(user_id),
        "email_type": kwargs.get("email_type") or '招聘系统',
        "body": email_content,
        "project_code": "CHR003",
        "project_name": "招聘",
        "module_code": kwargs.get("module_code") or "CHR003-001",
        "module_name": kwargs.get("module_name") or "候选人管理",
        "function_code": kwargs.get("function_code") or "CHR003-001-001",
        "function_name": kwargs.get("function_name") or "CHR003-001",
        "notify_url": "/recruitment2/email_notify_callback/",  # 回调地址
        "callback_data": kwargs.get("callback_data") or {},  # 回调数据
        "file_in_qiniu": True
    }
    res = await EhrRequest("company_setting").intranet("company_send_email").post(data=data)
    if not res or res["resultcode"] != 200:
        logger.error(f'邮件发送失败，发送参数：{data}, 返回：{res}')
