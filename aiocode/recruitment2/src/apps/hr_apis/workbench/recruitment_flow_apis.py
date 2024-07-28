from utils.api_auth import HRBaseView
from business.b_work_bench import WorkBenchFlowBusiness


class RecruitmentTrendsView(HRBaseView):
    """
    招聘总览
    """

    async def get(self, request):
        """
        返回招聘工作台 计划招聘
        """
        company_id = request.ctx.company_id
        user_id = request.ctx.user_id

        ret = await WorkBenchFlowBusiness.get_recruitment_trends(
            company_id=company_id, user_id=user_id
        )
        return self.data(ret)


class RecruitmentFlowView(HRBaseView):
    """
    招聘流程统计
    """

    async def get(self, request):
        """
        返回招聘流程各阶段应聘记录统计数据
        """
        company_id = request.ctx.company_id
        user_id = request.ctx.user_id

        ret = await WorkBenchFlowBusiness.get_recruitment_flow_count(
            company_id=company_id, user_id=user_id
        )
        return self.data(ret)
