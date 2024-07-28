# coding: utf-8
from datetime import datetime

import sqlalchemy
from aiomysql import sa
from sanic.request import Request

from utils.strutils import gen_uuid


class Paginator:
    DEFAULT_PAGE = 1
    DEFAULT_PER_PAGE = 20

    def __init__(self, engine: sa.Engine, exp, page: int = 1, limit: int = 20):
        self._exp = exp
        self._page = page
        self._limit = limit
        self._engine = engine

    @staticmethod
    def parse_limit_offset(page, limit):
        offset = (page - 1) * limit
        return limit, offset

    async def data(self):
        """
        获取分页数据
        """
        async with self._engine.acquire() as conn:
            count_exp = self._exp.with_only_columns([sqlalchemy.func.count(1)])
            count_result = await conn.execute(count_exp)
            total = await count_result.scalar()
            if total % self._limit == 0:
                total_page = 1
            else:
                total_page = (total - 1) // self._limit + 1
            limit, offset = self.parse_limit_offset(self._page, self._limit)
            rows_sql_stmt = self._exp.limit(limit).offset(offset)
            rows_result = await conn.execute(rows_sql_stmt)
            items = await rows_result.fetchall()

        return {
            'p': self._page,
            'limit': self._limit,
            'offset': 1,
            'totalpage': total_page,
            'total_count': total,
            'objects': [dict(item) for item in items]
        }

    @classmethod
    def get_p_limit(cls, request: Request):
        def _parse_page(d: dict):
            _p = d.get('p') or d.get('page')
            if _p:
                try:
                    _p = int(_p)
                    if _p < 1:
                        _p = cls.DEFAULT_PAGE
                except ValueError:
                    _p = cls.DEFAULT_PAGE
            return _p

        def _parse_limit(d: dict):
            _limit = d.get("limit")
            if _limit:
                try:
                    _limit = int(_limit)
                    if _limit < 0:
                        _limit = cls.DEFAULT_PAGE
                except ValueError:
                    _limit = cls.DEFAULT_PER_PAGE

            return _limit

        def _get_page(req: Request):
            page = _parse_page(req.args or {})
            if not page:
                page = _parse_page(req.json or {})
                if not page:
                    page = _parse_page(req.form or {})
                    if not page:
                        page = cls.DEFAULT_PAGE
            return page

        def _get_limit(req: Request):
            limit = _parse_limit(req.args or {})
            if not limit:
                limit = _parse_limit(req.json or {})
                if not limit:
                    limit = _parse_limit(req.form or {})
                    if not limit:
                        limit = cls.DEFAULT_PER_PAGE

            return limit

        p = _get_page(request)
        lmt = _get_limit(request)

        return p, lmt


def get_table_defaults(table_klass: sqlalchemy.Table) -> dict:

    defaults = dict()
    for column in table_klass.columns:
        if column.default is not None:
            value = column.default.arg
            if callable(value):
                # sqlalchemy会将default的函数统一为只支持一个参数，所以需要传一个无用的位置参数，建议所有自定义函数都不要有参数，这里统一处理
                value = value(None)
            defaults[column.key] = value
    return defaults


def get_table_onupdate(table_klass: sqlalchemy.Table) -> dict:
    data = dict()
    for column in table_klass.columns:
        if column.onupdate is not None:
            value = column.onupdate.arg
            if callable(value):
                # sqlalchemy会将default的函数统一为只支持一个参数，所以需要传一个无用的位置参数，建议所有自定义函数都不要有参数，这里统一处理
                value = value(None)
            data[column.key] = value

    return data


class DbExecutor:
    """
    数据库执行器
    """

    def _get_default_values(self, table_name: sqlalchemy.Table) -> dict:
        """
        获取table实例的默认值
        """
        return get_table_defaults(table_name)

    def _get_onupdate_values(self, table_name: sqlalchemy.Table) -> dict:
        """
        获取table实例更新的默认值
        """
        return get_table_onupdate(table_name)

    async def fetch_one_data(self, engine: sa.Engine, stmt) -> dict:
        """
        查询一条
        """
        async with engine.acquire() as conn:
            result = await conn.execute(stmt)
            data = await result.fetchone()

        return dict(data) if data else {}

    async def fetch_all_data(self, engine: sa.Engine, stmt) -> list:
        """
        查询所有
        """
        async with engine.acquire() as conn:
            result = await conn.execute(stmt)
            data = await result.fetchall()

        return data

    async def single_create(self, engine: sa.Engine, table_name: sqlalchemy.Table, values: dict) -> str:
        """
        单个插入数据
        """
        data = self._get_default_values(table_name)
        data.update(values)
        stmt = sqlalchemy.insert(table_name).values(data)
        async with engine.acquire() as conn:
            await conn.execute(stmt)

        return data.get("id")

    async def batch_create(self, engine: sa.Engine, table_name: sqlalchemy.Table, values: list) -> list:
        """
        批量插入数据
        """
        for row in values:
            row["id"] = row.get("id") or gen_uuid()
        stmt = sqlalchemy.insert(table_name).values(values)
        async with engine.acquire() as conn:
            await conn.execute(stmt)
        return [v["id"] for v in values]

    async def update_data(self, engine: sa.Engine, table_name: sqlalchemy.Table, values: dict, where_stmt) -> int:
        """
        更新指定条件的数据
        """
        on_update_data = self._get_onupdate_values(table_name)
        values.update(on_update_data)
        stmt = sqlalchemy.update(table_name).where(where_stmt).values(values)
        async with engine.acquire() as conn:
            result = await conn.execute(stmt)
        return result.rowcount


db_executor = DbExecutor()


__all__ = ['db_executor', "Paginator"]
