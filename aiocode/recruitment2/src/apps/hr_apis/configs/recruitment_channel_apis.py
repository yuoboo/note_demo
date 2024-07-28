# coding: utf-8
from sanic_wtf import SanicForm
from wtforms import StringField, IntegerField, BooleanField
from wtforms.validators import Required, Length, UUID

from business.b_recruitment_channel import RecruitmentChannelBusiness
from constants import ShowColor
from utils.api_auth import HRBaseView
from utils.sa_db import Paginator


class RecruitmentChannelView(HRBaseView):

    class GetForm(SanicForm):
        keyword = StringField(label="关键字模糊搜索")
        p = IntegerField(label='页码')
        limit = IntegerField(label="每页显示数")

    class PostForm(SanicForm):
        name = StringField(validators=[Required(), Length(max=10)], label="名称")
        related_url = StringField(default='', label="相关主页地址")
        remark = StringField(default='', validators=[Length(max=200)], label="备注")
        show_color = StringField(default=ShowColor.black, label="显示颜色")

    class PutForm(PostForm):
        u_id = StringField(validators=[Required(), UUID()], label="记录ID")

    async def get(self, request):
        """
        渠道列表
        """
        form = self.GetForm(formdata=request.args)
        if not form.validate():
            return self.error(form.errors)

        validated_data = form.data
        page, limit = Paginator.get_p_limit(request)
        validated_data['p'] = page
        validated_data['limit'] = limit
        data = await RecruitmentChannelBusiness.channel_list(
            request.ctx.company_id, validated_data
        )

        return self.data(data)

    async def post(self, request):
        """
        添加渠道
        """
        form = self.PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)
        data = await RecruitmentChannelBusiness.create_channel(
            request.ctx.company_id, request.ctx.user_id,
            form.data
        )

        return self.data(data)

    async def put(self, request):
        """
        更新渠道
        """
        form = self.PutForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)
        validated_data = form.data

        u_id = validated_data.pop("u_id")
        data = await RecruitmentChannelBusiness.update_channel(
            request.ctx.company_id, request.ctx.user_id,
            u_id, validated_data
        )

        return self.data(data)


class RecruitmentChannelStatusView(HRBaseView):

    class PostForm(SanicForm):
        u_id = StringField(validators=[Required(), UUID()], label="记录ID")
        is_forbidden = BooleanField(validators=[Required()], label="是否禁用")

    async def put(self, request):
        """
        启用、禁用
        """
        form = self.PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)
        validated_data = form.data

        u_id = validated_data.pop("u_id")
        data = await RecruitmentChannelBusiness.update_channel(
            request.ctx.company_id, request.ctx.user_id,
            u_id, validated_data
        )

        return self.data(data)
