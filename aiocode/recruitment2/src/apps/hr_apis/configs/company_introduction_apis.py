# coding: utf-8
from sanic_wtf import SanicForm
from wtforms import IntegerField, FloatField, StringField, validators

from business import biz
from utils.api_auth import HRBaseView


class PostForm(SanicForm):
    id = StringField()
    company_name = StringField(validators=[validators.Required()], label='企业名称')
    company_scale_id = IntegerField(validators=[validators.Required()], label='企业规模ID')
    industry_id = IntegerField(validators=[validators.Required()], label='行业ID')
    second_industry_id = IntegerField(label='二级行业ID')
    contacts = StringField(validators=[validators.Required(), validators.Length(max=20)], label="联系人")
    contact_number = StringField(validators=[validators.Required(), validators.Length(max=100)], label="联系电话")
    contact_email = StringField(validators=[validators.Length(max=50)], label="联系邮箱")
    company_address = StringField(label='所在地址', validators=[validators.Required(), validators.Length(max=50)])
    address_longitude = FloatField(label="地址经度")
    address_latitude = FloatField(label="address_latitude")

    company_desc = StringField(label='企业简介', validators=[validators.Required()])
    welfare_tag = StringField(label="福利标签", validators=[validators.Length(max=1000)])
    logo_url = StringField(label="企业logo", validators=[validators.Length(max=200)])
    image_url = StringField(label="公司照片", validators=[validators.Length(max=2000)])
    qrcode_url = StringField(label="企业联系人二维码", validators=[validators.Length(max=256)])
    qrcode_type = IntegerField(label="二维码类型")
    qrcode_user_id = StringField(label="二维码类型关联用户id")


class CompanyIntroductionListView(HRBaseView):

    class GetForm(SanicForm):
        p = IntegerField(default=1, label='页码')
        limit = IntegerField(default=100, label="每页显示数")

    async def get(self, request):
        """
        获取企业介绍列表
        """
        form = self.GetForm(formdata=request.args)
        if not form.validate():
            return self.error(form.errors)

        company = request.ctx.company
        data = await biz.com_intro.get_introduction_list(
            request.ctx.company_id, form.data, fullname=company.fullname, shortname=company.shortname
        )
        return self.data(data)


class CompanyIntroductionCreateView(HRBaseView):
    """
    @desc 添加企业介绍
    """
    async def post(self, request):
        form = PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        res = await biz.com_intro.create_company_intro(request.ctx.company_id, request.ctx.user_id, form.data)
        return self.data(res)


class CompanyIntroductionUpdateView(HRBaseView):
    """
    @desc 修改企业介绍
    """
    async def post(self, request):
        form = PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        res = await biz.com_intro.update_company_intro(request.ctx.company_id, request.ctx.user_id, form.data)
        return self.data(res)


class UpdateIntroductionQrCodeView(HRBaseView):
    """
    更新企业介绍联系人二维码
    """
    class PostForm(SanicForm):
        id = StringField()
        qrcode_url = StringField(label="企业联系人二维码", validators=[validators.Length(max=256)])
        qrcode_type = IntegerField(label="二维码类型")
        qrcode_user_id = StringField(label="二维码类型关联用户id")

    async def post(self, request):
        form = self.PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        res = await biz.com_intro.update_company_intro(request.ctx.company_id, request.ctx.user_id, form.data)
        return self.data(res)


class CompanyIntroductionDeleteView(HRBaseView):
    """
    @desc 修改企业介绍
    """
    async def post(self, request):
        record_id = request.json.get("id", "")
        res = await biz.com_intro.delete_company_intro(request.ctx.company_id, request.ctx.user_id, record_id)
        return self.data(res)


class CompanyIntroductionSortView(HRBaseView):
    """
    @desc 修改企业介绍
    """
    async def post(self, request):
        record_ids = request.json.get("record_ids", "")
        res = await biz.com_intro.sort_company_intro(request.ctx.company_id, request.ctx.user_id, record_ids)
        return self.data(res)

