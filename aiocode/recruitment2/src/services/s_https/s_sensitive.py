import json
import logging

from kits.exception import ServiceError
from utils.ehr_request import EhrRequest

logger = logging.getLogger('app')


class SensitiveService(object):
    """
    敏感词服务
    """

    @classmethod
    async def validation(cls, text: str, type_: int, auto_raise: bool = False) -> bool:
        """
        根据类型验证敏感词
        :param text: 内容
        :param type_: 类型
        :param auto_raise: 类型
        """
        sensitive = await cls.get(text, type_)
        if len(sensitive) > 0:
            if auto_raise:
                raise ServiceError(msg='内容存在敏感字符')
            return True
        return False

    @classmethod
    async def get(cls, text: str, type_: int) -> list:
        """
        根据类型和内容判断是否有敏感词
        :param text:
        :param type_:
        :return:
        """
        params = {
            "text": text,
            "type": type_,
        }
        res = await EhrRequest("sensitive").intranet("hasSensitiveWordsWithType").post(data=params)
        if res and res['resultcode'] == 200:
            ret = res['data'] or []
        else:
            # raise ServiceError(msg='内容存在敏感字符')
            logger.error("敏感词服务 验证敏感词错误 text: %s; type: %s; ret: %s" % (text, type, json.dumps(res)))
            ret = []
        return ret
