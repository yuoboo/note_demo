import logging

from business import biz
from utils.api_auth import BaseView

logger = logging.getLogger('app')


class EmailNotifyCallBackView(BaseView):

    async def post(self, request):
        """
        邮件通知回调
        @param request:
        @return:
        """
        logger.info(f"邮件通知发送后回调，回调参数:{request.json}")
        await biz.notify_callback.email_notify_callback(request.json)

        return self.data({})

