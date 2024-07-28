# coding: utf-8
import datetime
import re
import time

# 时分秒 格式化字符串
time_re = re.compile(
    r'(?P<hour>\d{1,2}):(?P<minute>\d{1,2})'
    r'(?::(?P<second>\d{1,2})(?:\.(?P<microsecond>\d{1,6})\d{0,6})?)?'
)

# 时间 格式化字符串
datetime_re = re.compile(
    r'(?P<year>\d{4})[-/](?P<month>\d{1,2})[-/](?P<day>\d{1,2})'
    r'([T ](?P<hour>\d{1,2}):(?P<minute>\d{1,2})'
    r'(?::(?P<second>\d{1,2})(?:\.(?P<microsecond>\d{1,6})\d{0,6})?)?'
    r'(?P<tzinfo>Z|[+-]\d{2}(?::?\d{2})?)?'
    r')?$'
)

DEFAULT_FORMAT = '%Y-%m-%d %H:%M:%S'  # 默认时间格式
DEFAULT_DATE_FORMAT = '%Y-%m-%d'  # 默认日期格式
DEFAULT_MONTH_FORMAT = '%Y-%m'  # 默认月份格式

DT_CONFIG = {
    'format_str': DEFAULT_FORMAT,  # {string} 时间格式化的格式字符串

    # format_list: {list<string>} 各种支持的时间格式
    'format_list': (DEFAULT_FORMAT, '%Y-%m-%d %H:%M:%S.%f', DEFAULT_DATE_FORMAT,
                    '%Y年%m月%d日 %H时%M分%S秒', '%Y年%m月%d日　%H时%M分%S秒', '%Y年%m月%d日 %H时%M分', '%Y年%m月%d日　%H时%M分',
                    '%Y年%m月%d日 %H:%M:%S', '%Y年%m月%d日　%H:%M:%S', '%Y年%m月%d日 %H:%M', '%Y年%m月%d日　%H:%M', '%Y年%m月%d日',
                    '%Y/%m/%d %H:%M:%S', '%Y/%m/%d %H:%M:%S.%f', '%Y/%m/%d', '%Y%m%d', '%Y%m%d%H%M%S',
                    '%Y/%m/%d %H:%M', '%Y-%m-%d %H:%M', "%Y-%m-%dT%H:%M",
                    '%Y-%m-%d %p %I:%M:%S', '%Y-%m-%d %p %I:%M', '%Y/%m/%d %p %I:%M:%S', '%Y/%m/%d %p %I:%M',
                    "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%S+08:00", "%Y-%m-%dT%H:%M:%S.%f+08:00",
                    ),
}


def get_today_start_and_end_datetime() -> list:
    """
    获取今天的开始与结束时间
    @return: list[开始时间, 结束时间]
    """
    today = datetime.datetime.today()
    return [get_date_min_datetime(today), get_date_max_datetime(today)]


def get_date_min_datetime(date):
    """
    获取指定日期的最小时间
    :param date:
    :return:
    """
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
    min_time = datetime.datetime.combine(date, datetime.time.min)

    return min_time


def get_date_max_datetime(date):
    """
    获取指定日期的最大时间
    :param date:
    :return:
    """
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
    max_time = datetime.datetime.combine(date, datetime.time.max)

    return max_time


def str_2_json_datetime(value):
    """
    字符串时间转json时间
    @param value:
    @return:
    """
    if not value:
        return value
    if 'T' in value:
        return value
    if ' ' in value:
        return value.replace(' ', 'T')
    return value


def time_stamp(length=13):
    """
    获取当前时间戳
    :param length: 长度 默认为10 标识秒级(s)， 其他则为毫秒级(ms)
    :return: 时间戳
    """
    if length == 10:
        return int(time.time())
    return int(round(time.time() * 1000))


def _timedelta_2_datetime(value):
    """
    datetime.timedelta类型转成时间
    :param {datetime.timedelta} value: 原时间
    :return {datetime.datetime}: 对应的时间
    """
    # datetime.timedelta 类型，则从初始时间相加减得出结果
    return datetime.datetime.fromtimestamp(0) + value


def _number_2_datetime(value):
    """
    纯数值类型转成时间
    :param {int|long|float} value: 原时间
    :return {datetime.datetime}: 对应的时间
    """
    return datetime.datetime.fromtimestamp(value)


def _str_2_datetime(value, format_str=None):
    """
    字符串转成时间
    :param {string} value: 原时间
    :param {string} format_str: 原时间对应的格式字符串(默认为: %Y-%m-%d %H:%M:%S)
    :return {datetime.datetime}: 对应的时间
    """
    # 指定格式
    if format_str:
        return datetime.datetime.strptime(value, format_str)

    # 通用匹配格式
    match = datetime_re.match(value)
    if match:
        kw = match.groupdict()
        if kw['microsecond']:
            kw['microsecond'] = kw['microsecond'].ljust(6, '0')
        kw.pop('tzinfo') # utc 暂时不支持这定义
        kw = {k: int(v) for k, v in kw.items() if v is not None}
        return datetime.datetime(**kw)

    # 含中文，或者特殊格式，只能尽量尝试匹配
    global DT_CONFIG
    # 上下午处理
    if '上午' in value: value = value.replace('上午', 'AM')
    if u'上午' in value: value = value.replace(u'上午', 'AM')
    if '下午' in value: value = value.replace('下午', 'PM')
    if u'下午' in value: value = value.replace(u'下午', 'PM')
    for format in DT_CONFIG.get('format_list'):
        try:
            return datetime.datetime.strptime(value, format)
        except:
            pass

    # 无法格式化
    raise ValueError("time data %r does not match time format" % value)


def to_date(value=None, format_str=None):
    """
    将时间转成 datetime.date 类型
    :param {time|datetime.datetime|datetime.date|int|long|float|string} value: 原时间(为空则默认为当前时间；纯数值则认为是时间戳,单位:秒)
    :param {string} format_str: 当原时间是字符串类型时，原时间对应的格式字符串(默认为: %Y-%m-%d %H:%M:%S)
    :return {datetime.date}: 对应的日期
    """
    if value in (None, ''):
        return datetime.date.today()
    # datetime
    elif isinstance(value, datetime.datetime):
        #return datetime.date(value.year, value.month, value.day)
        return value.date()
    # datetime.date类型，需要注意: isinstance(datetime.datetime(), datetime.date) 是返回 True 的
    elif isinstance(value, datetime.date):
        return value
    # time
    elif isinstance(value, time.struct_time):
        return datetime.date(*value[:3]) # 只能精确到秒,无法精确到毫秒级别
    # 字符串 类型,先类型转换
    elif isinstance(value, str):
        value = _str_2_datetime(value, format_str=format_str)
        return value.date()
    # 纯数值类型,认为是时间戳
    elif isinstance(value, (int, float)):
        return datetime.date.fromtimestamp(value)
    # datetime.timedelta 类型,先类型转换
    elif isinstance(value, datetime.timedelta):
        value = _timedelta_2_datetime(value)
        return value.date()
    # 其它类型,无法格式化
    return None


def to_datetime(value=None, format_str=None):
    """
    将时间转成 datetime.datetime 类型
        注: 由 time 转 datetime 类型时,只能精确到秒,无法精确到毫秒级别
    :param {time|datetime.datetime|datetime.date|int|long|float|string} value: 原时间(为空则默认为当前时间；纯数值则认为是时间戳,单位:秒)
    :param {string} format_str: 当原时间是字符串类型时，原时间对应的格式字符串(默认为: %Y-%m-%d %H:%M:%S)
    :return {datetime.datetime}: 对应的时间
    """
    if value in (None, ''):
        return datetime.datetime.now()
    # datetime
    elif isinstance(value, datetime.datetime):
        return value
    # datetime.date (与 datetime.datetime 类型不同,它不能添加时分秒)
    elif isinstance(value, datetime.date):
        return datetime.datetime(value.year, value.month, value.day)
        #return datetime.datetime.combine(value, datetime.datetime.min.time())
    # time
    elif isinstance(value, time.struct_time):
        return datetime.datetime(*value[:6]) # 只能精确到秒,无法精确到毫秒级别
        #value = time.mktime(value) # 先转成时间戳,交给下面专门处理时间戳的(实际上也是无法精确到毫秒)
    # 字符串
    elif isinstance(value, str):
        return _str_2_datetime(value, format_str=format_str)
    # 纯数值类型,认为是时间戳(要注意此处的时间不能早于1970-01-01 00:00)
    elif isinstance(value, (int, float)):
        return _number_2_datetime(value)
    # datetime.timedelta 类型,先类型转换
    elif isinstance(value, datetime.timedelta):
        return _timedelta_2_datetime(value)
    # 其它类型,无法格式化
    return None


if __name__ == "__main__":
    print(get_date_min_datetime("2020-10-16"))
    print(get_date_max_datetime("2019-11-11"))

    date_ = to_date('2020-10-20')
    datetime_ = to_datetime('2020/10/12')
    print(date_, datetime_)
