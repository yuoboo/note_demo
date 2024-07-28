
from sanic_wtf import SanicForm
import wtforms
from wtforms.validators import DataRequired, Required

from constants import SelectFieldFormType, SelectFieldUserType
from kits import safe_int
from utils.api_auth import HRBaseView
from kits.exception import APIValidationError
from business.configs.b_select_header import SelectHeaderBusiness


class SelectHeaderView(HRBaseView):
    """
    自定义表头相关接口
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

    async def post(self, request):
        """
        保存自定义表头配置
        """
        form = self.PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        company_id = request.ctx.company_id
        user_id = request.ctx.user_id
        scene_type = safe_int(form.scene_type.data)
        ret = await SelectHeaderBusiness.update_user_header_fields(
            company_id=company_id, user_id=user_id, fields=form.fields.data, scene_type=scene_type,
            user_type=SelectFieldUserType.hr
        )
        return self.data(ret)

    async def get(self, request):
        """
        获取自定义表头信息
        """
        form = self.GetForm(formdata=request.args)
        if not form.validate():
            return self.error(form.errors)

        company_id = request.ctx.company_id
        user_id = request.ctx.user_id
        scene_type = safe_int(form.scene_type.data)
        ret = await SelectHeaderBusiness.get_header_fields(
            company_id=company_id, user_id=user_id, scene_type=scene_type,
            user_type=SelectFieldUserType.hr
        )
        return self.data(ret)



