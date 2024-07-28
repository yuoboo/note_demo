import wtforms
from sanic_wtf import SanicForm
from wtforms.validators import Required, DataRequired

from business.configs.b_select_header import SelectHeaderBusiness
from constants import SelectFieldFormType, SelectFieldUserType
from kits import safe_int
from kits.exception import APIValidationError
from utils.api_auth import EmployeeBaseView


class EmpSelectHeaderView(EmployeeBaseView):
    """
    选择表头
    """
    class GetForm(SanicForm):
        scene_type = wtforms.StringField(
            validators=[Required(message="自定义表头场景类型缺失")], label="场景编码"
        )

        def validate_scene_type(self, field):
            if safe_int(field.data) not in SelectFieldFormType.attrs_:
                raise APIValidationError(msg=u"自定义表头用户类型错误")

    class PostForm(SanicForm):
        scene_type = wtforms.StringField(
            validators=[DataRequired(message="自定义表头场景类型缺失")], label="场景编码"
        )
        fields = wtforms.FieldList(wtforms.StringField(validators=[Required()]), min_entries=4)

    async def get(self, request):
        """
        获取表头
        """
        form = self.GetForm(formdata=request.args)
        if not form.validate():
            return self.error(form.errors)

        company_id = request.ctx.user.company_id
        emp_id = request.ctx.user.emp_id
        scene_type = safe_int(form.scene_type.data)

        ret = await SelectHeaderBusiness.get_header_fields(
            company_id, emp_id, scene_type, user_type=SelectFieldUserType.employee
        )
        return self.data(ret)

    async def post(self, request):
        """
        修改表头
        """
        form = self.PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        company_id = request.ctx.user.company_id
        emp_id = request.ctx.user.emp_id
        scene_type = safe_int(form.scene_type.data)

        ret = await SelectHeaderBusiness.update_user_header_fields(
            company_id, emp_id, fields=form.fields.data, scene_type=scene_type,
            user_type=SelectFieldUserType.employee
        )
        return self.data(ret)


class EmpEliminatedReasonView(EmployeeBaseView):
    """
    淘汰原因下拉选项列表 不分页
    """

    async def get(self, request):
        pass
