
from business import biz
from utils.api_auth import BaseView

from sanic_wtf import SanicForm
from wtforms.fields import StringField, IntegerField
from wtforms.validators import DataRequired, UUID

from utils.strutils import uuid2str


class ParticipantView(BaseView):

    class GetForm(SanicForm):
        company_id = StringField(validators=[DataRequired(), UUID()], label="企业id")
        participant_type = IntegerField(default=None, label="参与者类型")
        fields = StringField(default='', label="查询字段")

    async def get(self, request):
        """
        招聘团队参与者
        """
        form = self.GetForm(formdata=request.args)
        if not form.validate():
            return self.error(form.errors)

        company_id = uuid2str(form.company_id.data)
        fields = form.fields.data
        fields = fields.split(",") if fields else []
        res = await biz.recruit_team.get_participants_for_intranet(
            company_id=company_id, participant_type=form.participant_type.data,
            fields=fields
        )

        return self.data(res)
