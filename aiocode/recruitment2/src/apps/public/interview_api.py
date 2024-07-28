
from utils.api_auth import BaseView


class WechatUserMobileVerificationApi(BaseView):
    """
    验证码相关
    """
    async def post(self, request):
        """
        生成验证码
        """
        pass

    async def put(self, request):
        """
        校验 验证码
        """
        pass


class WeChatSignConfigApi(BaseView):
    """
    微信面试签到码
    """

    async def get(self, request):
        pass
