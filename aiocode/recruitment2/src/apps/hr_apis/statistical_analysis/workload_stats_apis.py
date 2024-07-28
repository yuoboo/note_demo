# coding: utf-8
import asyncio

from wtforms import BooleanField, DateField, IntegerField, validators

from apps.hr_apis.statistical_analysis import StatsBaseForm
from business.b_statistical_analysis import PositionWorkLoadStatsBusiness, TeamWorkLoadStatsBusiness
from utils.api_auth import HRBaseView
from utils.excel_util import ManySheetListExport


class PostForm(StatsBaseForm):
    status = IntegerField(label="招聘职位状态")
    start_dt = DateField(validators=[validators.Required()], label="开始时间")
    end_dt = DateField(validators=[validators.Required()], label="截止时间")
    filter_none_workload = BooleanField(label="是否过滤没有工作量对象")


class PositionWorkLoadView(HRBaseView):
    """
    职位工作量统计
    """

    @staticmethod
    def _handle_chart_response_data(data_list: list) -> dict:
        x2key_tuple = {
            0: ("record_total", "record_rate"),
            1: ("screen_total", "screen_rate"),
            2: ("follow_interview_total", "follow_interview_rate"),
            3: ("signed_interview_total", "signed_interview_rate"),
            4: ("offered_total", "offered_rate"),
            5: ("employed_total", "employed_rate")
        }
        x_axis = ['添加候选人', '筛选简历', '跟进面试', '面试签到', '发Offer', '确认入职']
        y_axis = [data["name"] for data in data_list]
        series = []
        for x in range(len(x_axis)):
            for y, data in enumerate(data_list):
                key_tuple = x2key_tuple[x]
                series.append(
                    {"x": x, "y": y, "value": data[key_tuple[1]].strip("%"), "num": data[key_tuple[0]]}
                )
        return {"xAxis": x_axis, "yAxis": y_axis, "series": series}

    @staticmethod
    def _handle_sheet_response_data(data: dict) -> dict:
        """
        @param data:
        @return:
        """
        max_interview_count = data.get("max_interview_count")

        header = [
            {'property': 'name', 'label': '招聘职位'},
            {'property': 'record_total', 'label': '添加候选人'},
            {'property': 'record_rate', 'label': '占比'},
            {'property': 'screen_total', 'label': '筛选简历'},
            {'property': 'screen_rate', 'label': '占比'},
            {'property': 'screen_passed_total', 'label': '筛选通过'},
            {'property': 'screen_passed_rate', 'label': '占比'},
            {'property': 'screen_eliminated_total', 'label': '筛选淘汰'},
            {'property': 'screen_eliminated_rate', 'label': '占比'},
            {'property': 'follow_interview_total', 'label': '跟进面试（全部轮次）'},
            {'property': 'follow_interview_rate', 'label': '占比'},
            {'property': 'signed_interview_total', 'label': '面试签到（全部轮次）'},
            {'property': 'signed_interview_rate', 'label': '占比'},
        ]
        for count in range(1, max_interview_count + 1):
            header.extend(
                [
                    {'property': f'follow_interview{count}_count', 'label': f'跟进面试（第{count}轮）'},
                    {'property': f'follow_interview{count}_rate', 'label': '占比'},
                    {'property': f'signed_interview{count}_count', 'label': f'面试签到（第{count}轮）'},
                    {'property': f'signed_interview{count}_rate', 'label': '占比'},
                ]
            )
        header.extend(
            [
                {'property': "offered_total", 'label': "发Offer"},
                {'property': "offered_rate", 'label': "占比"},
                {'property': "employed_total", 'label': "实际入职"},
                {'property': "employed_rate", 'label': "占比"},
            ]
        )
        return {'header': header, 'body': data["list"]}

    async def post(self, request):
        form = PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)
        business = PositionWorkLoadStatsBusiness(request.ctx.company_id, request.ctx.user_id)
        data = await business.position_workload_data(form.data)
        result = self._handle_chart_response_data(data["list"])
        sheet_data = self._handle_sheet_response_data(data)
        result["table"] = sheet_data
        return self.data(result)


class DepartmentWorkLoadView(HRBaseView):
    """
    部门工作量统计
    """

    @staticmethod
    def _handle_chart_response_data(data_list: list) -> dict:
        x2key_tuple = {
            0: ("record_total", "record_rate"),
            1: ("screen_total", "screen_rate"),
            2: ("follow_interview_total", "follow_interview_rate"),
            3: ("signed_interview_total", "signed_interview_rate"),
            4: ("offered_total", "offered_rate"),
            5: ("employed_total", "employed_rate")
        }
        x_axis = ['添加候选人', '筛选简历', '跟进面试', '面试签到', '发Offer', '确认入职']
        y_axis = [data["name"] for data in data_list]
        series = []
        for x in range(len(x_axis)):
            for y, data in enumerate(data_list):
                key_tuple = x2key_tuple[x]
                series.append(
                    {"x": x, "y": y, "value": data[key_tuple[1]].strip("%"), "num": data[key_tuple[0]]}
                )
        return {"xAxis": x_axis, "yAxis": y_axis, "series": series}

    @staticmethod
    def _handle_sheet_response_data(data: dict) -> dict:
        """
        @param data:
        @return:
        """
        max_interview_count = data.get("max_interview_count")
        header = [
            {'property': 'name', 'label': '用人部门'},
            {'property': 'record_total', 'label': '添加候选人'},
            {'property': 'record_rate', 'label': '占比'},
            {'property': 'screen_total', 'label': '筛选简历'},
            {'property': 'screen_rate', 'label': '占比'},
            {'property': 'screen_passed_total', 'label': '筛选通过'},
            {'property': 'screen_passed_rate', 'label': '占比'},
            {'property': 'screen_eliminated_total', 'label': '筛选淘汰'},
            {'property': 'screen_eliminated_rate', 'label': '占比'},
            {'property': 'follow_interview_total', 'label': '跟进面试（全部轮次）'},
            {'property': 'follow_interview_rate', 'label': '占比'},
            {'property': 'signed_interview_total', 'label': '面试签到（全部轮次）'},
            {'property': 'signed_interview_rate', 'label': '占比'}
        ]

        for count in range(1, max_interview_count+1):
            header.extend(
                [
                    {'property': f'follow_interview{count}_count', 'label': f'跟进面试（第{count}轮）'},
                    {'property': f'follow_interview{count}_rate', 'label': '占比'},
                    {'property': f'signed_interview{count}_count', 'label': f'面试签到（第{count}轮）'},
                    {'property': f'signed_interview{count}_rate', 'label': '占比'},
                ]
            )
        header.extend(
            [
                {'property': "offered_total", 'label': "发Offer"},
                {'property': "offered_rate", 'label': "占比"},
                {'property': "employed_total", 'label': "实际入职"},
                {'property': "employed_rate", 'label': "占比"},
            ]
        )

        return {'header': header, 'body': data["list"]}

    async def post(self, request):
        form = PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)
        business = PositionWorkLoadStatsBusiness(request.ctx.company_id, request.ctx.user_id)
        data = await business.department_workload_data(form.data)
        result = self._handle_chart_response_data(data["list"])
        sheet_data = self._handle_sheet_response_data(data)
        result["table"] = sheet_data

        return self.data(result)


class PositionWorkLoadExportView(HRBaseView):
    """
    职位工作量导出
    包含两张sheet: 部门投入工作量, 职位投入工作量
    """
    async def post(self, request):
        form = PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        business = PositionWorkLoadStatsBusiness(request.ctx.company_id, request.ctx.user_id)
        depart_task = business.department_workload_data(form.data)
        position_task = business.position_workload_data(form.data)
        depart_data, position_data = await asyncio.gather(depart_task, position_task)
        # 格式化数据
        depart_sheet = DepartmentWorkLoadView._handle_sheet_response_data(depart_data)
        depart_sheet["sheet_name"] = "部门投入工作量"
        position_sheet = PositionWorkLoadView._handle_sheet_response_data(position_data)
        position_sheet["sheet_name"] = "职位投入工作量"

        exporter = ManySheetListExport(export_data=[depart_sheet, position_sheet])
        return self.data({
            "url": await exporter.get_url("职位投入工作量.xlsx")
        })


class RecruitHRWorkLoadView(HRBaseView):
    """
    招聘HR工作量统计
    """

    @staticmethod
    def _handle_chart_response_data(data_list: list) -> dict:
        x2key_tuple = {
            0: ("record_total", "record_rate"),
            1: ("screen_total", "screen_rate"),
            2: ("arrange_interview_total", "arrange_interview_rate"),
            3: ("follow_interview_total", "follow_interview_rate"),
            4: ("offered_total", "offered_rate"),
            5: ("employed_total", "employed_rate")
        }
        x_axis = ['添加候选人', '筛选简历', '邀约面试', '跟进面试', '发Offer', '相关入职']
        y_axis = [data["name"] for data in data_list]
        series = []
        for x in range(len(x_axis)):
            for y, data in enumerate(data_list):
                key_tuple = x2key_tuple[x]
                series.append(
                    {"x": x, "y": y, "value": data[key_tuple[1]].strip("%"), "num": data[key_tuple[0]]}
                )
        return {"xAxis": x_axis, "yAxis": y_axis, "series": series}

    @staticmethod
    def _handle_sheet_response_data(data_list: list) -> dict:
        """
        @param data_list:
        @return:
        """
        header = [
            {'property': 'name', 'label': '招聘HR'},
            {'property': 'record_total', 'label': '添加候选人'},
            {'property': 'record_rate', 'label': '占比'},
            {'property': 'screen_total', 'label': '筛选简历'},
            {'property': 'screen_rate', 'label': '占比'},
            {'property': 'screen_passed_total', 'label': '筛选通过'},
            {'property': 'screen_passed_rate', 'label': '占比'},
            {'property': 'screen_eliminated_total', 'label': '筛选淘汰'},
            {'property': 'screen_eliminated_rate', 'label': '占比'},
            {'property': 'arrange_interview_total', 'label': '邀请面试'},
            {'property': 'arrange_interview_rate', 'label': '占比'},
            {'property': 'follow_interview_total', 'label': '跟进面试'},
            {'property': 'follow_interview_rate', 'label': '占比'},
            {'property': "offered_total", 'label': "发Offer"},
            {'property': "offered_rate", 'label': "占比"},
            {'property': "employed_total", 'label': "相关入职"},
            {'property': "employed_rate", 'label': "占比"}
        ]

        return {'header': header, 'body': data_list}

    async def post(self, request):
        form = PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)
        business = TeamWorkLoadStatsBusiness(request.ctx.company_id, request.ctx.user_id)
        data = await business.hr_workload_data(form.data)
        result = self._handle_chart_response_data(data)
        sheet_data = self._handle_sheet_response_data(data)
        result["table"] = sheet_data
        return self.data(result)


class RecruitEmpWorkLoadView(HRBaseView):
    """
    面试官工作量统计
    """

    @staticmethod
    def _handle_chart_response_data(data_list: list) -> dict:
        x2key_tuple = {
            0: ("screen_total", "screen_rate"),
            1: ("follow_interview_total", "follow_interview_rate"),
            2: ("employed_total", "employed_rate")
        }
        x_axis = ['筛选简历', '参与面试', '相关入职']
        y_axis = [data["name"] for data in data_list]
        series = []
        for x in range(len(x_axis)):
            for y, data in enumerate(data_list):
                key_tuple = x2key_tuple[x]
                series.append(
                    {"x": x, "y": y, "value": data[key_tuple[1]].strip("%"), "num": data[key_tuple[0]]}
                )
        return {"xAxis": x_axis, "yAxis": y_axis, "series": series}

    @staticmethod
    def _handle_sheet_response_data(data_list: list) -> dict:
        """
        @param data_list:
        @return:
        """
        header = [
            {'property': 'name', 'label': '面试官'},
            {'property': 'screen_total', 'label': '筛选简历'},
            {'property': 'screen_rate', 'label': '占比'},
            {'property': 'screen_passed_total', 'label': '筛选简历通过'},
            {'property': 'screen_passed_rate', 'label': '占比'},
            {'property': 'screen_eliminated_total', 'label': '筛选简历淘汰'},
            {'property': 'screen_eliminated_rate', 'label': '占比'},
            {'property': 'follow_interview_total', 'label': '参与面试'},
            {'property': 'follow_interview_rate', 'label': '占比'},
            {'property': "employed_total", 'label': "相关入职"},
            {'property': "employed_rate", 'label': "占比"}
        ]

        return {'header': header, 'body': data_list}

    async def post(self, request):
        form = PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)
        business = TeamWorkLoadStatsBusiness(request.ctx.company_id, request.ctx.user_id)
        data = await business.hr_workload_data(form.data)
        result = self._handle_chart_response_data(data)
        sheet_data = self._handle_sheet_response_data(data)
        result["table"] = sheet_data
        return self.data(result)


class RecruitmentTeamWorkLoadExportView(HRBaseView):
    """
    招聘团队工作量导出
    包含两个sheet：
    """

    async def post(self, request):
        form = PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        business = TeamWorkLoadStatsBusiness(
            company_id=request.ctx.company_id, user_id=request.ctx.user_id
        )
        hr_task = business.hr_workload_data(form.data)
        emp_task = business.emp_workload_data(form.data)
        hr_data, emp_data = await asyncio.gather(hr_task, emp_task)
        # 格式化数据

        hr_sheet = RecruitHRWorkLoadView._handle_sheet_response_data(hr_data)
        hr_sheet["sheet_name"] = "招聘HR工作量"
        _data = [hr_sheet]
        if not form.participant_ids.data:
            # 如果有HR筛选条件则不用导出员工工作量sheet
            emp_sheet = RecruitEmpWorkLoadView._handle_sheet_response_data(emp_data)
            emp_sheet["sheet_name"] = "面试官工作量"
            _data.append(emp_sheet)

        exporter = ManySheetListExport(export_data=_data)
        return self.data({
            "url": await exporter.get_url(file_name="招聘团队工作量统计表.xlsx")
        })
