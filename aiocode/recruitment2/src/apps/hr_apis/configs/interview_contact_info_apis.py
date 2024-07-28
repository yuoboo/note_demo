import wtforms
from sanic_wtf import SanicForm
from wtforms.validators import Required, Optional, Length, UUID

from error_code import Code
from kits.exception import ParamsError
from business.configs.b_interview_info import InterviewInformationBusiness
from utils.api_auth import HRBaseView


class InterviewContactInfo(HRBaseView):
    """
    面试联系人信息
    """
    permissions = {
        "post": "recruitment:common_config",
        "put": "recruitment:common_config",
        "delete": "recruitment:common_config",
    }

    class PostForm(SanicForm):
        linkman = wtforms.StringField(validators=[Required(message="联系人为必填"), Length(max=35)], label="联系人")
        linkman_mobile = wtforms.StringField(validators=[Required(message="联系电话为必填")], label="联系电话")
        address = wtforms.StringField(validators=[Optional(), Length(max=200)], label="详细地址")
        province_id = wtforms.IntegerField(label="省份id")
        city_id = wtforms.IntegerField(label="城市id")
        town_id = wtforms.IntegerField(label="区县id")

    class PutForm(PostForm):
        pass

    async def post(self, request):
        """
        创建面试联系人信息
        """
        form = self.PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        company_id = request.ctx.company_id
        user_id = request.ctx.user_id
        ret = await InterviewInformationBusiness.create_obj(
            company_id, user_id, form.data
        )
        return self.data(ret)

    async def get(self, request):
        """
        获取面试联系人列表
        """
        company_id = request.ctx.company_id
        ret = await InterviewInformationBusiness.get_list(company_id)
        return self.data(ret)

    async def put(self, request, pk):
        """
        编辑面试联系人信息
        """
        form = self.PutForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        company_id = request.ctx.company_id
        user_id = request.ctx.user_id

        ret = await InterviewInformationBusiness.update_obj(
            company_id, user_id, pk, form.data
        )
        return self.data(ret)

    async def delete(self, request, pk):
        """
        删除面试联系人信息
        """
        if not pk:
            raise ParamsError(Code.PARAM_ERROR)
        company_id = request.ctx.company_id
        user_id = request.ctx.user_id
        ret = await InterviewInformationBusiness.delete_obj(
            company_id, user_id, pk
        )
        return self.data(ret)


class InterviewContactInfoSortApi(HRBaseView):
    """
    面试联系人信息 排序
    """

    class PostForm(SanicForm):
        record_ids = wtforms.FieldList(wtforms.StringField(validators=[Required(), UUID()]))

    async def post(self, request):
        form = self.PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        company_id = request.ctx.company_id

        await InterviewInformationBusiness.sort_records(
            company_id, form.record_ids.data
        )
        return self.data({})

