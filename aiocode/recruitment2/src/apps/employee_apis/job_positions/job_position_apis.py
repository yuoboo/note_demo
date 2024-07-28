from sanic_wtf import SanicForm
from wtforms import StringField, FieldList, Field, IntegerField
from wtforms.validators import DataRequired, Length, Optional, UUID, NumberRange
from utils.api_auth import EmployeeBaseView
from business import biz
from utils.sa_db import Paginator
from utils.strutils import uuid2str


class JobPositionTypeView(EmployeeBaseView):
    """
    招聘职位类型前端选择组件源
    """
    async def get(self, request):
        res = await biz.job_position.get_position_type_tree()
        return self.data(res)


class EmpHrJobPositionMenuView(EmployeeBaseView):
    """
    招聘职位前端选择组件源
    """
    class GetForm(SanicForm):
        keyword = StringField(validators=[Optional()], default=None, label="名称关键字")

    async def get(self, request):
        form = self.GetForm(formdata=request.args)
        if not form.validate():
            return self.error(form.errors)

        company_id = uuid2str(request.ctx.user.company_id)
        user_id = await self.get_hr_id(request)
        query_params = form.data
        p, limit = Paginator.get_p_limit(request)
        query_params.update(
            {
                "is_page": True,
                "status": 1,
                "p": p,
                "limit": limit
            }
        )
        res = await biz.job_position.get_position_menu(company_id, user_id, query_params=query_params)
        return self.data(res)

