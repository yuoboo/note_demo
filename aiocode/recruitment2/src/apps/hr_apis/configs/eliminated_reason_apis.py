from sanic_wtf import SanicForm
import wtforms
from wtforms.validators import Required, UUID, Length, NumberRange, Optional

from utils.api_auth import HRBaseView
from kits.exception import APIValidationError
from business.configs.b_eliminated_reason import EliminatedReasonBusiness


class EliminatedReasonApi(HRBaseView):
    """
    淘汰原因  增删改查
    """

    class PostForm(SanicForm):
        reason = wtforms.StringField(validators=[Required()], label="淘汰原因")
        reason_step = wtforms.IntegerField(validators=[Required(), NumberRange(1, 3)], label="淘汰原因所属阶段")

    class GetForm(SanicForm):
        p = wtforms.IntegerField(default=1, label="页数")
        limit = wtforms.IntegerField(default=20, label="每页条数")
        reason_step = wtforms.IntegerField(validators=[Optional(), NumberRange(1, 3)])

    class PutForm(PostForm):
        reason = wtforms.StringField(validators=[Required(), Length(min=1, max=20)], label='淘汰原因')
        record_id = wtforms.StringField(validators=[Required(), UUID()], label='淘汰记录id')

    class DeleteForm(SanicForm):
        record_id = wtforms.StringField(validators=[Required(), UUID()], label='淘汰记录id')

    async def post(self, request):
        """
        新增淘汰原因
        """
        form = self.PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        company_id = request.ctx.company_id
        user_id = request.ctx.user_id

        _id = await EliminatedReasonBusiness.create_reason(
            company_id=company_id, user_id=user_id,
            reason_step=form.reason_step.data, reason=form.reason.data
        )

        return self.data({"id": _id})

    async def delete(self, request):
        """
        删除淘汰原因
        """
        form = self.DeleteForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        company_id = request.ctx.company_id
        user_id = request.ctx.user_id

        await EliminatedReasonBusiness.delete_reason(
            company_id=company_id, user_id=user_id, record_id=form.record_id.data
        )
        return self.data({"msg": "删除成功"})

    async def put(self, request):
        """
        修改淘汰原因
        """
        form = self.PutForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        company_id = request.ctx.company_id
        user_id = request.ctx.user_id

        _id = await EliminatedReasonBusiness.update_reason(
            company_id=company_id, user_id=user_id,
            record_id=form.record_id.data, reason=form.reason.data
        )
        return self.data({"id": _id})

    async def get(self, request):
        """
        获取淘汰原因列表  分页
        """
        form = self.GetForm(formdata=request.args)
        if not form.validate():
            return self.error(form.errors)

        company_id = request.ctx.company_id

        ret = await EliminatedReasonBusiness.get_list_with_pagination(
            company_id=company_id, page=form.p.data, limit=form.limit.data,
            reason_step=form.reason_step.data
        )
        return self.data(ret)


class EliminatedReasonSortApi(HRBaseView):
    """
    淘汰原因 排序
    """
    class PostForm(SanicForm):
        record_ids = wtforms.FieldList(
            wtforms.StringField(validators=[Required(), UUID()]), min_entries=1, label="淘汰记录id列表"
        )

    async def post(self, request):
        form = self.PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        company_id = request.ctx.company_id
        user_id = request.ctx.user_id

        await EliminatedReasonBusiness.sort_reasons(
            company_id=company_id, user_id=user_id, record_ids=form.record_ids.data
        )
        return self.data({"msg": "排序完成"})


class EliminatedReasonSelectListApi(HRBaseView):
    """
    淘汰原因 下拉选项列表 不分页
    """

    class GetForm(SanicForm):
        reason_step = wtforms.StringField(label='淘汰原因阶段')

    async def get(self, request):
        form = self.GetForm(formdata=request.args)
        if not form.validate():
            return self.error(form.errors)

        company_id = request.ctx.company_id

        reason_step = form.reason_step.data
        if reason_step:
            try:
                reason_step = int(reason_step)
            except ValueError:
                raise APIValidationError(msg="reason_step 参数错误")
        else:
            reason_step = None

        ret = await EliminatedReasonBusiness.get_reason_select_list(
            company_id=company_id, reason_step=reason_step
        )
        return self.data(ret)


class EliminatedReasonStepConfigApi(HRBaseView):
    """
    各阶段面试淘汰原因概况统计
    """

    async def get(self, request):
        company_id = request.ctx.company_id

        ret = await EliminatedReasonBusiness.get_count_by_reason_step(company_id=company_id)
        return self.data(ret)

