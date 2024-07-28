# coding: utf-8
from constants import SalaryUnit


def get_salary_range(salary_min, salary_max, unit_type):
    """
    获取工资范围
    @param salary_min:
    @param salary_max:
    @param unit_type:
    @return:
    """
    unit_str = SalaryUnit.attrs_[unit_type]
    base_salary = 10000

    def deal_num(origin_num, base_num):
        res = str(round(float(origin_num) / base_num, 2))
        if ".0" in res:
            index = res.rindex(".")
            res = res[:index]

        return res

    if salary_min == -1 and salary_max == -1:
        salary_str = "薪资面议"
    else:
        if salary_min and not salary_max:
            if salary_min >= base_salary:
                salary_str = "{}万{}".format(deal_num(salary_min, base_salary), unit_str)
            else:
                salary_str = str(salary_min) + unit_str
        elif not salary_min and salary_max:
            if salary_max >= base_salary:
                salary_str = "{}万{}".format(deal_num(salary_max, base_salary), unit_str)
            else:
                salary_str = str(salary_max) + unit_str
        elif not salary_min and not salary_max:
            salary_str = ""
        else:
            if salary_min < base_salary and salary_max >= base_salary:  # pylint: disable=protected-access
                salary_str = "{}千-{}万{}".format(
                    deal_num(salary_min, 1000), deal_num(salary_max, base_salary), unit_str
                )

            elif salary_min >= base_salary and salary_max >= base_salary:
                if salary_min == salary_max:
                    salary_str = "{}万{}".format(deal_num(salary_max, base_salary), unit_str)
                else:
                    salary_str = "{}-{}万{}".format(
                        deal_num(salary_min, base_salary), deal_num(salary_max, base_salary), unit_str
                    )
            else:
                if salary_min == salary_max:
                    salary_str = str(salary_max) + unit_str
                else:
                    salary_str = str(salary_min) + "-" + str(salary_max) + unit_str

    return salary_str


def get_position_salary_range(salary_min, salary_max, unit_type):
    """
    招聘职位列表使用
    :param salary_min:
    :param salary_max:
    :param unit_type:
    :return:
    """

    unit_str = SalaryUnit.attrs_[unit_type] if unit_type else ""
    salary_str = ""
    if salary_min == -1 and salary_max == -1:
        salary_str = "薪资面议"
    else:
        if salary_min and salary_max:
            if salary_min == salary_max:
                salary_str = str(salary_max) + unit_str
            else:
                salary_str = str(salary_min) + "-" + str(salary_max) + unit_str
        else:
            if salary_max:
                salary_str = str(salary_max) + unit_str
            if salary_min:
                salary_str = str(salary_min) + unit_str

    return salary_str
