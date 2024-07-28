from sanic_wtf import SanicForm
from wtforms import StringField, FieldList
from wtforms.validators import DataRequired

from business import biz
from utils.api_auth import BaseView


class CheckHasAllowJoinTalentView(BaseView):
    class PostForm(SanicForm):
        company_id = StringField(validators=[DataRequired()])
        candidate_ids = FieldList(StringField(label="候选人IDs"))

    async def post(self, request):
        """
        检查当前候选人是否可以加入人才库
        """
        form = self.PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)
        data = await biz.candidate_record.check_has_allow_join_talent(
            form.company_id.data, form.candidate_ids.data
        )
        return self.data(data)
