# coding: utf-8
from sanic_wtf import SanicForm
from wtforms import StringField, BooleanField, IntegerField, FieldList, Field
from wtforms.validators import UUID, Required, Length, NumberRange

from business import biz
from utils.api_auth import HRBaseView
from utils.strutils import uuid2str


class ReferralConfigView(HRBaseView):
    """
    内推说明信息设置View
    """
    class PostForm(SanicForm):
        desc_title = StringField(validators=[Length(max=100)], default='', label='内推说明')
        desc = StringField(default='', label='内推说明')

    async def post(self, request):
        """
        添加或者更新内推说明信息
        @param request:
        @return:
        """
        form = self.PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        await biz.referral_config.create_or_update_referral_config(
            request.ctx.company_id, request.ctx.user_id, form.data
        )

        return self.data({})

    async def get(self, request):
        """
        获取内推说明信息
        @param request:
        @return:
        """
        data = await biz.referral_config.get_referral_config(request.ctx.company_id)

        return self.data(data)
