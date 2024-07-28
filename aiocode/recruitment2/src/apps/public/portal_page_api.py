from sanic_wtf import SanicForm
from wtforms import StringField, IntegerField, FormField, FieldList, Field
from wtforms.validators import DataRequired, Length, UUID, Optional

from business import biz
from constants import CandidateRecordSource
from services.s_https.s_ucenter import get_company_for_share_id
from utils.api_auth import WeChatBaseView
from utils.api_auth import BaseView
from utils.strutils import uuid2str


class CandidateDeliveryForm(SanicForm):
    candidate_name = StringField(validators=[DataRequired(), Length(max=20)], label="候选人姓名")
    mobile = StringField(validators=[DataRequired(), Length(max=11)], label="候选人手机号")
    personal_evaluation = StringField(validators=[Optional(), Length(max=1000)], label="自我评价")


class CandidatePortalPageView(WeChatBaseView):
    """
    候选人投递招聘网页
    """
    class PostForm(SanicForm):
        position_record_id = StringField(validators=[DataRequired()], label='内推职位ID')
        share_id = StringField(validators=[DataRequired()], label="企业shareID")
        form_data = FormField(CandidateDeliveryForm, label="表单信息")
        attachment = FieldList(Field(), label="附件信息")
        referee_id = StringField(validators=[Optional()], default=None, label="推荐人id")
        recruitment_channel_id = StringField(validators=[Optional()], default=None, label="招聘渠道")
        activate_id = StringField(validators=[Optional()], default=None, label="激活记录ID")

    async def post(self, request):
        """
        求职者主动投递招聘网页
        """
        form = self.PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        company = await get_company_for_share_id(form.share_id.data)
        candidate_attachments = []
        resume_key = None
        for item in form.attachment.data:
            if item.get("field_key") == "candidate_resume":
                resume_key = item.get("file_list")[0].get("key")
                continue
            candidate_attachments.append(item)
        candidate_data = request.json.get("form_data", {})
        openid = request.ctx.user.openid
        unionid = request.ctx.user.unionid

        res = await biz.portal_delivery.candidate_delivery_record(
            company_id=uuid2str(company.get("id")),
            form_data=candidate_data,
            recruitment_channel_id=form.recruitment_channel_id.data,
            position_record_id=form.position_record_id.data,
            resume_key=resume_key,
            attachments=candidate_attachments,
            referee_id=form.referee_id.data,
            open_id=openid, union_id=unionid,
            source=CandidateRecordSource.WX_RECRUITMENT,
            activate_id=form.activate_id.data
        )

        return self.data(res)


class PortalPositionQrCodeView(BaseView):
    """
    获取内推职位的小程序码
    """
    async def get(self, request):
        share_id = uuid2str(request.args.get("share_id"))
        employee_id = uuid2str(request.args.get("employee_id"))
        position_id = uuid2str(request.args.get("portal_position_id"))
        channel_id = uuid2str(request.args.get("channel_id"))

        # 兼容历史，只有职位id情况
        company_id = None
        if share_id:
            company = await get_company_for_share_id(share_id)
            if not company:
                return self.error("企业不存在")
            company_id = company.id
        if not position_id:
            return self.error("参数缺失")

        company_info = {"share_id": share_id, "company_id": company_id}
        res = await biz.portal_page.get_portal_position_qrcode_url(
            employee_id, position_id, company_info, channel_id
        )
        return self.data(res)


class ReferralEmployeeDetailView(BaseView):
    """
    @desc 获取内推人信息
    """
    async def get(self, request):
        share_id = request.args.get("share_id")
        company = await get_company_for_share_id(share_id)
        if not company:
            return self.data({})

        employee_id = request.args.get("employee_id")
        res = await biz.portal_page.get_referral_employee_info(
            company.id, employee_id, emp_site=False
        )
        return self.data(res)


class RecruitmentPageDetailView(BaseView):
    """
    @desc 获取招聘门户详细信息
    """
    class GetForm(SanicForm):
        recruitment_page_id = StringField(validators=[DataRequired()], label='招聘门户ID')
        share_id = StringField(validators=[Optional()], label="企业shareID")
        path = StringField(validators=[DataRequired()], label="小程序码path")

    async def get(self, request):
        callback = request.args.get('callback', 'callback')
        form = self.GetForm(data=request.args)
        if not form.validate():
            return self.error_js(form.errors, callback=callback)

        recruitment_page_id = uuid2str(form.recruitment_page_id.data[0])
        res = await biz.portal_page.portal_company_intro_by_id(recruitment_page_id)

        path = form.path.data[0]
        width = 280
        key = biz.config_common.make_key("%s/%s" % (path, width))
        qr_code = await biz.config_common.get_share_mini_qrcode(key, path, width=width)

        res['qrcode'] = qr_code

        return self.js(res, callback=callback)


class PortalPositionFilterView(BaseView):
    """
    H5 根据招聘网页获取 城市/招聘职位 筛选组件
    """
    class GetForm(SanicForm):
        # share_id = StringField(Optional(), validators=[UUID()])
        page_id = StringField(validators=[Optional(), UUID()], label="招聘网页id")

    async def get(self, request):
        form = self.GetForm(formdata=request.args)
        if not form.validate():
            return self.error(form.errors)

        page_id = uuid2str(request.args.get("page_id"))
        share_id = request.args.get("share_id")
        company_id = None
        # 兼容历史分享链接无share_id情况
        if share_id:
            company = await get_company_for_share_id(share_id)
            if not company:
                return self.data({})
            company_id = uuid2str(company.get("id"))

        res = await biz.portal_page.get_position_type_and_city(
            company_id=company_id, page_id=page_id
        )
        return self.data(res)
