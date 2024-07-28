from sanic_wtf import SanicForm
from wtforms import StringField, FieldList, IntegerField
from wtforms.validators import DataRequired, UUID, Optional, NumberRange

from business import biz
from utils.api_auth import BaseView
from utils.strutils import uuid2str


class PortalPageView(BaseView):

    class PostForm(SanicForm):
        company_id = StringField(validators=[DataRequired(), UUID()])
        ids = FieldList(StringField(validators=[Optional(), UUID()], label="招聘门户ids"))
        fields = FieldList(StringField(default='', label="需要返回的字段列表"))

    async def post(self, request):
        """
        获取企业的招聘门户信息
        """
        form = self.PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        company_id = uuid2str(form.company_id.data)
        ids = form.ids.data or None
        fields = form.fields.data or None

        data = await biz.intranet.portal_page.get_portal_page(
            company_id, ids, fields
        )

        return self.data(data)
