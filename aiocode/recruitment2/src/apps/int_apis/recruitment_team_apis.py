from sanic_wtf import SanicForm
from wtforms import StringField, FieldList, IntegerField
from wtforms.validators import DataRequired, UUID, Optional, NumberRange

from business import biz
from utils.api_auth import BaseView
from utils.strutils import uuid2str


class RecruitmentTeamView(BaseView):

    class PostForm(SanicForm):
        company_id = StringField(validators=[DataRequired(), UUID()])
        participant_type = IntegerField(validators=[DataRequired(), NumberRange(min=1, max=2)], label='招聘成员类型')
        ids = FieldList(StringField(validators=[Optional(), UUID()], label="招聘成员ids"))
        fields = FieldList(StringField(default='', label="需要返回的字段列表"))

    async def post(self, request):
        """
        获取企业的招聘团队信息
        """
        form = self.PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        company_id = uuid2str(form.company_id.data)
        participant_type = form.participant_type.data
        participant_ids = form.ids.data or None
        fields = form.fields.data or None

        data = await biz.recruitment_team.get_company_team(
            company_id, participant_type, fields, participant_ids
        )

        return self.data(data)
