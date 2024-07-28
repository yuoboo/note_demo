from collections import defaultdict

from bs4 import BeautifulSoup

from kits.exception import APIValidationError
from services import svc
from services.s_https.s_common import get_qiniu_file_info
from services.s_https.s_sensitive import SensitiveService


class EmailTemplateBusiness(object):

    @classmethod
    async def create_template(cls, company_id: str, user_id: str, validated_data: dict):
        data = await svc.email_template.create_email_template(
            company_id, user_id, validated_data
        )

        return data

    @classmethod
    async def _template_attachments(cls, template_ids: list):
        """
        获取模板附件信息
        @param template_ids:
        @return:
        """
        template_id2attachments = defaultdict(list)
        attachments = await svc.email_template.get_template_attachments(template_ids)
        file_keys = [t.get("file_key") for t in attachments]
        if file_keys:
            file_data = await get_qiniu_file_info(file_keys)
            key2url = {item["key"]: item["url"] for item in file_data}
            for att in attachments:
                template_id2attachments[att.get("email_template_id")].append(
                    {
                        "file_name": att.get("file_name"),
                        "file_size": att.get("file_size"),
                        "file_type": att.get("file_type"),
                        "file_key": att.get("file_key"),
                        "file_url": key2url.get(att.get("file_key"))
                    }
                )

        return template_id2attachments

    @classmethod
    async def get_templates(cls, company_id: str, user_id: str, params: dict):
        """
        获取模板列表
        @param company_id:
        @param user_id:
        @param params:
        @return:
        """
        data = await svc.email_template.get_email_templates(
            company_id, params.get("usage"), params
        )
        if not data:
            await svc.email_template.create_default_templates(company_id, user_id, params.get("usage"))
            data = await svc.email_template.get_email_templates(
                company_id, params.get("usage"), params
            )
        template_ids = [item.get("id") for item in data]
        template_id2attachments = await cls._template_attachments(template_ids)

        for item in data:
            item["attaches"] = template_id2attachments.get(item["id"]) or []

        return data

    @classmethod
    async def _check_sensitive_word(cls, email_title: str, email_content: str):
        """
        检查敏感词
        @param email_title:
        @param email_content:
        @return:
        """
        check_str = email_title
        soup = BeautifulSoup(email_content, 'html.parser')
        p_tags = soup.find_all('p')
        for p in p_tags:
            check_str += p.text.strip().replace(' ', '')
        sensitive_words = await SensitiveService.get(check_str, 1)
        if sensitive_words:
            raise APIValidationError(14002, msg=f"{','.join(sensitive_words)}是违禁词语，请勿在邮件内添加!")

    @classmethod
    async def update_template(cls, company_id: str, user_id: str, validated_data: dict):
        """
        更新邮件模板
        @param company_id:
        @param user_id:
        @param validated_data:
        @return:
        """

        email_title = validated_data.get("email_title")
        email_content = validated_data.get("email_content")
        attachments = validated_data.pop("attaches", [])

        await cls._check_sensitive_word(email_title, email_content)
        await svc.email_template.update_email_template(
            company_id, user_id, validated_data
        )
        await svc.email_template.create_template_attachments(
            validated_data.get("id"), attachments
        )

        return validated_data.get("id")

    @classmethod
    async def delete_template(cls, company_id: str, user_id: str, template_id: str):
        """
        删除邮件模板
        @param company_id:
        @param user_id:
        @param template_id:
        @return:
        """
        await svc.email_template.delete_email_template(
            company_id, user_id, template_id
        )

        return template_id
