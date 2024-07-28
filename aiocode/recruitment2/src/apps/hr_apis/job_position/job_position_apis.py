# coding: utf-8
from sanic_wtf import SanicForm
from wtforms import StringField, FieldList, IntegerField
from wtforms.validators import Required, UUID, Optional

from business import biz
from utils.api_auth import HRBaseView
from utils.api_util import format_request_args
from utils.strutils import uuid2str


class JobPositionSetReferralBonusView(HRBaseView):
    class PostForm(SanicForm):
        job_position_ids = FieldList(StringField(validators=[Required(), UUID()]), min_entries=1)  # 招聘职位IDs
        referral_bonus = StringField()

    async def post(self, request):
        """
        设置招聘职位的内推奖金
        """
        form = self.PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)
        company_id = request.ctx.company_id
        user_id = request.ctx.user_id
        res = await biz.job_position.set_positions_referral_bonus(
            company_id, user_id, form.job_position_ids.data, form.referral_bonus.data
        )
        return self.data(res)


class JobPositionCityListView(HRBaseView):

    async def get(self, request):
        data = await biz.job_position.position_city_list(
            request.ctx.company_id, request.ctx.user_id
        )

        return self.data(data)


class JobPositionDepartmentTreeView(HRBaseView):
    """
    部门树
    """
    class GetForm(SanicForm):
        scene_type = IntegerField(default=None, label="场景代码,1.内推职位场景")

    async def get(self, request):
        form = self.GetForm(formdata=request.args)
        if not form.validate():
            return self.error(form.errors)

        company_id = uuid2str(request.ctx.company_id)
        res = await biz.portal_page.get_position_department_tree(
            company_id, scene_type=form.scene_type.data)
        return self.data(res)


class JobPositionTypeTreeView(HRBaseView):
    """
    招聘职位类型树 前端选择组件源
    """
    async def get(self, request):
        res = await biz.job_position.get_position_type_tree()
        return self.data(res)


class ReferralJobPositionView(HRBaseView):
    class GetForm(SanicForm):
        keyword = StringField()
        is_referral_bonus = IntegerField()
        dep_ids = StringField()
        status = IntegerField()
        work_type = IntegerField()
        province_id = IntegerField()
        city_id = IntegerField()
        p = IntegerField()
        limit = IntegerField()

    async def get(self, request):
        """
        获取内推设置职位列表
        :param request:
        :return:
        """
        form = self.GetForm(formdata=request.args)
        if not form.validate():
            return self.error(form.errors)

        data = await biz.job_position.get_portals_position_list(
            request.ctx.company_id, request.ctx.user_id, form.data
        )
        return self.data(data)
