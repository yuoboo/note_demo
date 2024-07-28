from services.s_https.s_ucenter import get_company_for_id
from utils.client import HttpClient
from utils.time_cal import time_stamp
from utils.logger import http_logger
from utils.json_util import json_dumps
from configs import config

app_env = config.get("APP_ENV")


class BIService(object):

    @classmethod
    async def send_data_to_bi(cls, params: dict, fill_time: bool = True):
        """
        上报数据到BI大数据
        :param params: 发送数据
        :param fill_time:
        :return:
        """
        http_logger.info("send_to_bi: params-{}".format(params))
        _url = {
            "local": "http://bdcenter-test.2haohr.com/kafka_tool/entrance",
            "dev": "",
            "test": "http://bdcenter-test.2haohr.com/kafka_tool/entrance",
            "production": "http://bdcenter.2haohr.com/kafka_tool/entrance",
        }
        if fill_time:
            params["push_time"] = time_stamp()

        http_url = _url.get(app_env)
        if not http_url:
            # bi 没有dev环境
            http_logger.info("send_to_bi [dev]: params-{}".format(params))
            return

        res = await HttpClient.post(http_url, data=json_dumps(params), headers={"Content-Type": "application/json"})
        if res and res['resultcode'] == 200:
            return res["data"]
        else:
            http_logger.info("BI指标数据传送接口失败: 原因-{}".format(res.json().get("message", "")))
