from sanic_wtf import SanicForm
from wtforms import StringField, FieldList, Field, IntegerField
from wtforms.validators import DataRequired, Length, Optional, UUID

from business import biz
from business.b_wework import WeWorkBusiness
from constants.redis_keys import PORTALS_WEWORK_ADD_CANDIDATE
from drivers.redis import redis_db
from error_code import Code as ErrorCode
from kits.exception import APIValidationError
from utils.api_auth import EmployeeBaseView
from utils.redis_util import LockTimeoutError, RedisLock
from utils.sa_db import Paginator
from utils.strutils import uuid2str


class EmpReferralRecordView(EmployeeBaseView):
    """
    推荐候选人简历(员工内推)
    """
    class PostForm(SanicForm):
        candidate_name = StringField(validators=[DataRequired(), Length(max=20)], label='求职者姓名')
        position_record_id = StringField(validators=[DataRequired(), UUID()], label='内推职位ID')
        mobile = StringField(validators=[DataRequired(), Length(max=11)], label='求职者手机')
        referee_id = StringField(validators=[Optional(), UUID()], default=None, label="推荐人ID")
        resume_key = StringField(validators=[DataRequired()], label="候选人简历")
        attachments = FieldList(Field(), label="候选人附件")
        reason = StringField(validators=[DataRequired(), Length(max=500)], label="推荐理由")
        portal_id = StringField(validators=[DataRequired(), UUID()], label="招聘门户id")

    async def post(self, request):
        """
        推荐候选人简历(员工内推)
        """
        form = self.PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        company_id = uuid2str(request.ctx.user.company_id)
        emp_id = uuid2str(request.ctx.user.emp_id)

        attachments = [{
            'file_list': form.attachments.data,
            'field_key': 'other_attachments'
        }]

        openid = request.ctx.user.openid
        unionid = request.ctx.user.unionid

        await biz.portal_delivery.create_referral_record(
            company_id=company_id, user_id=emp_id, form_data=form.data, attachments=attachments,
            open_id=openid, union_id=unionid
        )
        return self.data({"msg": "提交成功"})


class WeWorkReferralView(EmployeeBaseView):
    """
    企业微信侧边栏推荐简历
    """
    class PostForm(SanicForm):
        resume_key = StringField(validators=[DataRequired(), UUID()], label="简历文件key")
        candidate_name = StringField(validators=[DataRequired(), Length(max=20)], label="求职者姓名")
        mobile = StringField(validators=[DataRequired(), Length(max=11)], label="求职者手机号")
        position_record_id = StringField(validators=[DataRequired(), UUID()], label="内推职位id")
        reason = StringField(validators=[DataRequired(), Length(max=500)], label="推荐理由")
        attachments = FieldList(Field(), label="求职者附件")
        external_id = StringField(validators=[DataRequired(), Length(max=50)], label="外部联系人id")
        portal_id = StringField(validators=[Optional(), UUID()], default=None, label="招聘门户id")

    async def post(self, request):
        """
        企业微信内推简历
        """
        form = self.PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        company_id = uuid2str(request.ctx.user.company_id)
        emp_id = uuid2str(request.ctx.user.emp_id)
        attachments = [{
            "file_list": form.attachments.data,
            "field_key": "other_attachments"
        }]
        openid = request.ctx.user.openid
        unionid = request.ctx.user.unionid

        await biz.portal_delivery.we_work_referral_record(
            company_id=company_id, user_id=emp_id, form_data=form.data,
            attachments=attachments, open_id=openid, union_id=unionid,
        )
        return self.data({"msg": "提交成功"})


class EmpWeWorkCandidateCreateView(EmployeeBaseView):
    """
    企业微信侧边栏 招聘门户添加候选人(员工鉴权HR身份操作)
    """
    class PostForm(SanicForm):
        resume_key = StringField(validators=[DataRequired(), UUID()], label="简历文件key")
        candidate_name = StringField(validators=[DataRequired(), Length(max=20)], label="求职者姓名")
        mobile = StringField(validators=[DataRequired(), Length(max=11)], label="求职者手机号")
        job_position_id = StringField(validators=[DataRequired(), UUID()], label="招聘职位id")
        status = IntegerField(validators=[DataRequired()], label="候选人状态")
        recruit_channel_id = StringField(validators=[Optional(), UUID()],  default=None, label="招聘渠道")
        attachments = FieldList(Field(), label="求职者附件")
        external_id = StringField(validators=[DataRequired(), Length(max=50)], label="外部联系人id")

    async def post(self, request):
        """
        HR招聘门户添加候选人
        """
        form = self.PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        company_id = uuid2str(request.ctx.user.company_id)
        user_id = await self.get_hr_id(request)
        if not user_id:
            raise APIValidationError(ErrorCode.FORBIDDEN)

        key = PORTALS_WEWORK_ADD_CANDIDATE[0].format(
            company_id=uuid2str(company_id),
            user_id=uuid2str(user_id),
            name=form.candidate_name.data,
            mobile=form.mobile.data
        )
        try:
            async with RedisLock(
                    await redis_db.default_redis,
                    key=key,
                    timeout=PORTALS_WEWORK_ADD_CANDIDATE[1],
                    wait_timeout=0,
            ):
                attachments = [{
                    "file_list": form.attachments.data,
                    "field_key": "other_attachments"
                }]

                res = await biz.portal_delivery.we_work_add_candidate_by_hr(
                    company_id=company_id, user_id=user_id, form_data=form.data,
                    attachments=attachments
                )
                return self.data(res)
        except LockTimeoutError:
            raise APIValidationError(ErrorCode.candidate_resubmit)


class EmpWeWork2HAOHRExternalContactQrCodeView(EmployeeBaseView):
    """
    获取外部联系人二维码
    """
    async def get(self, request):
        """
        推荐候选人简历(内推)
        """
        company_id = uuid2str(request.ctx.user.company_id)
        emp_id = uuid2str(request.ctx.user.emp_id)
        app_id = await WeWorkBusiness.get_company_app_id(company_id)

        qr_code = await biz.portal_wework.get_external_contact_qr_code(app_id, company_id, emp_id)
        return self.data({"qr_code": qr_code})


class ReferralListPostForm(SanicForm):
    dep_ids = FieldList(StringField(validators=[Optional(), UUID()]), label='用人部门')
    keyword = StringField(label="候选人姓名/手机")
    start_dt = StringField(label="内推时间(开始)")
    end_dt = StringField(label="内推时间(结束)")
    position_ids = FieldList(StringField(validators=[Optional(), UUID()]), label="招聘职位id")
    status = FieldList(IntegerField(), label="候选人状态")
    portal_ids = FieldList(
        StringField(validators=[Optional(), UUID()], label="招聘门户id")
    )
    is_has_bonus = StringField(default=None, label="是否有内推奖励")


class EmpReferralRecordListView(EmployeeBaseView):
    """
    协作者平台内推记录
    """

    async def post(self, request):
        """
        获取招聘内推记录列表
        """
        form = ReferralListPostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        company_id = uuid2str(request.ctx.user.company_id)
        emp_id = uuid2str(request.ctx.user.emp_id)
        page, limit = Paginator.get_p_limit(request)
        res = await biz.portal_delivery.get_emp_referral_records_with_page(
            company_id, emp_id, form.data, page, limit,
        )
        return self.data(res)


class EmpReferralRecordExportView(EmployeeBaseView):
    """
    内推记录导出
    """

    async def post(self, request):
        form = ReferralListPostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        company_id = uuid2str(request.ctx.user.company_id)
        emp_id = uuid2str(request.ctx.user.emp_id)
        url = await biz.portal_delivery.export_referral_record_for_emp(
            company_id, form_data=form.data, emp_id=emp_id
        )
        return self.data({"url": url})


class EmpMyReferralRecordView(EmployeeBaseView):
    """
    员工端我的内推记录
    """

    async def get(self, request):
        """
        查询小程序我的内推记录
        """
        company_id = uuid2str(request.ctx.user.company_id)
        emp_id = uuid2str(request.ctx.user.emp_id)
        page, limit = Paginator.get_p_limit(request)
        res = await biz.portal_delivery.get_my_referral_records_with_page(
            company_id=company_id, referee_id=emp_id, page=page, limit=limit
        )
        return self.data(res)


class EmpMyReferralStatView(EmployeeBaseView):
    """
    员工端我的内推统计
    """

    async def get(self, request):
        company_id = uuid2str(request.ctx.user.company_id)
        emp_id = uuid2str(request.ctx.user.emp_id)

        res = await biz.portal_delivery.get_delivery_record_stat_emp(
            company_id, emp_id=emp_id
        )
        return self.data(res)

