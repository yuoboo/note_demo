from business.candidate_record.b_candidate_record_search import CandidateRecordSearchBusiness
from constants import ParticipantType
from utils.api_auth import EmployeeBaseView
from utils.api_util import format_request_args
from utils import performance


class SearchQueryConfigView(EmployeeBaseView):
    async def get(self, request):
        """
        获取招聘中列表统计信息
        """
        params = format_request_args(request.args)
        data = await CandidateRecordSearchBusiness.process_query_config(
            request.ctx.user.company_id, request.ctx.user.emp_id, params,
            user_type=ParticipantType.EMPLOYEE
        )
        return self.data(data)


class SearchQueryView(EmployeeBaseView):
    async def get(self, request):
        """
        获取列表数据
        @param request:
        @return:
        """
        params = format_request_args(request.args)
        data = await CandidateRecordSearchBusiness.search(
            request.ctx.user.company_id, request.ctx.user.emp_id, params,
            user_type=ParticipantType.EMPLOYEE
        )
        return self.data(data)
