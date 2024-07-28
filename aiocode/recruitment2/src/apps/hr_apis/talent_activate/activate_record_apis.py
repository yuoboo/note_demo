from sanic_wtf import SanicForm
from wtforms import FieldList, StringField, IntegerField, Field
from wtforms.validators import Required

from business import biz
from utils.api_auth import HRBaseView


class ActivateRecordView(HRBaseView):

    class PostForm(SanicForm):
        candidates = FieldList(Field(), label="候选人信息")
        portal_page_id = StringField(label="门户网页ID")
        page_position_id = StringField(label="网页职位ID")
        email_template_id = StringField(label="邮件模板ID")
        send_email_id = StringField(label="发送邮件ID", default='')
        sms_template_id = IntegerField(label="短信模板ID")
        notify_way = IntegerField(validators=[Required()], label="通知方式：1-短信 2-邮件 3-短信、邮件")

    async def post(self, request):
        """
        yapi地址：http://yapi.2haohr.com:4000/project/819/interface/api/117344
        发起人才激活
        @param request:
        @return:
        """
        form = self.PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        data = await biz.activate_record.create_records(
            request.ctx.company_id, request.ctx.user_id, form.data
        )

        return self.data(data)


class TryActivateView(HRBaseView):
    """
    激活试发
    """

    class PostForm(SanicForm):
        candidates = FieldList(Field(), label="候选人信息")
        portal_page_id = StringField(label="门户网页ID")
        page_position_id = StringField(label="网页职位ID")
        email_template_id = StringField(label="邮件模板ID")
        send_email_id = StringField(label="发送邮件ID", default='')
        sms_template_id = IntegerField(label="短信模板ID")
        notify_way = IntegerField(validators=[Required()], label="通知方式：1-短信 2-邮件 3-短信、邮件")
        receiver_mobile = StringField(label="试发接收人手机号", default='')
        receiver_email = StringField(label="试发接收人邮件", default='')

    async def post(self, request):
        """
        yapi地址：http://yapi.2haohr.com:4000/project/819/interface/api/122685
        @param request:
        @return:
        """
        form = self.PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        await biz.activate_record.activate_try(
            request.ctx.company_id, request.ctx.user_id, form.data
        )

        return self.data({})

    async def get(self, request):
        """
        试发次数查询
        yapi地址：http://yapi.2haohr.com:4000/project/819/interface/api/122692
        @param request:
        @return:
        """
        data = await biz.activate_record.activate_try_count(
            request.ctx.company_id, request.ctx.user_id
        )

        return self.data(data)


class ActivateRecordListView(HRBaseView):

    class PostForm(SanicForm):
        add_by_ids = FieldList(StringField(label="添加人"))
        portal_page_id = StringField(label="门户网页ID")
        keyword = StringField(label="关键字")
        start_dt = StringField(label="添加时间（开始）")
        end_dt = StringField(label="结束时间（结束）")
        candidate_status = FieldList(IntegerField(label="应聘记录状态"))
        activate_status = IntegerField(label="激活状态")
        p = IntegerField(default=1, label="页码")
        limit = IntegerField(default=10, label="单页数量")

    async def post(self, request):
        """
        yapi地址：http://yapi.2haohr.com:4000/project/819/interface/api/117428
        @param request:
        @return:
        """
        form = self.PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        data = await biz.activate_record.record_list(
            request.ctx.company_id, form.data
        )

        return self.data(data)


class ActivateRecordPortalListView(HRBaseView):
    """
    激活记录中门户列表
    """

    async def get(self, request):
        """
        yapi: http://yapi.2haohr.com:4000/project/819/interface/api/117449
        @param request:
        @return:
        """
        data = await biz.activate_record.record_portal_list(
            request.ctx.company_id
        )

        return self.data(data)


class CandidateActivateCountView(HRBaseView):
    """
    人才本月激活次数
    """

    async def get(self, request):
        """
        yapi地址：http://yapi.2haohr.com:4000/project/819/interface/api/117505
        @param request:
        @return:
        """
        candidate_id = request.args.get("candidate_id")
        if not candidate_id:
            return self.error("参数错误")
        data = await biz.activate_record.talent_activate_count(
            request.ctx.company_id, candidate_id
        )

        return self.data(data)
