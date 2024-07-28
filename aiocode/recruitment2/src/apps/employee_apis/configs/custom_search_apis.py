# coding: utf-8
from business.configs.b_custom_search import CustomSearchBusiness
from constants import CustomSearchSceneType, ParticipantType
from utils.api_auth import EmployeeBaseView


class CustomSearchView(EmployeeBaseView):
    async def get(self, request):
        """
        获取自定义筛选条件设置接口
        """
        scene_type = request.args.get('scene_type', CustomSearchSceneType.PROCESS)

        data = await CustomSearchBusiness.get(
            request.ctx.user.company_id,
            scene_type,
            ParticipantType.EMPLOYEE,
            request.ctx.user.emp_id
        )
        return self.data(data)

    async def post(self, request):
        """
        创建或修改自定义筛选条件设置接口
        """
        scene_type = request.json.get('scene_type', CustomSearchSceneType.PROCESS)
        config = request.json.get('config', [])

        await CustomSearchBusiness.create_or_update(
            request.ctx.user.company_id,
            scene_type,
            ParticipantType.EMPLOYEE,
            request.ctx.user.emp_id,
            config
        )
        return self.data(True)
