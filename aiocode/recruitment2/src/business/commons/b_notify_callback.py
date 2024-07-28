from constants import NoticeCallBackType
from services import svc


class NotifyCallBackBusiness(object):

    @classmethod
    async def email_notify_callback(cls, callback_data: dict):
        """
        邮件通知回调
        @param callback_data:
        @return:
        """
        added_data = callback_data.pop('added_data', {})
        if added_data:
            biz_type = added_data.get("biz_type")
            biz_id = added_data.get("biz_id")
            if biz_type == NoticeCallBackType.talent_active:
                await svc.activate_record.fill_notify_result(biz_id, callback_data, 2)
