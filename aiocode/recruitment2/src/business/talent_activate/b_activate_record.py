import datetime
from asyncio import gather
from datetime import date
from urllib.parse import urlencode

import ujson

from celery_worker import celery_app
from configs import config
from constants import ParticipantType, ActivateNotifyWay, NoticeCallBackType
from constants.redis_keys import TALENT_ACTIVE_TRY_NOTICE
from drivers.redis import redis_db
from kits.exception import APIValidationError
from services import svc
from services.s_https.s_sms_notice import send_sms_by_action_code_for_free

from utils.strutils import gen_uuid, uuid2str


class ActivateRecordBusiness(object):
    """
    人才激活记录业务类
    """

    @staticmethod
    async def _get_activate_url(
            share_id: str, channel_id: str, portal_id: str, portal_position_id: str, activate_id: str
    ):
        """
        获取激活短信链接
        @param share_id:
        @param channel_id:
        @param portal_id:
        @param portal_position_id:
        @param activate_id:
        @return:
        """
        base_url = config.get("EMPLOY_ASSISTANT_URL")
        if portal_position_id:
            h5_url = config.get("PORTAL_POSITION_H5_URL")
            h5_url = h5_url.format(
                position_record_id=portal_position_id, portal_id=portal_id,
                channel_id=channel_id or "", share_id=share_id
            )
        else:
            h5_url = config.get("PORTAL_HOME_H5_URL")
            h5_url = h5_url.format(
                portal_id=portal_id, channel_id=channel_id or "", share_id=share_id
            )
        h5_url = f'{h5_url}&activate_id={activate_id}'
        redirect_url = urlencode({"url": "/pages/sms-web/index?url={}".format(h5_url)})
        url = "{}&{}".format(base_url, redirect_url)
        short_url = await svc.http_common.create_short_url(url)

        return short_url

    @staticmethod
    def _cal_sms_amount(content):
        """
        计算单挑短信需要扣除的额度
        @param content:
        @return:
        """
        content_l = len(content)
        if content_l <= 70:
            return 1
        else:
            sms_count = content_l // 70
            left_num = content_l % 70
            return sms_count if left_num == 0 else sms_count + 1

    @classmethod
    async def _notify_sms_by_candidate(
            cls, company_name: str, template: dict, candidate_info: dict, user_id: str,
            company_id: str,  short_url: str, task_id: str, action_code: str, activate_id: str,
            candidates_count: int, is_try: bool = False
    ):
        """
        逐个通知候选人
        """
        tem_content = template.get("text")
        content = tem_content.replace("#人才姓名#", candidate_info.get("name")).replace("#公司名称#", company_name).replace(
            "#招聘门户链接#", short_url
        )
        if is_try:
            await send_sms_by_action_code_for_free(
                action_code, company_id, candidate_info.get("mobile"), {"content": content},
                event_id=30110, biz_id=uuid2str(activate_id)
            )
        else:
            sms_count = cls._cal_sms_amount(content) * candidates_count
            message_body = [
                {
                    "emp_name": candidate_info.get("name"),
                    "mobile": candidate_info.get("mobile"),
                    "event_id": 30110,
                    "biz_id": uuid2str(activate_id),
                    "messagebody": {
                        "check_words": [
                            {"type": "company_name", "content": [company_name]},
                            {"type": "person_name", "content": [candidate_info.get("name")]},
                        ],
                        "content": content
                    }
                }
            ]
            # task_id 保证只扣一次费
            await svc.http_sms.send_sms_by_action_code(
                action_code, company_id, sms_count, message_body, task_id=task_id, user_id=user_id,
                module_code="CHR003-004", func_module="CHR003-004-001", biz_func="CHR003-004-001-001",
                func_page="sms_send_talent_activate"
            )
            await svc.activate_record.fill_sms_content(activate_id, content)

    @classmethod
    async def _notify_email_by_candidate(
            cls, company_id: str, user_id: str, send_email_id: str, email_info: dict,
            candidate_info: dict, company_name: str, active_record_id: str, short_url: str
    ):
        recipients = [{"address": candidate_info.get("email"), "name": candidate_info.get("name")}]
        email_title = email_info.get("email_title")
        email_content = email_info.get("email_content").replace("#人才姓名#", candidate_info.get("name")).replace(
            "#公司名称#", company_name).replace("#招聘门户链接#", short_url)

        await svc.http_email.send_mail_by_company_email(
            send_email_id, recipients, email_title, email_content, company_id, user_id,
            callback_data={"biz_type": NoticeCallBackType.talent_active, "biz_id": uuid2str(active_record_id)},
            files=email_info.get("attachments", [])
        )

    @classmethod
    async def active_notify_candidates(
            cls, company_id: str, user_id: str, task_id: str, candidate_id2activate_id: dict,
            validated_data: dict, is_try: bool = False
    ):
        """
        激活通知候选人
        @param company_id:
        @param user_id:
        @param task_id:
        @param candidate_id2activate_id:
        @param validated_data:
        @param is_try:
        @return:
        """
        sms_template_id = validated_data.get("sms_template_id")
        email_template_id = validated_data.get("email_template_id")
        send_email_id = validated_data.get("send_email_id")
        portal_page_id = validated_data.get("portal_page_id")
        page_position_id = validated_data.get("page_position_id")
        candidate_id2email_info = {
            uuid2str(item.get("candidate_id")): item for item in validated_data.get("candidates")
        }

        sms_template = await svc.http_sms.get_template_by_id(company_id, sms_template_id)
        candidate_ids = list(candidate_id2activate_id.keys())
        company, channel_id = await gather(
            svc.http_ucenter.get_company_for_id(company_id),
            svc.recruit_channel.find_channel_by_name(
                company_id, "人才激活"
            ),
        )
        share_id = company.get("share_id") if company else ""

        candidates, action_code = await gather(
            svc.candidate.get_candidates_by_ids(
                company_id, candidate_ids, ["id", "name", "mobile", "email"]
            ),
            svc.http_sms.get_company_sms_action_code(company_id)
        )

        short_url = ""
        company_name = company.get("shortname") or company.get("fullname")
        for candidate in candidates:
            if is_try:
                candidate.update(
                    {"mobile": validated_data.get("receiver_mobile"), "email": validated_data.get("receiver_email")}
                )
            activate_id = candidate_id2activate_id.get(candidate.get("id"))
            # 如果为空， 则不存在短链接
            if portal_page_id:
                short_url = await cls._get_activate_url(
                    share_id, channel_id, portal_page_id, page_position_id, activate_id
                )
            if sms_template_id:
                await cls._notify_sms_by_candidate(
                    company_name, sms_template, candidate, user_id, company_id,
                    short_url, task_id, action_code, activate_id, len(candidates), is_try
                )
            if email_template_id:
                email_info = candidate_id2email_info.get(candidate.get("id"))
                await cls._notify_email_by_candidate(
                    company_id, user_id, send_email_id, email_info,
                    candidate, company_name, activate_id, short_url
                )

    @classmethod
    async def _activate_validation(cls, company_id: str, validated_data: dict):

        sms_template_id = validated_data.get("sms_template_id")
        email_template_id = validated_data.get("email_template_id")
        send_email_id = validated_data.get("send_email_id")
        notify_way = validated_data.get("notify_way")
        if notify_way == ActivateNotifyWay.Sms and not sms_template_id:
            raise APIValidationError(101201, msg='短信模板ID缺失')
        if notify_way == ActivateNotifyWay.Email and not email_template_id:
            raise APIValidationError(101201, msg='邮件模板ID缺失')
        if notify_way == ActivateNotifyWay.Sms_Email and not all([sms_template_id, email_template_id]):
            raise APIValidationError(101201, msg='通知模板ID缺失')
        if notify_way != ActivateNotifyWay.Sms and not send_email_id:
            raise APIValidationError(101201, msg='邮件发送地址缺失')
        if sms_template_id:
            sms_template = await svc.http_sms.get_template_by_id(company_id, sms_template_id)
            if not sms_template or not sms_template.get("text"):
                raise APIValidationError(101201, msg="短信模板不存在")
        if email_template_id:
            email_template = await svc.email_template.get_template_by_id(company_id, email_template_id)
            if not email_template:
                raise APIValidationError(101201, msg="邮件模板不存在")

    @classmethod
    async def create_records(cls, company_id: str, user_id: str, validated_data: dict):
        """
        创建激活记录
        @param company_id:
        @param user_id:
        @param validated_data:
        @return:
        """
        candidate_ids = [
            uuid2str(candidate.get("candidate_id")) for candidate in validated_data.get("candidates", [])
        ]
        await cls._activate_validation(company_id, validated_data)

        task_id = gen_uuid()
        candidate_id2activate_id = await svc.activate_record.create_records(
            company_id, user_id, task_id, candidate_ids, validated_data
        )
        await svc.candidate_comment.batch_create_candidate_comment(
            company_id, candidate_ids, "发起了人才激活", user_id,
            user_type=ParticipantType.HR, need_name=True
        )
        await svc.http_candidate.update_latest_activate_dt(company_id, candidate_ids)
        # celery_app.send_task("apps.tasks.talent_activate.activate_notify_candidates", args=(
        #     company_id, user_id, task_id, candidate_id2activate_id, validated_data
        # ))
        await cls.active_notify_candidates(
            company_id, user_id, task_id, candidate_id2activate_id, validated_data
        )

    @classmethod
    async def _get_portal_info(cls, company_id: str, portal_ids: list):
        id2info = {}
        if portal_ids:
            pages = await svc.portal_page.get_pages_by_ids(
                company_id, portal_ids, ["id", "name"]
            )
            for page in pages:
                id2info[page.get("id")] = {
                    "portal_page_name": page.get("name")
                }

        return id2info

    @classmethod
    async def _get_email_template_info(cls, company_id: str, template_ids: list):
        id2info = {}
        if template_ids:
            templates = await svc.email_template.get_template_by_ids(
                company_id, template_ids, ["id", "name"]
            )
            for template in templates:
                id2info[template.get("id")] = {
                    "email_template_name": template.get("name")
                }

        return id2info

    @classmethod
    async def _get_portal_position_info(cls, company_id: str, portal_position_ids: list):
        id2info = {}
        if portal_position_ids:
            positions = await svc.portal_position.get_portal_positions_by_ids(
                company_id, portal_position_ids, ["id", "name"]
            )
            for position in positions:
                id2info[position.get("id")] = {
                    "portal_position_name": position.get("name")
                }

        return id2info

    @classmethod
    async def _get_add_by_info(cls, user_ids: list):
        id2info = {}
        if user_ids:
            users = await svc.http_ucenter.get_users(user_ids)
            for user in users:
                id2info[uuid2str(user["id"])] = {
                    "add_by_name": user.get("nickname")
                }

        return id2info

    @classmethod
    async def _filter_data(cls, company_id: str, data: dict, candidates: list):
        """
        填充返回数据
        @param company_id:
        @param data:
        @param candidates:
        @return:
        """
        candidate_id2info = {item.pop("id"): item for item in candidates}
        if data["objects"]:
            portal_page_ids = set()
            page_position_ids = set()
            add_by_ids = set()
            email_template_ids = set()
            for item in data["objects"]:
                if item.get("portal_page_id"):
                    portal_page_ids.add(item.get("portal_page_id"))
                if item.get("page_position_id"):
                    page_position_ids.add(item.get("page_position_id"))
                if item.get("add_by_id"):
                    add_by_ids.add(item.get("add_by_id"))
                if item.get("email_template_id"):
                    email_template_ids.add(item.get("email_template_id"))
            user_id2info = await cls._get_add_by_info(list(add_by_ids))
            portal_id2info = await cls._get_portal_info(company_id, list(portal_page_ids))
            portal_position_id2info = await cls._get_portal_position_info(
                company_id, list(page_position_ids)
            )
            email_template_id2info = await cls._get_email_template_info(company_id, list(email_template_ids))

            for item in data["objects"]:
                hide_data = False if item["portal_page_id"] else True
                item.update(
                    candidate_id2info.get(item["candidate_id"], {})
                )
                item.update(
                    user_id2info.get(item["add_by_id"], {})
                )
                item.update(
                    email_template_id2info.get(item["email_template_id"], {})
                )
                item.update(
                    portal_id2info.get(item["portal_page_id"], {})
                )
                item["sms_response"] = ujson.loads(item["sms_response"]) if item["sms_response"] else {}
                if not hide_data:
                    item.update(
                        portal_position_id2info.get(item["page_position_id"], {"portal_position_name": "全部"})
                    )
                else:
                    item.update(
                        {
                            "latest_read_dt": "",
                            "is_read": None,
                            "portal_position_name": "",
                            "activate_status": 0
                        }
                    )
        return data

    @classmethod
    async def record_list(cls, company_id: str, query_params: dict):
        """
        激活记录列表
        @param company_id:
        @param query_params:
        @return:
        """
        fields = [
            "id", "portal_page_id", "page_position_id", "activate_status", "add_by_id", "add_dt",
            "is_read", "latest_read_dt", "notify_way", "candidate_id", "candidate_record_id",
            "sms_content", "email_template_id", "sms_response"
        ]
        keyword = query_params.get("keyword")
        candidates = []
        if keyword:
            candidates = await svc.candidate.filter_talents(company_id, keyword)
            candidate_ids = [item.get("id") for item in candidates]
            query_params.update({"candidate_ids": candidate_ids})
            if not candidates:
                return {
                    "p": 1, "limit": 10, "offset": 1, "totalpage": 1, "total_count": 0, "objects": []
                }
        data = await svc.activate_record.record_list_with_page(company_id, query_params, fields)
        if not keyword:
            candidate_ids = [item.get("candidate_id") for item in data["objects"]]
            candidates = await svc.candidate.get_candidates_by_ids(
                company_id, list(set(candidate_ids)), ["id", "name", "mobile", "email"]
            )

        res = await cls._filter_data(company_id, data, candidates)

        return res

    @classmethod
    async def record_portal_list(cls, company_id):
        """
        获取企业激活记录中所有网页集合
        @param company_id:
        @return:
        """
        records = await svc.activate_record.record_list_without_page(
            company_id, ["portal_page_id"]
        )
        portal_ids = set()
        for record in records:
            portal_ids.add(record.get("portal_page_id"))
        res = []
        if portal_ids:
            res = await svc.portal_page.get_pages_by_ids(
                company_id, list(portal_ids), ["id", "name"]
            )
        return res

    @classmethod
    async def talent_activate_count(cls, company_id: str, candidate_id: str):
        """
        查询人才本月激活次数
        @param company_id:
        @param candidate_id:
        @return:
        """
        month_first_date = date(year=date.today().year, month=date.today().month, day=1)
        records = await svc.activate_record.candidate_activate_records(
            company_id, candidate_id, ["id"], {"start_dt": month_first_date}
        )

        return len(records)

    @classmethod
    async def activate_link_view(cls, company_id: str, record_id: str):
        """
        激活链接被访问后记录访问
        @param company_id:
        @param record_id:
        @return:
        """
        activate = await svc.activate_record.get_activate_record_by(
            company_id, record_id, ["candidate_id", "is_read"]
        )
        if activate:
            candidate_id = activate.get("candidate_id")
            is_read = activate.get("is_read")
            candidates = await svc.candidate.get_candidates_by_ids(
                company_id, [candidate_id], fields=["id", "talent_is_join"]
            )
            await svc.activate_record.update_view_status(company_id, record_id)
            if not is_read and candidates and candidates[0].get("talent_is_join"):
                await svc.candidate_comment.create_comment(
                    company_id, candidate_id, "人才查看了职位信息"
                )
            await svc.http_candidate.update_latest_follow_dt(
                company_id, [candidate_id]
            )

    @classmethod
    async def activate_try_count(cls, company_id: str, user_id: str, redis_key: str = ""):
        """
        人才激活试发次数
        @param company_id:
        @param user_id:
        @param redis_key:
        @return:
        """
        if not redis_key:
            redis_key = TALENT_ACTIVE_TRY_NOTICE[0].format(
                company_id=uuid2str(company_id), user_id=uuid2str(user_id),
                date_str=datetime.date.today().strftime("%Y%m%d")
            )
        redis_cli = await redis_db.default_redis
        try_count = await redis_cli.get(redis_key) or 0
        try_count = int(try_count)

        return try_count

    @classmethod
    async def activate_try(cls, company_id: str, user_id: str, validated_data: dict):
        """
        人才激活试发功能
        @param company_id:
        @param user_id:
        @param validated_data:
        @return:
        """
        candidate_ids = [uuid2str(candidate.get("candidate_id")) for candidate in validated_data.get("candidates")]
        await cls._activate_validation(company_id, validated_data)
        candidate_id2activate_id = {candidate_ids[0]: uuid2str(gen_uuid())}

        redis_key = TALENT_ACTIVE_TRY_NOTICE[0].format(
            company_id=uuid2str(company_id), user_id=uuid2str(user_id), date_str=datetime.date.today().strftime("%Y%m%d")
        )
        try_count = await cls.activate_try_count(company_id, user_id, redis_key)
        if try_count >= 3:
            raise APIValidationError(201201, msg='今日激活试发次数已用完')
        # 激活试发
        await cls.active_notify_candidates(
            company_id, user_id, uuid2str(gen_uuid()), candidate_id2activate_id, validated_data, True
        )
        # celery_app.send_task("apps.tasks.talent_activate.activate_notify_candidates", args=(
        #     company_id, user_id, uuid2str(gen_uuid()), candidate_id2activate_id, validated_data, True
        # ))
        # 保存试发次数
        redis_cli = await redis_db.default_redis
        await redis_cli.setex(redis_key, TALENT_ACTIVE_TRY_NOTICE[1], try_count+1)
