from utils.api_auth import HRBaseView
from business.b_work_bench import WorkBenchBusiness


class LastJobPositionView(HRBaseView):

    """
    最近职位统计
    """
    async def get(self, request):
        company_id = request.ctx.company_id
        user_id = request.ctx.user_id
        ret = await WorkBenchBusiness.get_last_position(company_id=company_id, user_id=user_id)
        return self.data(ret)


class PositionTodayAdd(HRBaseView):
    """
    招聘职位今日新增
    """

    async def get(self, request):
        company_id = request.ctx.company_id
        user_id = request.ctx.user_id
        ret = await WorkBenchBusiness.get_position_today_add(company_id=company_id, user_id=user_id)
        return self.data(ret)
