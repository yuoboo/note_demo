# -*- coding: utf-8 -*-
from __future__ import absolute_import

from aiomysql import sa
from cached_property import cached_property

from configs import config


def aiomysql_path():
    try:
        from aiomysql.connection import IncompleteReadError
        return
    except:
        pass

    try:
        from asyncio.streams import IncompleteReadError
        return
    except:
        pass

    import asyncio
    from pymysql import OperationalError

    async def _read_bytes(self, num_bytes):
        try:
            data = await self._reader.readexactly(num_bytes)
        except asyncio.exceptions.IncompleteReadError as e:
            msg = "Lost connection to MySQL server during query"
            raise OperationalError(2013, msg) from e
        except (IOError, OSError) as e:
            msg = "Lost connection to MySQL server during query (%s)" % (e,)
            raise OperationalError(2013, msg) from e
        return data

    from aiomysql.connection import Connection
    Connection._read_bytes = _read_bytes


# 0.0.21版本已修复此Bug
# aiomysql_path()


def get_db_config(name: str = "default") -> dict:
    conf = config.MYSQL_CONFIG[name]
    return dict(
        minsize=conf["pool_min_size"],
        maxsize=conf["pool_max_size"],
        host=conf["host"],
        port=conf["port"],
        user=conf["user"],
        password=conf["password"],
        db=conf["db"],
        autocommit=conf['autocommit']
    )


class DB:

    @cached_property
    async def default_db(self) -> sa.Engine:
        engine = await sa.create_engine(**get_db_config("default"), echo=True)
        return engine

    @cached_property
    async def common_db(self) -> sa.Engine:
        return await sa.create_engine(**get_db_config("common"), echo=True)

    def __init__(self):
        self.default = None
        self.common = None

    async def init_mysql_db(self):
        # 添加在初始化中
        self.default = await self.default_db
        self.common = await self.common_db

    async def close_mysql_db(self):
        self.default.close()
        await self.default.wait_closed()

        self.common.close()
        await self.common.wait_closed()


db = DB()


__all__ = ['db', ]
