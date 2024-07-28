# coding: utf-8
import asyncio

from wtforms import IntegerField, BooleanField

from apps.hr_apis.statistical_analysis import StatsBaseForm
from business.b_statistical_analysis import RecruitProgressBusiness
from constants import RecruitProgressType
from utils.api_auth import HRBaseView
from utils.excel_util import ManySheetListExport
from utils.number_cal import to_decimal


class PostForm(StatsBaseForm):
    status = IntegerField(label="招聘职位状态")
    filter_full = BooleanField(label="是否过滤已招满职位")
    scene_type = IntegerField(label="维度编码（1：职位 2：部门 3：岗位类别）")
    clear_total = BooleanField(default=True, label='职位是否明确计划招聘人数')  # 此参数不需要前端传， 默认过滤逻辑


class RecruitProgressView(HRBaseView):
    """
    招聘进度统计分析(chart)
    """

    @staticmethod
    def _handle_chart_response_data(result_data: dict):
        """
        处理chart接口返回
        """
        ret = {}
        series = []
        total_employed_count = result_data.get("total_employed_count")
        total_position_total = result_data.get("total_position_total")

        for item in result_data.get("list", []):
            position_total = item.get("position_total")
            employed_count = item.get("employed_count") or 0
            max_num = max([position_total, employed_count])
            if (max_num % 5) == 0:
                range_num = max_num
            else:
                range_num = max_num + 5 - (max_num % 5)
            progress = f'{to_decimal(employed_count / position_total, 1) * 100}'
            series.append(
                {
                    "title": item["name"],
                    "range": range_num,
                    "actual": employed_count,
                    "target": position_total,
                    "rate": progress
                }
            )

        ret['series'] = series
        ret.update(
            {
                "series": series,
                "position_count": result_data.get("position_count"),
                "total_employed_count": total_employed_count,
                "total_position_total": total_position_total,
                "progress": f'{to_decimal(total_employed_count / total_position_total) * 100}' if total_position_total else "-"
            }
        )

        return ret

    async def post(self, request):
        form = PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)
        validated_data = form.data
        scene_type = validated_data.get("scene_type")
        business = RecruitProgressBusiness(
            request.ctx.company_id, request.ctx.user_id
        )
        if scene_type == RecruitProgressType.position:
            data = await business.position_progress_chart(validated_data)
        elif scene_type == RecruitProgressType.department:
            data = await business.department_progress(validated_data)
        elif scene_type == RecruitProgressType.title_cate:
            data = await business.title_group_progress(validated_data)
        else:
            return self.error("参数错误")
        data = self._handle_chart_response_data(data)
        return self.data(data)


class RecruitProgressSheetView(HRBaseView):
    """
    招聘进度统计分析(sheet)
    """
    @staticmethod
    def _handle_sheet_response_data(data, scene_type):
        data_list = data.get("list") or []
        ret = {"body": data_list}
        header = []
        if scene_type == RecruitProgressType.position:
            header.extend(
                [
                    {'label': '招聘职位', 'property': 'name'},
                    {'label': '用人部门', 'property': 'dep_name'},
                    {'label': '招聘HR', 'property': 'hr_participants'},
                    {'label': '启动日期', 'property': 'start_dt'},
                    {'label': '截止日期', 'property': 'deadline'},
                    {'label': '紧急程度', 'property': 'emergency_level'},
                    {'label': '计划招聘', 'property': 'position_total'},
                    {'label': '已入职', 'property': 'employed_count'},
                    {'label': '待招聘', 'property': 'to_be_recruit'},
                    {'label': '达成率', 'property': 'progress_rate'},
                    {'label': '初筛通过', 'property': 'preliminary_screen_passed'}
                ]
            )
            max_interview_count = data.get("max_interview_count") or 0
            interview_header = []
            for i in range(1, max_interview_count + 1):
                interview_header.extend([
                    {'label': '已安排面试(第{}轮)'.format(i), 'property': 'interview_arranged_{}'.format(i)},
                    {'label': '已面试(第{}轮)'.format(i), 'property': 'interviewed_{}'.format(i)},
                    {'label': '通过面试(第{}轮)'.format(i), 'property': 'interview_passed_{}'.format(i)},
                ])
                header.extend(interview_header)

            header.extend(
                [
                    {'label': '拟录用', 'property': 'proposed_employment'},
                    {'label': '已发Offer', 'property': 'offer_issued'},
                    {'label': '待入职', 'property': 'to_be_employed'},
                ]
            )
        elif scene_type == RecruitProgressType.department:
            header.extend(
                [
                    {'label': '用人部门', 'property': 'name'},
                    {'label': '计划招聘', 'property': 'position_total'},
                    {'label': '已入职', 'property': 'employed_count'},
                    {'label': '待招聘', 'property': 'to_be_recruit'},
                    {'label': '达成率', 'property': 'progress_rate'},
                ]
            )
        else:
            header.extend(
                [
                    {'label': '岗位类别', 'property': 'name'},
                    {'label': '计划招聘', 'property': 'position_total'},
                    {'label': '已入职', 'property': 'employed_count'},
                    {'label': '待招聘', 'property': 'to_be_recruit'},
                    {'label': '达成率', 'property': 'progress_rate'},
                ]
            )
        ret["header"] = header
        return ret

    async def post(self, request):
        form = PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)
        validated_data = form.data
        scene_type = validated_data.get("scene_type")
        business = RecruitProgressBusiness(
            request.ctx.company_id, request.ctx.user_id
        )
        if scene_type == RecruitProgressType.position:
            data = await business.position_progress_sheet(validated_data)
        elif scene_type == RecruitProgressType.department:
            data = await business.department_progress(validated_data)
        elif scene_type == RecruitProgressType.title_cate:
            data = await business.title_group_progress(validated_data)
        else:
            return self.error("参数错误")
        data = self._handle_sheet_response_data(data, scene_type)

        return self.data(data)


class RecruitProgressExportView(HRBaseView):
    """
    招聘进度excel导出
    """

    async def post(self, request):
        form = PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        validated_params = form.data
        business = RecruitProgressBusiness(
            company_id=request.ctx.company_id, user_id=request.ctx.user_id
        )
        # 1. 职位 2.部门 3. 岗位类别
        position_task = business.position_progress_sheet(validated_params)
        dep_task = business.department_progress(validated_params)
        title_group_task = business.title_group_progress(validated_params)

        position_data, dep_data, title_group_data = await asyncio.gather(
            position_task, dep_task, title_group_task
        )

        position_sheet = RecruitProgressSheetView._handle_sheet_response_data(position_data, 1)
        position_sheet["sheet_name"] = "职位招聘进度"

        dep_sheet = RecruitProgressSheetView._handle_sheet_response_data(dep_data, 2)
        dep_sheet["sheet_name"] = "部门招聘进度"

        title_group_sheet = RecruitProgressSheetView._handle_sheet_response_data(title_group_data, 3)
        title_group_sheet["sheet_name"] = "岗位类别招聘进度"

        export_data = [dep_sheet, title_group_sheet, position_sheet]
        exporter = ManySheetListExport(export_data=export_data)
        return self.data({
            "url": await exporter.get_url(file_name="招聘进度统计表.xlsx")
        })
