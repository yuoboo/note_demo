# coding: utf-8

from business import biz
from kits.exception import APIValidationError
from utils.api_auth import BaseView


class DeleteDeliveryRecordView(BaseView):

    async def post(self, request):
        """
        删除投递记录
        @param request:
        @return:
        """
        company_id = request.json.get("company_id")
        user_id = request.json.get("user_id")
        candidate_record_ids = request.json.get("candidate_record_ids")

        if not all([company_id, user_id, candidate_record_ids]):
            raise APIValidationError(msg="参数缺失")
        await biz.portal_delivery.delete_delivery_record(
            company_id, user_id, candidate_record_ids
        )

        return self.data({})
