from business.b_wework import WeWorkBusiness
from utils.api_auth import BaseView
from utils.api_util import format_request_args


class ExternalContactView(BaseView):
    async def get(self, request):
        """
        获取招聘中列表统计信息
        """
        params = format_request_args(request.args)
        data = await WeWorkBusiness.get_by_external_id_first(
            params.get('company_id', None), params.get('external_id', None)
        )
        return self.data(data)
