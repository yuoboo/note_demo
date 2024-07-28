from sanic_wtf import SanicForm
from wtforms import StringField, FieldList
from wtforms.validators import DataRequired, UUID

from business.commons import com_biz
from utils.api_auth import BaseView
from utils.strutils import uuid2str


class FieldConvertView(BaseView):
    class PostForm(SanicForm):
        company_id = StringField(validators=[DataRequired(), UUID()])
        hr_participant_ids = FieldList(StringField(label="招聘HRid"))
        job_position_ids = FieldList(StringField(label="职位id"))
        channel_ids = FieldList(StringField(label="渠道id"))
        emp_participant_ids = FieldList(StringField(label="面试官id"))
        portal_page_ids = FieldList(StringField(label="招聘门户id"))

    async def post(self, request):
        """
        删除投递记录
        @param request:
        @return:
        """
        form = self.PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        company_id = uuid2str(form.company_id.data)
        results = await com_biz.data_report.common.field_convert(company_id, form.data)

        return self.data(results)
