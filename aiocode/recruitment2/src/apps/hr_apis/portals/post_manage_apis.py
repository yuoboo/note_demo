"""
招聘门户投递管理
"""
from datetime import datetime
from celery_worker import celery_app

from sanic_wtf import SanicForm
from wtforms import StringField, FieldList, IntegerField
from wtforms.validators import UUID, Optional, DataRequired, Length

from business.commons.b_task_center import TaskCenterBusiness
from constants import ParticipantType, TaskType
from kits.exception import APIValidationError
from utils.api_auth import HRBaseView
from business import biz
from utils.sa_db import Paginator
from utils.strutils import uuid2str


class PostForm(SanicForm):
    keyword = StringField(label="求职者姓名/手机号模糊搜索")
    dep_ids = FieldList(StringField(validators=[Optional(), UUID()]), label="用户部门")
    start_dt = StringField(label="内推时间范围(开始)")
    end_dt = StringField(label="内推时间范围(结束)")
    referee = StringField(label='内推人姓名/手机号')
    position_ids = FieldList(StringField(validators=[Optional(), UUID()]), label='招聘职位id')
    status = FieldList(IntegerField(), label='候选人状态')
    is_payed = StringField(default=None, label="内推奖金是否发放")
    portal_ids = FieldList(
        StringField(validators=[Optional(), UUID()], label="招聘门户id")
    )
    is_has_bonus = StringField(default=None, label="是否有内推奖励")


class ReferralRecordListView(HRBaseView):
    """
    投递记录列表
    """

    async def post(self, request):
        form = PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)
        company_id = uuid2str(request.ctx.company_id)
        user_id = uuid2str(request.ctx.user_id)
        page, limit = Paginator.get_p_limit(request)
        res = await biz.portal_delivery.get_referral_records(
            company_id, user_id, form.data, page, limit
        )
        return self.data(res)


class PortalRecordStatisticsView(HRBaseView):
    """
    投递记录统计
    """
    async def get(self, request):
        company_id = uuid2str(request.ctx.company_id)

        res = await biz.portal_delivery.get_delivery_record_stat(company_id)
        return self.data(res)


class PortalRecordPromotionStatView(HRBaseView):
    """
    推广效果统计
    """
    async def get(self, request):
        company_id = uuid2str(request.ctx.company_id)
        res = await biz.portal_delivery.get_delivery_record_stat_info(company_id)
        return self.data(res)


class ReferralRecordExportView(HRBaseView):
    """
    内推记录导出
    """
    async def post(self, request):
        form = PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        company_id = uuid2str(request.ctx.company_id)
        user_id = uuid2str(request.ctx.user_id)

        tc_data = await TaskCenterBusiness.add(
            company_id, user_id, TaskType.export,
            "投递记录",
            datetime.strftime(datetime.now(), "%Y年%m月%d日"))

        celery_app.send_task("apps.tasks.portals.portals_export_task_center", args=(
            company_id, user_id, tc_data.task_type, tc_data.task_id, form.data))
        return self.data("SUCCESS")

        # company_id = uuid2str(request.ctx.company_id)
        # url = await biz.portal_delivery.export_referral_record(company_id, form.data)
        # return self.data({
        #     "url": url
        # })


class ReferralRecordSetPayView(HRBaseView):
    """
    设置是否发放内推奖金
    """
    permissions = {
        "post": "recruitment:referral_management"
    }

    class PostForm(SanicForm):
        referral_record_ids = FieldList(
            StringField(validators=[DataRequired(), UUID()]), min_entries=1, label="内推记录ids"
        )
        is_payed = StringField(default=None, label="是否发放奖金")

    async def post(self, request):
        form = self.PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        company_id = uuid2str(request.ctx.company_id)
        user_id = uuid2str(request.ctx.user_id)
        is_payed = form.is_payed.data
        if is_payed is None:
            raise APIValidationError(msg="is_payed 字段缺失")

        await biz.portal_delivery.set_referral_record_payed(
            company_id, user_id, record_ids=form.referral_record_ids.data, is_payed=bool(is_payed)
        )
        return self.data({"msg": "设置成功"})


class DeliveryRecordSetBonusView(HRBaseView):
    """
    设置内推奖励
    """
    permissions = {
        "post": "recruitment:referral_management"
    }

    class PostForm(SanicForm):
        ids = FieldList(
            StringField(validators=[DataRequired(), UUID()]), min_entries=1, label="投递记录ids"
        )
        referral_bonus = StringField(validators=[Optional(), Length(max=200)], label="内推奖励")

    async def post(self, request):
        form = self.PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        company_id = uuid2str(request.ctx.company_id)
        user_id = uuid2str(request.ctx.user_id)
        await biz.portal_delivery.set_referral_bonus(
            company_id, user_id, ids=form.ids.data, referral_bonus=form.referral_bonus.data
        )
        return self.data({"msg": "设置成功"})


class PortalPostPositionListView(HRBaseView):
    """
    查询内推记录中职位列表(下拉组件)
    """

    async def get(self, request):
        company_id = uuid2str(request.ctx.company_id)
        user_id = uuid2str(request.ctx.user_id)
        res = await biz.portal_page.get_portal_position_for_menu(
            company_id, user_id, ParticipantType.HR
        )
        return self.data(res)
