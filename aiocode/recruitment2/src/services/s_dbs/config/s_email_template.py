import datetime

import sqlalchemy as sa
from sqlalchemy import and_

from constants import EmailTemplateUsage
from drivers.mysql import db
from kits.exception import APIValidationError
from models.m_config import tb_email_template, tb_email_template_attach
from services.s_https.s_ucenter import get_company_for_id
from utils.sa_db import db_executor, Paginator
from utils.strutils import uuid2str

DEFAULT_TEMPLATES = {
    'offer': {
        'name': '默认模板',
        "title": u"{}录用通知书",
        "content": '''
            <h2 style="text-align: center;font-size: 24px;font-weight: bold;">录用通知书</h2><p><br/></p>
            <p>尊敬的<span class="atwho-inserted" data-atwho-at-query="#">#候选人姓名#</span>&nbsp;</p><p><br></p>
            <p style="text-indent: 2em;">感谢您对公司的认可，非常荣幸地通知您，您已被我司正式录用，欢迎您加入<span class="atwho-inserted" data-atwho-at-query="#">#公司名称#</span>！&nbsp;</p>
            <p style="text-indent: 2em;">您所入职的部门：<span class="atwho-inserted" data-atwho-at-query="#">#入职部门#</span>&nbsp;</p>
            <p style="text-indent: 2em;">您所入职的岗位：<span class="atwho-inserted" data-atwho-at-query="#">#入职岗位#</span>&nbsp;</p>
            <p><br></p>
            <p style="text-indent: 2em;">入职所需的材料和证件</p><p style="text-indent: 2em;">1. 原单位离职证明（加盖原单位公章）1份</p><p style="text-indent: 2em;">2. 身份证原件</p>
            <p style="text-indent: 2em;">3. 学位证、毕业证原件</p><p style="text-indent: 2em;">4. 相关资格证书原件</p><p style="text-indent: 2em;">5. 入职体检证明</p><p style="text-indent: 2em;"><br></p>
            <p style="text-indent: 2em;">请您于<span class="atwho-inserted" data-atwho-at-query="#">#预计入职时间#</span>&nbsp;带以上材料，进行报到</p><p style="text-indent: 2em;"><br></p>
            <p style="text-indent: 2em;">联系人：<span class="atwho-inserted" data-atwho-at-query="#">#联系人姓名#</span>&nbsp;</p><p style="text-indent: 2em;">联系电话：<span class="atwho-inserted" data-atwho-at-query="#">#联系人电话#</span>&nbsp;</p>
            <p style="text-indent: 2em;">联系人邮箱：<span class="atwho-inserted" data-atwho-at-query="#">#联系人邮箱#</span>&nbsp;</p><p style="text-indent: 2em;"><br></p>
            <p style="text-indent: 2em;">再次欢迎您加入<span class="atwho-inserted" data-atwho-at-query="#">#公司名称#</span>&nbsp;！</p>
            <p><br></p>
        '''.strip()
    },
    'interview_notify': {
        'name': '默认模板',
        "title": u"{}面试通知",
        "content": '''
            <h2 style="text-align: center;font-size: 24px;font-weight: bold;">面试通知</h2><p><br/></p>
            <p>尊敬的<span class="atwho-inserted" data-atwho-at-query="#" id="dm_interview_candidate_name">#候选人姓名#</span>&nbsp;</p>
            <p></p>
            <p style="text-indent: 2em;">您好，感谢您对<span class="atwho-inserted" data-atwho-at-query="#">#公司名称#</span>&nbsp;的信任和支持，您提供的应聘资料符合我司的面试要求，特邀您前来参与面试。为能顺利帮您安排面试，请详细了解以下信息：</p><br>
            <p><strong>应聘职位：</strong><span class="atwho-inserted" data-atwho-at-query="#" id="dm_interview_jobposition_name">#应聘职位#</span>&nbsp;</p><p><strong>面试时间：</strong><span class="atwho-inserted" data-atwho-at-query="#">#面试时间#</span>&nbsp;</p>
            <p><strong>面试地址：</strong><span class="atwho-inserted" data-atwho-at-query="#">#面试地址#</span>&nbsp;</p><br>
            <p style="text-indent: 2em;">请您安排时间准时到达面试地点，如有疑问请与<span class="atwho-inserted" data-atwho-at-query="#">#联系人#</span>&nbsp;（<span class="atwho-inserted" data-atwho-at-query="#">#联系电话#</span>&nbsp;）联系。祝您面试成功！</p><p><br>
        '''.strip()
    },
    'mobile_interview_notify': {
        'name': '电话面试模板',
        'title': '{}面试通知',
        'content': '''
             <h2 style="text-align: center;font-size: 24px;font-weight: bold;">面试通知</h2><p><br/></p>
             <p>尊敬的<span class="atwho-inserted" data-atwho-at-query="#" id="dm_interview_candidate_name">#候选人姓名#</span>&nbsp; </p> 
             <p></p> 
             <p style="text-indent: 2em;">您好，感谢您对<span class="atwho-inserted" data-atwho-at-query="#">#公司名称#</span>&nbsp;的信任和支持，您提供的应聘资料符合我司的面试要求，特邀您进行远程电话面试，请了解以下信息：</p> 
             <br /> 
             <p><strong>应聘职位：</strong><span class="atwho-inserted" data-atwho-at-query="#" id="dm_interview_jobposition_name">#应聘职位#</span>&nbsp;</p> 
             <p><strong>面试时间：</strong><span class="atwho-inserted" data-atwho-at-query="#">#面试时间#</span>&nbsp;</p>
             <br /> 
             <p style="text-indent: 2em;">请您做好准备，按时参加。如有疑问请与<span class="atwho-inserted" data-atwho-at-query="#">#联系人#</span>&nbsp;（<span class="atwho-inserted" data-atwho-at-query="#">#联系电话#</span>&nbsp;）联系。祝您面试成功！</p> 
             <p><br /></p>
         '''.strip()
    },
    'video_interview_notify': {
        'name': '视频面试模板',
        'title': '{}面试通知',
        'content': '''
            <h2 style="text-align: center;font-size: 24px;font-weight: bold;">面试通知</h2><p><br/></p>
            <p>尊敬的<span class="atwho-inserted" data-atwho-at-query="#" id="dm_interview_candidate_name">#候选人姓名#</span>&nbsp; </p> 
            <p></p> 
            <p style="text-indent: 2em;">您好，感谢您对<span class="atwho-inserted" data-atwho-at-query="#">#公司名称#</span>&nbsp;的信任和支持，您提供的应聘资料符合我司的面试要求。疫情期间，我们尽量采用无接触远程面试的方式，现特邀您进行视频面试，请了解以下信息：</p> 
            <br /> 
            <p><strong>应聘职位：</strong><span class="atwho-inserted" data-atwho-at-query="#" id="dm_interview_jobposition_name">#应聘职位#</span>&nbsp;</p> 
            <p><strong>面试时间：</strong><span class="atwho-inserted" data-atwho-at-query="#">#面试时间#</span>&nbsp;</p>
            <br /> 
            <p style="text-indent: 2em;">请您做好准备，按时参加。如有疑问请与<span class="atwho-inserted" data-atwho-at-query="#">#联系人#</span>&nbsp;（<span class="atwho-inserted" data-atwho-at-query="#">#联系电话#</span>&nbsp;）联系。祝您面试成功！</p> 
            <p><br /></p>
        '''.strip()
    },
    "eliminate_notify": {
        "name": "默认模板",
        "title": u"{}应聘结果通知",
        "content": '''
            <h2 style="text-align: center;font-size: 24px;font-weight: bold;">应聘结果通知</h2><p><br/></p>
            <p>尊敬的<span class="atwho-inserted" data-atwho-at-query="#" id="dm_interview_candidate_name">#候选人姓名#</span>&nbsp;</p>
            <p></p>
            <p style="text-indent: 2em;">非常感谢您应聘<span class="atwho-inserted" data-atwho-at-query="#">#公司名称#</span>的<span class="atwho-inserted" data-atwho-at-query="#" id="dm_interview_jobposition_name">#应聘职位#</span>&nbsp;，让我们了解到您的背景与能力，但经评估后非常抱歉地告知您，您暂不符合岗位条件，未能被成功录用，希望您能获得更好的工作机会，期盼有机会再与您合作。</p>
            <br>
        '''.strip()
    },

    "talent_activate": {
        "name": "人才激活",
        "title": "{}邀请您查看新的工作机会",
        "content": '''
            <h2 style="text-align: center;">期待您的加入</h2><p>
            <br></p><p>亲爱的<span class="atwho-inserted" data-atwho-at-query="#" id="dm_interview_candidate_name">#人才姓名#</span>&nbsp; </p><p>今年<span class="atwho-inserted" data-atwho-at-query="#">#公司名称#</span>&nbsp;将深耕行业，加大人才投入，打造一批最懂行业的作战团队，提供全套行业解决方案，助力产业发展。</p><p>我们将加强平台的健康运作，加强业务协同，提升运营效率。</p><p>我们希望____不止是<span>____</span><span>，而是拥有无限可能的</span><span>____</span><span>。</span></p><p>我们希望用____的方式服务社会，在____中探索更多价值。</p><p>如果你对____仍保存一份热爱，那就让<span class="atwho-inserted" data-atwho-at-query="#">#公司名称#</span>&nbsp;成为你实现梦想的平台，欢迎你与我们一起开创<span>____</span><span>的未来。</span></p><p>
            <br></p><p style="text-align: center;"><b>加入我们</b>：<span class="atwho-inserted" data-atwho-at-query="#">#招聘门户链接#</span>&nbsp;</p>
        '''.strip()
    },

    "wishes_talent_activate": {
        "name": "祝福",
        "title": "收到来自{}的祝福",
        "content": '''
            <p>亲爱的<span class="atwho-inserted" data-atwho-at-query="#">#人才姓名#</span>&nbsp;</p><p>勤奋，让成功充满机遇；</p><p>自信，让人生充满激情；</p><p>爱人，让生命愈加完整；</p><p>朋友，让生活变得丰富。</p><p>珍惜美好的爱人，珍惜真诚的朋友。</p><p><span class="atwho-inserted" data-atwho-at-query="#">#公司名称#</span>&nbsp;&nbsp;祝您：幸福一生~</p>
        '''.strip()
    }
}


class EmailTemplateService(object):

    @staticmethod
    def get_template_by_usage(usage):
        for key, value in EmailTemplateUsage.values_.items():
            if value == usage:
                return DEFAULT_TEMPLATES[key]
        return {}

    @classmethod
    async def create_email_template(cls, company_id: str, user_id: str, validated_data: dict):
        """
        创建邮件模板
        @param company_id:
        @param user_id:
        @param validated_data:
        @return:
        """
        company = await get_company_for_id(uuid2str(company_id))
        template = cls.get_template_by_usage(validated_data.get("usage"))
        if not template:
            raise APIValidationError(101201, msg='默认模板不存在')

        validated_data.update(
            {
                "company_id": uuid2str(company_id),
                "update_by_id": uuid2str(user_id),
                "add_by_id": uuid2str(user_id),
                "email_title": template["title"].format(company.get("fullname")),
                "email_content": template["content"]
            }
        )
        engine = await db.default_db
        id_ = await db_executor.single_create(engine, tb_email_template, validated_data)

        return id_

    @classmethod
    async def create_default_templates(cls, company_id: str, user_id: str, usage: int):
        """
        创建默认的邮件模板
        @param company_id:
        @param user_id:
        @param usage:
        @return:
        """
        company = await get_company_for_id(uuid2str(company_id))
        usage2default_templates = {
            EmailTemplateUsage.offer: [DEFAULT_TEMPLATES["offer"]],
            EmailTemplateUsage.interview_notify: [
                DEFAULT_TEMPLATES["interview_notify"],
                DEFAULT_TEMPLATES["mobile_interview_notify"],
                DEFAULT_TEMPLATES["video_interview_notify"]
            ],
            EmailTemplateUsage.eliminate_notify: [DEFAULT_TEMPLATES["eliminate_notify"]],
            EmailTemplateUsage.talent_activate: [
                DEFAULT_TEMPLATES["talent_activate"], DEFAULT_TEMPLATES["wishes_talent_activate"]
            ]
        }
        templates = []
        default_templates = usage2default_templates.get(usage) or []
        for template in default_templates:
            templates.append(
                {
                    "company_id": uuid2str(company_id),
                    "add_by_id": uuid2str(user_id),
                    "name": template['name'],
                    "email_title": template['title'].format(company.get("fullname")),
                    "email_content": template['content'],
                    "is_default": True,
                    "usage": usage

                }
            )
        engine = await db.default_db
        await db_executor.batch_create(engine, tb_email_template, templates)

        return

    @classmethod
    async def get_email_templates(cls, company_id: str, usage: int, params: dict):
        """
        获取邮件模板
        @param company_id:
        @param usage:
        @param params:
        @return:
        """
        fields = [column.key for column in tb_email_template.columns]
        stmt = sa.select(
            [tb_email_template.c.get(field).label(field) for field in fields]
        ).where(
            and_(
                tb_email_template.c.company_id == uuid2str(company_id),
                tb_email_template.c.usage == usage,
                tb_email_template.c.is_deleted == 0
            )
        ).order_by(
            tb_email_template.c.add_dt
        )

        engine = await db.default_db
        data = await db_executor.fetch_all_data(engine, stmt)
        return [dict(item) for item in data]

    @classmethod
    async def update_email_template(cls, company_id: str, user_id: str, validated_data: dict):
        """
        更新邮件模板
        @param company_id:
        @param user_id:
        @param validated_data:
        @return:
        """
        where_stmt = and_(
            tb_email_template.c.id == uuid2str(validated_data.get("id")),
            tb_email_template.c.company_id == uuid2str(company_id)
        )
        data = {
            "name": validated_data.get("name"),
            "email_title": validated_data.get("email_title"),
            "email_content": validated_data.get("email_content"),
            "update_by_id": uuid2str(user_id),
        }
        engine = await db.default_db
        await db_executor.update_data(engine, tb_email_template, data, where_stmt)

    @classmethod
    async def delete_email_template(cls, company_id: str, user_id: str, id_: str):
        """
        删除邮件模板
        @param company_id:
        @param user_id:
        @param id_:
        @return:
        """
        engine = await db.default_db
        await db_executor.update_data(
            engine, tb_email_template, {"is_deleted": True, "update_by_id": uuid2str(user_id)},
            and_(
                tb_email_template.c.id == uuid2str(id_),
                tb_email_template.c.company_id == uuid2str(company_id)
            )
        )
        await db_executor.update_data(
            engine, tb_email_template_attach, {"is_deleted": True},
            tb_email_template_attach.c.email_template_id == uuid2str(id_)
        )

    @classmethod
    async def get_template_attachments(cls, template_ids: list):
        """
        获取模板附件
        @param template_ids:
        @return:
        """
        fields = [column.key for column in tb_email_template_attach.columns]

        stmt = sa.select(
            [tb_email_template_attach.c.get(field).label(field) for field in fields]
        ).where(
            and_(
                tb_email_template_attach.c.email_template_id.in_(template_ids),
                tb_email_template_attach.c.is_deleted == 0
            )
        )

        engine = await db.default_db
        data = await db_executor.fetch_all_data(engine, stmt)
        return [dict(item) for item in data]

    @classmethod
    async def create_template_attachments(cls, template_id: str, attachments: list):
        """
        设置模板附件
        @param template_id:
        @param attachments:
        @return:
        """
        engine = await db.default_db
        await db_executor.update_data(
            engine, tb_email_template_attach, {"is_deleted": True},
            tb_email_template_attach.c.email_template_id == uuid2str(template_id)
        )
        data = []
        for att in attachments:
            data.append(
                {
                    "email_template_id": uuid2str(template_id),
                    "file_name": att.get("file_name"),
                    "file_size": att.get("file_size"),
                    "file_type": att.get("file_type"),
                    "file_key": att.get("file_key"),
                    "add_dt": datetime.datetime.now()
                }
            )
        await db_executor.batch_create(engine, tb_email_template_attach, data)

    @classmethod
    async def get_template_by_id(cls, company_id: str, template_id: str, fields: list = None):
        """
        根据模板id查询模板
        @param company_id:
        @param template_id:
        @param fields:
        @return:
        """
        engine = await db.default_db
        fields = fields or ["email_title", "email_content"]
        stmt = sa.select(
            [tb_email_template.c.get(field).label(field) for field in fields]
        ).where(
            and_(
                tb_email_template.c.id == uuid2str(template_id),
                tb_email_template.c.company_id == uuid2str(company_id)
            )
        )
        data = await db_executor.fetch_one_data(engine, stmt)

        return data

    @classmethod
    async def get_template_by_ids(cls, company_id: str, template_ids: list, fields: list = None):
        """
        根据模板id查询模板
        @param company_id:
        @param template_ids:
        @param fields:
        @return:
        """
        template_ids = [uuid2str(id_) for id_ in template_ids]
        engine = await db.default_db
        fields = fields or ["name", "email_title", "email_content"]
        stmt = sa.select(
            [tb_email_template.c.get(field).label(field) for field in fields]
        ).where(
            and_(
                tb_email_template.c.id.in_(template_ids),
                tb_email_template.c.company_id == uuid2str(company_id)
            )
        )
        data = await db_executor.fetch_all_data(engine, stmt)

        return [dict(item) for item in data]
