# coding=utf-8
import datetime

from constants import SalaryUnit


def get_age_range(age_min, age_max, job_position=False):
    if all([age_min, age_max]):
        if age_min == -1 and age_max == -1:
            res = "不限" if job_position else "年龄不限"
        else:
            if age_min == age_max:
                res = str(age_min)
            else:
                res = str(age_min) + "-" + str(age_max)
            tail = ''
            if not job_position:
                tail = '岁'
            res = f'{res}{tail}'
    elif age_min:
        res = str(age_min) + "以上"
    elif age_max:
        res = str(age_max) + "以下"
    else:
        res = ""

    return res


def calculate_now_year(dt):
    """
    计算时间与当前时间相差年
    """
    try:
        today = datetime.datetime.today()
        if 'T' in dt:
            dt = dt.split('T')[0]
        start_date = datetime.datetime.strptime(dt, "%Y-%m-%d")
        if start_date < datetime.datetime(100, 1, 1):
            return None
        return today.year - start_date.year - ((today.month, today.day) < (start_date.month, start_date.day))
    except:
        return None
