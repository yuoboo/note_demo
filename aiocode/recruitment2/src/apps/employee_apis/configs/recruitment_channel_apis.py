# coding： utf-8
from sanic_wtf import SanicForm
from wtforms import StringField, IntegerField

from business.b_recruitment_channel import RecruitmentChannelBusiness
from utils.api_auth import EmployeeBaseView


class EmployeeRecruitmentChannelView(EmployeeBaseView):

    class GetForm(SanicForm):
        keyword = StringField(label="关键字模糊搜索")
        p = IntegerField(default=1, label='页码')
        limit = IntegerField(default=999, label="每页显示数")

    async def get(self, request):
        """
        渠道列表
        """
        form = self.GetForm(formdata=request.args)
        if not form.validate():
            return self.error(form.errors)

        validated_data = form.data
        data = await RecruitmentChannelBusiness.channel_list(
            request.ctx.user.company_id, validated_data
        )

        return self.data(data)
