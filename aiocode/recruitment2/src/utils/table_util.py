from __future__ import absolute_import

import copy
from functools import cached_property

import sqlalchemy as sa

from utils.sa_db import get_table_defaults


__all__ = ["TableUtil"]


class TableUtil:
    """
    表相关工具
    """
    # todo 排除字段

    def __init__(self, tb_klass: sa.Table):
        self.table = tb_klass

    @cached_property
    def tb_keys(self):
        """
        返回table的所有keys
        """
        return [col.key for col in self.table.columns]

    def check_and_pop_fields(self, check_data: dict) -> dict:
        """
        校验数据中的key是否在table中存在， 不存在的key 则pop掉
        """
        check_data = copy.deepcopy(check_data)
        for key in check_data:
            if key not in self.tb_keys:
                check_data.pop(key)
        return check_data

    def filter_keys(self, keys: list, default: list = None, is_filter: bool = False) -> list:
        """
        过滤table中的key, 没有的key不会返回
        如果 keys 为空则返回default,
            如果没有设置 default, 则返回table所有的keys
        is_filter 是否过滤非model字段  大部分场景过滤会掩盖字段写错无法查出问题 在明确需要过滤的场景使用
        """
        default = default or self.tb_keys
        keys = keys or default

        if is_filter:
            keys = list(filter(lambda x: x in self.tb_keys, keys))

        return keys

    def table_defaults(self) -> dict:
        """
        返回所有默认值
        这里不可以缓存， 否则所有动态的默认值都固定了 eg: add_dt ..
        """
        return get_table_defaults(self.table)

    def get_default(self, key, default=None):
        return self.table_defaults().get(key, default)
