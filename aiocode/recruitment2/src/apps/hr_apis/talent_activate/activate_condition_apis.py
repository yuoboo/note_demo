from business import biz
from utils.api_auth import HRBaseView


class VerifyCandidatesView(HRBaseView):

    async def post(self, request):
        """
        yapi地址：http://yapi.2haohr.com:4000/project/819/interface/api/117211
        批量校验候选人是否满足激活
        @param request:
        @return:
        """
        candidate_ids = request.json.get("candidate_ids")
        if not candidate_ids or not isinstance(candidate_ids, list):
            return self.error("参数错误")
        data = await biz.activate_condition.batch_verify_candidates(
            request.ctx.company_id, candidate_ids
        )

        return self.data(data)


class VerifyCandidateView(HRBaseView):

    async def post(self, request):
        """
        yapi地址：http://yapi.2haohr.com:4000/project/819/interface/api/117218
        单个校验候选人是否满足激活
        @param request:
        @return:
        """
        candidate_id = request.json.get("candidate_id")
        if not candidate_id:
            return self.error("参数错误")
        data = await biz.activate_condition.verify_candidate(
            request.ctx.company_id, candidate_id
        )

        return self.data(data)
