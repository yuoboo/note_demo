from sanic_wtf import SanicForm
from wtforms import IntegerField, StringField, validators, TextField, FieldList, Field

from business import biz
from utils.api_auth import HRBaseView


class EmailTemplateView(HRBaseView):
    """
    通知模板  主要是邮件通知模板
    包括 面试 淘汰， 参数 usage: '2' 面试, '3' 淘汰
    """

    class PostForm(SanicForm):
        usage = IntegerField(
            validators=[validators.data_required(), validators.NumberRange(min=1, max=4)], label='模板类型'
        )
        name = StringField(
            validators=[validators.data_required(), validators.Length(min=1, max=50)], label='模板名称'
        )

    class GetForm(SanicForm):
        usage = IntegerField(
            validators=[validators.data_required(), validators.NumberRange(min=1, max=4)], label='模板类型'
        )

    class PutForm(SanicForm):
        name = StringField(
            validators=[validators.data_required(), validators.Length(min=1, max=50)], label='模板名称'
        )
        email_title = StringField(
            validators=[validators.data_required(), validators.Length(min=1, max=100)], label='模板标题'
        )
        email_content = TextField(
            validators=[validators.data_required()], label='模板内容'
        )
        id = StringField(
            validators=[validators.data_required(), validators.Length(min=1, max=36)], label='模板ID'
        )
        attaches = FieldList(Field(), label='模板附件')

    class DeleteForm(SanicForm):
        template_id = StringField(
            validators=[validators.data_required(), validators.Length(min=1, max=36)], label='模板ID'
        )

    async def post(self, request):
        """
        创建模板
        """
        form = self.PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)
        data = await biz.email_template.create_template(
            request.ctx.company_id, request.ctx.user_id, form.data
        )

        return self.data(data)

    async def put(self, request):
        """
        编辑模板
        """
        form = self.PutForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)
        data = await biz.email_template.update_template(
            request.ctx.company_id, request.ctx.user_id, form.data
        )

        return self.data(data)

    async def delete(self, request):
        """
        删除模板
        """
        form = self.DeleteForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)
        await biz.email_template.delete_template(
            request.ctx.company_id, request.ctx.user_id, form.template_id.data
        )
        return self.data({})

    async def get(self, request):
        """
        邮件列表
        """
        form = self.GetForm(formdata=request.args)
        if not form.validate():
            return self.error(form.errors)
        data = await biz.email_template.get_templates(
            request.ctx.company_id, request.ctx.user_id, form.data
        )

        return self.data(data)


class OfferEmailTemplateView(HRBaseView):
    """
    Offer通知模板  主要是邮件通知模板
    """

    async def post(self, request):
        """
        创建模板
        """
        pass

    async def put(self, request):
        """
        编辑模板
        """
        pass

    async def delete(self, request):
        """
        删除模板
        """
        pass

    async def get(self, request):
        """
        邮件列表
        """
        pass
