from sanic.request import RequestParameters

from business.candidate_record.b_candidate_record_search import CandidateRecordSearchBusiness
from utils.api_auth import HRBaseView
from utils.api_util import format_request_args


class SearchQueryConfigView(HRBaseView):
    async def get(self, request):
        """
        获取招聘中列表统计信息
        """
        params = format_request_args(request.args)
        data = await CandidateRecordSearchBusiness.process_query_config(
            request.ctx.company_id, request.ctx.user_id, params
        )
        return self.data(data)


class SearchQueryView(HRBaseView):
    async def get(self, request):
        """
        获取列表数据
        @param request:
        @return:
        """
        params = format_request_args(request.args)
        data = await CandidateRecordSearchBusiness.search(
            request.ctx.company_id, request.ctx.user_id, params
        )
        return self.data(data)
