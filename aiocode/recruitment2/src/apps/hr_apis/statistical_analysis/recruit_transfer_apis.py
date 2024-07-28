# coding: utf-8
from wtforms import DateField, BooleanField
from wtforms import validators

from apps.hr_apis.statistical_analysis import StatsBaseForm
from business.b_statistical_analysis import RecruitTransferBusiness, STATUS_KEY_MAP
from constants import CandidateRecordStatus
from utils.api_auth import HRBaseView
from utils.excel_util import ManySheetListExport


class PostForm(StatsBaseForm):
    start_dt = DateField(validators=[validators.Required()], label="开始时间")
    end_dt = DateField(validators=[validators.Required()], label="截止时间")
    filter_forbidden = BooleanField(default=False, label="是否过滤已禁用渠道")


class CandidateTransferView(HRBaseView):

    async def post(self, request):
        """
        招聘转化率chart报表
        @param request:
        @return:
        """
        form = PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        business = RecruitTransferBusiness(
            request.ctx.company_id, request.ctx.user_id
        )
        data = await business.candidate_transfer_chart(form.data)

        return self.data(data)


class CandidateTransferSheetView(HRBaseView):

    @staticmethod
    def _handle_sheet_response_data(data):
        max_interview_count = data["max_interview_count"]
        header = [
            {'property': 'name', 'label': '招聘职位'},
            {'property': 'dep_name', 'label': '用人部门'},
            {'property': 'new_add', 'label': '新增候选人'}
        ]
        stats_status_list = RecruitTransferBusiness.get_all_transfer_status(max_interview_count)
        previous_key = ""
        previous_key_name = ""
        for status in stats_status_list:
            if isinstance(status, int):
                status_key = STATUS_KEY_MAP[status]
                key_name = CandidateRecordStatus.attrs_[status]
            else:
                status_key = f'{STATUS_KEY_MAP[status[1]]}_{status[0]}'
                key_name = f'{CandidateRecordStatus.attrs_[status[1]]}第({status[0]})轮'
            header.append(
                {'property': status_key, 'label': key_name},
            )
            absolute_key = f'ab_{status_key}_rate'
            absolute_key_name = f'新增候选人->{key_name}'
            if isinstance(status, int) and status == CandidateRecordStatus.PRIMARY_STEP2:
                header.append(
                    {'property': absolute_key, 'label': absolute_key_name}
                )
            else:
                header.append(
                    {
                        'property': f're_{previous_key}_{status_key}_rate',
                        'label': f'{previous_key_name}->{key_name}'
                    }
                )
                header.append({'property': absolute_key, 'label': absolute_key_name})
            previous_key = status_key
            previous_key_name = key_name

        return {'header': header, 'body': data["list"]}

    async def post(self, request):
        """
        招聘转化率sheet报表
        @param request:
        @return:
        """
        form = PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        business = RecruitTransferBusiness(
            request.ctx.company_id, request.ctx.user_id
        )
        data = await business.candidate_transfer_sheet(form.data)
        data = self._handle_sheet_response_data(data)

        return self.data(data)


class CandidateTransferExportView(HRBaseView):

    async def post(self, request):
        form = PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        business = RecruitTransferBusiness(
            company_id=request.ctx.company_id, user_id=request.ctx.user_id
        )
        candidate_sheet = await business.candidate_transfer_sheet(form.data)
        candidate_sheet = CandidateTransferSheetView._handle_sheet_response_data(candidate_sheet)
        candidate_sheet["sheet_name"] = "新增候选人转化率"

        export_data = [candidate_sheet]
        exporter = ManySheetListExport(export_data=export_data)

        return self.data({
            "url": await exporter.get_url(file_name="新增候选人转化率.xlsx")
        })


class ChannelTransferStatsView(HRBaseView):

    @staticmethod
    def _handle_chart_response_data(data: list) -> dict:
        res = {
            "xAxis": ["新增候选人", "初选通过", "面试通过", "已发Offer", "已入职"]
        }
        series = []
        for channel in data:
            series.append(
                {
                    "name": channel["name"],
                    "data": [
                        channel["total"], channel["preliminary_screen_passed"], channel["interview_passed"],
                        channel["offer_issued"], channel["employed"]
                    ]
                }
            )
        res["series"] = series
        return res

    @staticmethod
    def _handle_sheet_response_data(data: list) -> dict:
        header = [
            {'property': 'name', 'label': '招聘渠道'},
            {'property': 'total', 'label': '新增候选人'},
            {'property': 'total2primary_passed_rate', 'label': '新增候选人->初选通过'},
            {'property': 'preliminary_screen_passed', 'label': '初选通过'},
            {'property': 'primary_passed2interview_passed_rate', 'label': '初选通过->面试通过'},
            {'property': 'total2interview_passed_rate', 'label': '新增候选人->面试通过'},
            {'property': 'interview_passed', 'label': '面试通过'},
            {'property': 'interview_passed2offer_issued_rate', 'label': '面试通过->已发Offer'},
            {'property': 'total2offer_issued_rate', 'label': '新增候选人->已发Offer'},
            {'property': 'offer_issued', 'label': '已发Offer'},
            {'property': 'offer_issued2employed_rate', 'label': '已发Offer->已入职'},
            {'property': 'total2employed_rate', 'label': '新增候选人->已入职'},
            {'property': 'employed', 'label': '已入职'},
        ]

        return {'header': header, 'body': data}

    async def post(self, request):
        """
        招聘渠道转化率报表
        @param request:
        @return:
        """
        form = PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        business = RecruitTransferBusiness(
            request.ctx.company_id, request.ctx.user_id
        )
        data = await business.channel_transfer_data(form.data)
        result = self._handle_chart_response_data(data["list"])
        sheet_data = self._handle_sheet_response_data(data["list"])
        result["table"] = sheet_data
        result["recruiting_total"] = data["recruiting_total"]

        return self.data(result)


class ChannelTransferExportView(HRBaseView):
    """
    招聘渠道转化导出
    """
    async def post(self, request):
        form = PostForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        business = RecruitTransferBusiness(
            request.ctx.company_id, request.ctx.user_id
        )
        data = await business.channel_transfer_data(form.data)
        sheet_data = ChannelTransferStatsView._handle_sheet_response_data(data["list"])
        sheet_data["sheet_name"] = "招聘渠道转化率"

        exporter = ManySheetListExport(export_data=[sheet_data])

        return self.data({
            "url": await exporter.get_url(file_name="招聘渠道转化率统计表.xlsx")
        })
