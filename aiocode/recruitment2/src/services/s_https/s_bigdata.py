# coding: utf-8
import calendar
import datetime
from configs import config
from utils.client import HttpClient
from utils.strutils import uuid2str


class BigDataDate(object):
    start_day = None
    end_day = None

    def __init__(self, start_dt, end_dt):
        self.start_day = start_dt.strftime("%Y%m%d")
        self.end_day = end_dt.strftime("%Y%m%d")


class BigDataDateFormat(object):
    @classmethod
    def get_yesterday(cls):
        """
        获取大数据时间 - 昨天
        :return:
        """
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        return BigDataDate(yesterday, yesterday)

    @classmethod
    def get_current_month(cls):
        """
        获取大数据时间 - 本月
        :return:
        """
        now = datetime.datetime.now()
        month_start = datetime.datetime(now.year, now.month, 1)
        month_end = datetime.datetime(now.year, now.month, calendar.monthrange(now.year, now.month)[1])
        return BigDataDate(month_start, month_end)


class BigDataService(object):
    @classmethod
    def get_url(cls):
        return '%s%s' % (config.BIGDATA_URL, 'bd/query_engine/recruitment/puv')

    @classmethod
    def get_pv(cls, data):
        count = 0
        if data and len(data) > 0:
            for d in data:
                count += d.get('pv', 0)
        return count

    @classmethod
    async def get_portals_pv_current_month(cls, company_share_id: str) -> int:
        """
        获取招聘门户本月pv
        :param company_share_id: 企业分享id
        :return: pv
        """
        data = {
            'compId': uuid2str(company_share_id),
            'timeType': 3,
            'type': 1
        }
        res = await HttpClient.get(cls.get_url(), params=data)
        if not res or res["resultcode"] != 200:
            ret = []
        else:
            ret = res.get('data', [])
        return cls.get_pv(ret)

    @classmethod
    async def get_portals_pv_yesterday(cls, company_share_id: str) -> int:
        """
        获取招聘门户昨天pv
        :param company_share_id: 企业分享id
        :return: pv
        """
        data = {
            'compId': uuid2str(company_share_id),
            'timeType': 1,
            'type': 1
        }
        res = await HttpClient.get(cls.get_url(), params=data)
        if not res or res["resultcode"] != 200:
            ret = []
        else:
            ret = res.get('data', [])
        return cls.get_pv(ret)

    @classmethod
    async def get_portals_page_pv_current_month(cls, company_share_id: str) -> int:
        """
        获取招聘门户本月pv
        :param company_share_id: 企业分享id
        :return: pv
        """
        data = {
            'compId': uuid2str(company_share_id),
            'timeType': 3,
            'type': 2
        }
        res = await HttpClient.get(cls.get_url(), params=data)
        if not res or res["resultcode"] != 200:
            ret = []
        else:
            ret = res.get('data', [])
        return ret

    @classmethod
    async def get_portals_page_pv_yesterday(cls, company_share_id: str) -> int:
        """
        获取招聘门户昨天pv
        :param company_share_id: 企业分享id
        :return: pv
        """
        data = {
            'compId': uuid2str(company_share_id),
            'timeType': 1,
            'type': 2
        }
        res = await HttpClient.get(cls.get_url(), params=data)
        if not res or res["resultcode"] != 200:
            ret = []
        else:
            ret = res.get('data', [])
        return ret

    @classmethod
    async def get_portals_employee_pv_current_month(cls, company_share_id: str, employee_id: str) -> int:
        """
        获取员工招聘门户本月pv
        :param company_share_id: 企业分享id
        :return: pv
        """
        data = {
            'compId': uuid2str(company_share_id),
            'timeType': 3,
            'type': 6,
            'empId': uuid2str(employee_id)
        }
        res = await HttpClient.get(cls.get_url(), params=data)
        if not res or res["resultcode"] != 200:
            ret = []
        else:
            ret = res.get('data', [])
        return cls.get_pv(ret)

    @classmethod
    async def get_portals_employee_pv_yesterday(cls, company_share_id: str, employee_id: str) -> int:
        """
        获取员工招聘门户昨天pv
        :param company_share_id: 企业分享id
        :return: pv
        """
        data = {
            'compId': uuid2str(company_share_id),
            'timeType': 1,
            'type': 6,
            'empId': uuid2str(employee_id)
        }
        res = await HttpClient.get(cls.get_url(), params=data)
        if not res or res["resultcode"] != 200:
            ret = []
        else:
            ret = res.get('data', [])
        return cls.get_pv(ret)

    @classmethod
    async def get_portals_pv(
            cls, company_share_id: str, dt: BigDataDate) -> int:
        """
        获取招聘门户pv
        :param company_share_id:
        :param dt: 大数据日期格式
        """
        data = {
            'share_id': uuid2str(company_share_id),
            'start_day': dt.start_day,
            'end_day': dt.end_day
        }
        http_url = '%s%s' % (config.BIGDATA_URL, 'training/recruitment/share_pv')

        res = await HttpClient.post(http_url, json_body=data)
        if not res or res["resultcode"] != 200:
            ret = {}
        else:
            ret = res.get('data', {})

        count = ret.get('data', 0)
        return count

    @classmethod
    async def get_portals_employee_pv(
            cls, company_share_id: str, employee_id: str, dt: BigDataDate) -> int:
        """
        获取招聘门户+员工id的pv
        :param company_share_id:
        :param employee_id: 员工id
        :param dt: 大数据日期格式
        """
        data = {
            'share_id': uuid2str(company_share_id),
            'business_id': uuid2str(employee_id),
            'start_day': dt.start_day,
            'end_day': dt.end_day
        }
        http_url = '%s%s' % (config.BIGDATA_URL, 'training/recruitment/business_pv')

        res = await HttpClient.post(http_url, json_body=data)
        if not res or res["resultcode"] != 200:
            ret = {}
        else:
            ret = res.get('data', {})

        count = ret.get('data', 0)
        return count

    @classmethod
    async def get_portals_page_pv(
            cls, company_share_id: str, recruit_page_ids: list, dt: BigDataDate) -> list:
        """
        获取招聘门户+招聘门户id列表的pv
        :param company_share_id:
        :param recruit_page_ids: 招聘门户id列表
        :param dt: 大数据日期格式
        """
        if not recruit_page_ids:
            return []

        data = {
            'share_id': uuid2str(company_share_id),
            'recruit_page_id': recruit_page_ids,
            'start_day': dt.start_day,
            'end_day': dt.end_day
        }
        http_url = '%s%s' % (config.BIGDATA_URL, 'training/recruitment/recruit_page_pv')

        res = await HttpClient.post(http_url, json_body=data)
        if not res or res["resultcode"] != 200:
            ret = []
        else:
            ret = res.get('data', {}).get('data', [])

        return ret
