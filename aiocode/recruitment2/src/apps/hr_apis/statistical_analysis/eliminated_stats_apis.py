# coding: utf-8
from wtforms import DateField, IntegerField, validators

from apps.hr_apis.statistical_analysis import StatsBaseForm
from business.b_statistical_analysis import EliminatedReasonStatsBusiness
from constants import CandidateRecordStatus
from utils.api_auth import HRBaseView
from utils.excel_util import ManySheetListExport


class PostForm(StatsBaseForm):
    start_dt = DateField(validators=[validators.Required()], label="开始时间")
    end_dt = DateField(validators=[validators.Required()], label="截止时间")
    eliminated_status = IntegerField(validators=[validators.Required()], label="淘汰状态")


class EliminatedReasonStatsView(HRBaseView):

    @staticmethod
    def _handle_chart_response_data(data, eliminated_status):
        res = {
            "xAxis": [],
            "legend": ['人数', '累计占比'],
            "series": []
        }
        if eliminated_status == CandidateRecordStatus.PRIMARY_STEP3:
            data_list = data.get("primary_eliminated_data")
        elif eliminated_status == CandidateRecordStatus.INTERVIEW_STEP4:
            data_list = data.get("interview_eliminated_data")
        else:
            data_list = data.get("employed_eliminated_data")
        x_axis, l_data, r_data = [], [], []
        for item in data_list:
            x_axis.append(item.get("reason_name"))
            l_data.append(item.get("count"))
            r_data.append(item.get("sum_percent_num"))
        series = [
            {"name": "人数", "type": "bar", "data": l_data},
            {"name": "累计占比", "type": "line", "data": r_data}
        ]
        res.update(
            {
                "xAxis": x_axis,
                "series": series
            }
        )
        return res

    async def post(self, request):
        """
        淘汰原因chart报表
        @param request:
        @return:
        """
        form = PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        business = EliminatedReasonStatsBusiness(
            request.ctx.company_id, request.ctx.user_id
        )
        eliminated_status = form.data.get("eliminated_status")
        data = await business.eliminated_reason_stats_data(form.data)
        data = self._handle_chart_response_data(
            data, eliminated_status
        )

        return self.data(data)


class EliminatedReasonStatsSheetView(HRBaseView):

    @staticmethod
    def _handle_sheet_response_data(data, eliminated_status):
        header = [
            {'property': 'reason_name', 'label': '淘汰原因'},
            {'property': 'count', 'label': '人数'},
            {'property': 'percent', 'label': '占比'},
            {'property': 'sum_percent_str', 'label': '累计占比'}
        ]
        if eliminated_status == CandidateRecordStatus.PRIMARY_STEP3:
            body = data.get("primary_eliminated_data")
        elif eliminated_status == CandidateRecordStatus.INTERVIEW_STEP4:
            body = data.get("interview_eliminated_data")
        else:
            body = data.get("employed_eliminated_data")

        return {"header": header, "body": body}

    async def post(self, request):
        """
        淘汰原因sheet报表
        @param request:
        @return:
        """
        form = PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        business = EliminatedReasonStatsBusiness(
            request.ctx.company_id, request.ctx.user_id
        )
        eliminated_status = form.data.get("eliminated_status")
        data = await business.eliminated_reason_stats_data(form.data)
        data = self._handle_sheet_response_data(data, eliminated_status)
        return self.data(data)


class EliminatedReasonStatsExportView(HRBaseView):
    class PostForm(StatsBaseForm):
        start_dt = DateField(validators=[validators.Required()], label="开始时间")
        end_dt = DateField(validators=[validators.Required()], label="截止时间")

    async def post(self, request):
        form = self.PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        business = EliminatedReasonStatsBusiness(
            company_id=request.ctx.company_id, user_id=request.ctx.user_id
        )
        # 初筛淘汰, 面试淘汰， 放弃录用
        validated_data = form.data
        validated_data["eliminated_status"] = None
        sheet_data = await business.eliminated_reason_stats_data(validated_data)

        primary_sheet = EliminatedReasonStatsSheetView._handle_sheet_response_data(
            sheet_data, CandidateRecordStatus.PRIMARY_STEP3
        )
        primary_sheet["sheet_name"] = "初筛淘汰原因"

        interview_sheet = EliminatedReasonStatsSheetView._handle_sheet_response_data(
            sheet_data, CandidateRecordStatus.INTERVIEW_STEP4
        )
        interview_sheet["sheet_name"] = "面试淘汰原因"
        employ_sheet = EliminatedReasonStatsSheetView._handle_sheet_response_data(
            sheet_data, CandidateRecordStatus.EMPLOY_STEP5
        )
        employ_sheet["sheet_name"] = "录用淘汰原因"

        exporter = ManySheetListExport(export_data=[primary_sheet, interview_sheet, employ_sheet])

        return self.data({
            "url": await exporter.get_url(file_name="淘汰原因统计表.xlsx")
        })
