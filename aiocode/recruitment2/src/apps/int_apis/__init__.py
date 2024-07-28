# coding: utf-8
from business.b_events import SubscriptionEventBusiness
from celery_worker import celery_app
from utils.api_auth import BaseView


class EventCallBackView(BaseView):
    """
    事件分发平台统一回调接口
    参考文档：https://dianmi.feishu.cn/docs/doccnb1RTKUJVXiu4FuglBBiwxd#
    """

    async def post(self, request):
        data = request.json
        # await SubscriptionEventBusiness.handle_events(
        #     data.get("from"), data.get("ev_type"),
        #     data.get("event_id"), data.get("data")
        # )
        celery_app.send_task("apps.tasks.common.subscription_event_task", args=(data,))

        return self.data({})
