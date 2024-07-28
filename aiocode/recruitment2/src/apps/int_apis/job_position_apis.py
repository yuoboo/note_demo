from sanic_wtf import SanicForm
from wtforms import StringField, FieldList
from wtforms.validators import DataRequired, UUID, Optional

from business.b_job_position import IntranetJobPositionBusiness
from utils.api_auth import BaseView
from utils.strutils import uuid2str


class SelectJobPositionView(BaseView):
    """
    查询指定招聘需求信息
    """

    class PostForm(SanicForm):
        company_id = StringField(validators=[DataRequired(), UUID()])
        ids = FieldList(StringField(validators=[Optional(), UUID()], label="招聘需求ids"))
        fields = FieldList(StringField(default='', label="需要返回的字段列表"))

    async def post(self, request):

        form = self.PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        company_id = uuid2str(form.company_id.data)
        ids = [uuid2str(_id) for _id in form.ids.data if _id]

        res = await IntranetJobPositionBusiness.get_job_position_info(
            company_id=company_id, ids=ids, fields=form.fields.data
        )
        return self.data(res)
