# -*- coding: utf-8 -*-
from sanic_wtf import SanicForm
from wtforms import StringField, IntegerField, BooleanField
from wtforms.validators import UUID, Optional, Required
from business import biz
from utils.api_auth import EmployeeBaseView
from utils.strutils import uuid2str


class EmpPortalPositionListView(EmployeeBaseView):
    class PostForm(SanicForm):
        job_name = StringField()  # 职位名搜索词
        secondary_cate = StringField()  # 职位类型
        has_bonus = BooleanField()  # 是否有内推奖金
        city_id = IntegerField()  # 市
        portal_page_id = StringField(validators=[Required()])  # 门户网页ID
        p = IntegerField(default=1)
        limit = IntegerField(default=20)

    async def post(self, request):
        """
        网页职位列表
        """
        company_id = request.ctx.user.company_id

        form = self.PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        portal_page_id = request.json.get("portal_page_id")
        ret = await biz.portal_page.get_portal_position_list(
            company_id, request.json, portal_page_id, is_page=True
        )
        return self.data(ret)


class EmpPortalPositionSelectListView(EmployeeBaseView):

    async def get(self, request):
        """
        内推职位列表(下拉数据源)
        """
        company_id = request.ctx.user.company_id
        portal_page_id = request.args.get("portal_page_id")
        if not portal_page_id:
            return self.error("招聘门户ID缺失")

        ret = await biz.portal_page.get_portal_position_list(
            company_id, {}, portal_page_id, select_data=True
        )
        return self.data(ret)


class EmpPortalPositionDetailView(EmployeeBaseView):
    """
    @desc 网页职位详情
    """
    class GetForm(SanicForm):
        id = StringField(validators=[UUID()])

    async def get(self, request):
        form = self.GetForm(formdata=request.args)
        if not form.validate():
            return self.error(form.errors)

        record_id = uuid2str(form.data.get("id"))
        res = await biz.portal_page.get_portal_position_detail(request.ctx.user.company_id, record_id)
        return self.data(res)


class EmpReferRecordPositionListView(EmployeeBaseView):
    """
    查询内推记录中职位列表(下拉组件)
    """

    async def get(self, request):
        company_id = uuid2str(request.ctx.user.company_id)
        emp_id = uuid2str(request.ctx.user.emp_id)
        res = await biz.portal_page.get_portal_position_for_menu(
            company_id, emp_id
        )
        return self.data(res)


class EmpPortalPositionListFilterView(EmployeeBaseView):
    """
    招聘门户 城市/职位类型 筛选源：根据招聘网页信息返回筛选结果
    """
    class GetForm(SanicForm):
        page_id = StringField(validators=[Optional(), UUID()], default=None, label="招聘网页id")

    async def get(self, request):
        form = self.GetForm(formdata=request.args)
        if not form.validate():
            return self.error(form.errors)

        company_id = request.ctx.user.company_id
        ret = await biz.portal_page.get_position_type_and_city(
            company_id=company_id, page_id=uuid2str(form.page_id.data)
        )
        return self.data(ret)


class EmpPortalDepartmentTreeView(EmployeeBaseView):
    """
    员工端部门选择树
    """
    class GetForm(SanicForm):
        scene_type = IntegerField(default=None, label="场景代码,1.内推职位场景")

    async def get(self, request):
        form = self.GetForm(formdata=request.args)
        if not form.validate():
            return self.error(form.errors)

        company_id = uuid2str(request.ctx.user.company_id)
        res = await biz.portal_page.get_position_department_tree(
            company_id, scene_type=form.scene_type.data)
        return self.data(res)
