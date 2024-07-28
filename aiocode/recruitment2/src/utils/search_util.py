import datetime

import ujson
from dateutil.relativedelta import relativedelta

from utils.strutils import uuid2str


class SearchParamsUtils:
    """
    搜索条件处理类
    """
    def __init__(self, params: dict):
        self.params = params

    def get_array(self, name: str, is_format_uuid: bool = False):
        """
        获取参数列表
        @param name: 搜索条件名
        @param is_format_uuid: 是否格式化uuid， 将uuid中的中杆去掉
        @return:
        """
        value = self.get_value(name)
        if value is None:
            return value

        if isinstance(value, str):
            if value == '':
                return None
            if ',' in value:
                results = value.split(',')
            else:
                results = [value]
        else:
            results = value

        if is_format_uuid:
            return [uuid2str(v) for v in results]

        return results

    def get_range(self, name):
        """
        获取参数范围
        @param name: 搜索条件名
        @return:
        """
        value = self.get_value(name)
        if not value:
            return None

        target_type = ujson.loads(value)
        gte = target_type.get('gte', None)
        if gte in ['']:
            gte = None
        lte = target_type.get('lte', None)
        if lte in ['']:
            lte = None

        if gte is None and lte is None:
            return None

        return [gte, lte]

    def get_range_date_query(self, name):
        """
        获取日期范围查询条件
        @param name:
        @return:
        """
        range = self.get_range(name)
        try:
            gte = range[0]
            lte = range[1]

            age_range = {}
            if gte:
                age_range['gte'] = gte
            if lte:
                age_range['lte'] = lte
                if 'gte' not in age_range:
                    age_range['gt'] = "1900-01-01"

            age_range['format'] = "yyyy-MM-dd"
            age_range['time_zone'] = "+08:00"
            return age_range
        except Exception as e:
            return None

    def num_date_query(self, name):
        """
        数字通过当前时间，计算出对应日期，并生成查询条件
        @param name: 范围[开始, 结束]
        @return: 查询条件
        """
        range = self.get_range(name)

        if range is None or len(range) != 2:
            return None

        try:
            now = datetime.datetime.now()
            gte = range[0]
            lte = range[1]

            age_range = {}
            if lte:
                date = now + relativedelta(years=-(int(float(lte)) + 1))
                if date <= datetime.datetime(1910, 1, 1):
                    date = datetime.datetime(1910, 1, 1)
                age_range['gt'] = datetime.datetime.strftime(date, "%Y-%m-%d")
            if gte:
                date = now + relativedelta(years=-int(float(gte)))
                if date <= datetime.datetime(1910, 1, 1):
                    date = datetime.datetime(1910, 1, 1)
                age_range['lte'] = datetime.datetime.strftime(date, "%Y-%m-%d")
                if 'gt' not in age_range:
                    age_range['gt'] = "1900-01-01"

            age_range['format'] = "yyyy-MM-dd"
            age_range['time_zone'] = "+08:00"
            return age_range
        except:
            return None

    def get_value(self, name, default=None):
        value = self.params.get(name, default)
        if value == '':
            value = None
        return value

    def get_int(self, name, default=None):
        value = self.get_value(name, default)
        try:
            return int(value)
        except:
            return default
