from sanic_wtf import SanicForm
from wtforms import StringField
from wtforms.validators import DataRequired, UUID, Optional

from business.b_recruitment_channel import IntranetChannelBiz
from business.configs.b_common import CommonBusiness
from business.configs.b_eliminated_reason import IntranetEliminateReasonBiz
from utils.api_auth import BaseView
from utils.api_util import format_request_args
from utils.strutils import uuid2str


class EmpIdConvertHrIdView(BaseView):
    async def get(self, request):
        """
        员工id换hr id
        """
        params = format_request_args(request.args)
        data = await CommonBusiness.get_hr_by_emp_id(
            params.get('company_id', None), params.get('emp_id', None)
        )
        return self.data(data)


class EliminatedReasonView(BaseView):
    """
    获取指定淘汰原因信息
    """

    class GetForm(SanicForm):
        company_id = StringField(validators=[DataRequired(), UUID()])
        ids = StringField(validators=[Optional()], default='', label="淘汰原因ids, 使用逗号,隔开")
        fields = StringField(default='', label="需要返回的字段列表, 使用逗号,隔开")

    async def get(self, request):
        """
        查询淘汰原因
        """
        form = self.GetForm(formdata=request.args)
        if not form.validate():
            return self.error(form.errors)

        ids = str(form.ids.data or '').split(",")
        fields = str(form.fields.data).split(",") if form.fields.data else []
        company_id = uuid2str(form.company_id.data)

        res = await IntranetEliminateReasonBiz.get_reason_info(
            company_id=company_id, ids=[uuid2str(_id) for _id in ids if _id], fields=fields
        )
        return self.data(res)


class RecruitmentChannelView(BaseView):
    """
    获取指定招聘渠道信息
    """

    class GetForm(SanicForm):
        company_id = StringField(validators=[DataRequired(), UUID()])
        ids = StringField(validators=[Optional()], default='', label="招聘渠道ids, 使用逗号,隔开")
        fields = StringField(default='', label="需要返回的字段列表, 使用逗号,隔开")

    async def get(self, request):

        form = self.GetForm(formdata=request.args)
        if not form.validate():
            return self.error(form.errors)

        ids = str(form.ids.data or '').split(",")
        fields = str(form.fields.data).split(",") if form.fields.data else []
        company_id = uuid2str(form.company_id.data)

        res = await IntranetChannelBiz.get_channel_info(
            company_id=company_id, ids=[uuid2str(_id) for _id in ids if _id], fields=fields
        )
        return self.data(res)
