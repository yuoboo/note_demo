from services.s_https.s_common import get_sms_platfor_company_sms_balance


class SmsPlatformBusiness(object):
    @classmethod
    async def get_balance(cls, company_id: str) -> int:
        """
        获取企业短信余额接口
        @param company_id: 企业id
        @return:
        """
        balance = await get_sms_platfor_company_sms_balance(company_id=company_id)
        return balance
