from __future__ import absolute_import

import asyncio
import datetime

import sqlalchemy as sa
from constants import redis_keys
from drivers.mysql import db
from utils.cache_kits import set_cache_decorate, clear_cache_decorate
from models.m_common import tb_district, tb_school_info, tb_share_short_url, tb_share_miniqrcode
from utils.table_util import TableUtil
from utils.sa_db import db_executor


class DistrictService(object):
    """
    行政区数据
    """

    @classmethod
    @set_cache_decorate(redis_keys.COMMON_DISTRICT_LIST, expire=60*60*24*7)
    async def get_list_cache(cls):
        """
        获取列表数据缓存
        :return:
        """
        query = sa.select([
            tb_district.c.id.label("id"),
            tb_district.c.code.label("code"),
            tb_district.c.upstream.label("upstream"),
            tb_district.c.name.label("name"),
            tb_district.c.fullname.label("fullname"),
            tb_district.c.mergername.label("mergername"),
            tb_district.c.pinyin.label("pinyin"),
            tb_district.c.pinyin_lite.label("pinyin_lite"),
            tb_district.c.level.label("level"),
            tb_district.c.sort.label("sort"),
            tb_district.c.is_county_level_city.label("is_county_level_city")
        ]).order_by(
            tb_district.c.level,
            tb_district.c.id
        )
        engine = await db.common_db
        async with engine.acquire() as conn:
            exp = await conn.execute(query)
            ret = await exp.fetchall()

        return [dict(item) for item in ret]

    @classmethod
    @clear_cache_decorate([redis_keys.COMMON_DISTRICT_LIST])
    async def clear_all_cache(cls):
        pass

    @classmethod
    async def get_tree(cls, children_key="childrens"):
        """
        获取行政区树形结构数据
        """
        parent_key = "upstream"

        _cache = await cls.get_list_cache()
        data_dict = dict(zip([_c["id"] for _c in _cache], _cache))
        ret = []
        for _c in _cache:
            obj = data_dict.get(_c["id"])
            obj.setdefault(children_key, [])
            pid = _c.get(parent_key)
            parent = data_dict.get(pid)
            if parent:
                parent.setdefault(children_key, []).append(obj)
            else:
                ret.append(obj)
        return ret

    @classmethod
    async def get_district(cls, ids: list) -> dict:
        """
        查询数据库获取行政区数据
        """
        query = sa.select([
            tb_district.c.id.label("id"),
            tb_district.c.name.label("name"),
            tb_district.c.upstream.label("upstream")
        ]).where(
            tb_district.c.id.in_(ids)
        )
        engine = await db.common_db
        async with engine.acquire() as conn:
            exp = await conn.execute(query)
            ret = await exp.fetchall()

        if ret:
            return dict(zip([r["id"] for r in ret], ret))
        return dict()


class SchoolService(object):
    @classmethod
    async def get_school_by_ids(cls, name_list: list) -> dict:
        """
        查询数据库学校信息
        """
        query = sa.select([
            tb_school_info.c.id.label("id"),
            tb_school_info.c.name.label("name"),
            tb_school_info.c.label.label('label')
        ]).where(
            tb_school_info.c.name.in_(name_list)
        )

        engine = await db.common_db
        async with engine.acquire() as conn:
            exp = await conn.execute(query)
            ret = await exp.fetchall()

        return ret


tb_share_short_url_tbu = TableUtil(tb_share_short_url)


class ShareShortUrlService(object):
    @classmethod
    async def get_by_key(cls, key) -> dict:
        query_keys = tb_share_short_url_tbu.tb_keys
        exp = sa.select(
            [tb_share_short_url.c[key].label(key) for key in query_keys]
        ).where(
            tb_share_short_url.c.key == key
        )
        engine = await db.default_db
        return await db_executor.fetch_one_data(engine, exp)

    @classmethod
    async def create(cls, key, url, short_url):
        value = {
            "key": key,
            "url": url,
            "short_url": short_url,
            "add_dt": datetime.datetime.now()
        }

        engine = await db.default_db
        pk = await db_executor.single_create(
            engine, tb_share_short_url, value
        )
        return pk


tb_share_miniqrcode_tbu = TableUtil(tb_share_miniqrcode)


class ShareMiniQrCodeService(object):
    @classmethod
    async def get_by_key(cls, key) -> dict:
        query_keys = tb_share_miniqrcode_tbu.tb_keys
        exp = sa.select(
            [tb_share_miniqrcode.c[key].label(key) for key in query_keys]
        ).where(
            tb_share_miniqrcode.c.key == key
        )
        engine = await db.default_db
        return await db_executor.fetch_one_data(engine, exp)

    @classmethod
    async def create(cls, key, url, qr_code):
        value = {
            "key": key,
            "url": url,
            "qr_code": qr_code,
            "add_dt": datetime.datetime.now()
        }

        engine = await db.default_db
        pk = await db_executor.single_create(
            engine, tb_share_miniqrcode, value
        )
        return pk


if __name__ == "__main__":
    async def tester():
        # cache = await DistrictService.get_list_cache()
        # print(cache)
        # print(f"len, {len(cache)}")
        #
        # # tree = await DistrictService.get_tree()
        # # print(tree)
        # #
        # await DistrictService.clear_all_cache()
        #
        # tree2 = await DistrictService.get_tree()
        # print(tree2)
        obj = await DistrictService.get_district([3000017])
        print(obj)


    asyncio.run(tester())
