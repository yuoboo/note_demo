from sanic_wtf import SanicForm
from wtforms import StringField, FieldList

from business import biz
from utils.api_auth import HRBaseView


class CheckHasAllowJoinTalentView(HRBaseView):
    class PostForm(SanicForm):
        candidate_ids = FieldList(StringField(label="候选人IDs"))

    async def post(self, request):
        """
        检查当前候选人是否可以加入人才库
        """
        form = self.PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)
        data = await biz.candidate_record.check_has_allow_join_talent(
            request.ctx.company_id, form.candidate_ids.data
        )
        results = {}
        for key, value in data.items():
            results[key] = value.get('text', '')
        return self.data(results)
