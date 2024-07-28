from __future__ import absolute_import
import uuid
import datetime
import asyncio
import functools
import json

import aioredis

from constants import CacheType
from kits.exception import ServiceError
from services.s_https.s_ucenter import get_company_user
from utils.strutils import uuid2str
from drivers.redis import redis_db


def format_json(data):
    """
    部分格式不能直接json化, 需要转换一下格式
    eg: UUID, set, datetime.datetime, datetime.date
    """
    if isinstance(data, uuid.UUID):
        return data.hex

    elif isinstance(data, (datetime.date, datetime.datetime)):
        return str(data)

    elif isinstance(data, dict):
        ret = dict()
        for k, v in data.items():
            k = format_json(k)
            v = format_json(v)
            ret[k] = v

    elif isinstance(data, (list, tuple)):
        ret = []
        for x in data:
            ret.append(format_json(x))
        ret = type(data)(ret)

    elif isinstance(data, set):
        # set 不能json化, 这里直接转为list
        ret = []
        for x in data:
            ret.append(format_json(x))
    else:
        return data

    return ret


def default_json(obj):
    """
    单独处理不能json化的格式
    """
    if isinstance(obj, uuid.UUID):
        return obj.hex

    elif isinstance(obj, set):
        return list(obj)

    elif isinstance(obj, (datetime.datetime, datetime.date)):
        return str(obj)

    raise TypeError(f"{type(obj)} {obj} is Not JSON Serializer")


class CacheKlass(object):
    _expire = 60*60*24  # 过期时间
    _company_list_cache_key = None  # 企业数据缓存key, 返回列表数据
    _company_tree_cache_key = None  # 企业数据缓存key, 返回树形结构数据, 需要额外设置_parent_key
    _user_list_cache_key = None     # 用户数据缓存key, 返回列表数据
    _user_tree_cache_key = None     # 用户数据缓存key, 返回树形结构数据, 需要额外设置_parent_key

    # 用来自动创建树结构的key
    _parent_key = None   # 上级字段key
    _children_key = "childrens"    # 下级字段key
    _pk = "id"  # 唯一键, 缓存数据中必须带有此字段
    _cache_db = CacheType.common    # redis 连接池类型

    """
    说明:
    1. 继承的类需要实现 get_company_data/get_user_data, 该方法返回的数据为缓存设置的数据
    2. 缓存key中company_id, user_id需要使用占位符 {company_id},{user_id}
        eg: "recruitment2:configs:header:{company_id}_{user_id}"
        
    3. 使用树形结构的缓存需要设置 _company_list_cache_key, _company_tree_cache_key, _parent_key, _children_key 四个属性
    """

    @classmethod
    async def get_cache_db(cls, cache_type: str = None):
        cache_type = cache_type or cls._cache_db
        if cache_type == CacheType.common:
            return await redis_db.common_redis
        elif cache_type == CacheType.default:
            return await redis_db.default_redis

        raise Exception(f"the _cache_db of {cls.__name__} must choice from CacheType")

    @classmethod
    async def get_company_data(cls, company_id):
        raise NotImplementedError

    @classmethod
    async def get_user_data(cls, company_id, user_id):
        raise NotImplementedError

    @classmethod
    async def create_tree(cls, data):
        """
        生成树形结构数据
        :param data: 源数据，如果有序则需要先排序
        """
        if not data:
            return []

        if not cls._parent_key:
            raise ServiceError(msg="请指定 _parent_key of CacheKlass")

        _dict = {d[cls._pk]: d for d in data}
        res = []
        for i in data:
            obj = _dict.get(i[cls._pk])
            # 加入下级key
            obj.setdefault(cls._children_key, [])
            # 加入上级
            parent_pk = obj.get(cls._parent_key)
            parent = _dict.get(parent_pk)
            if not parent:
                res.append(obj)
            else:
                parent.setdefault(cls._children_key, []).append(obj)

        return res

    @classmethod
    async def cache_company_list(cls, company_id):
        """
        获取企业的缓存数据
        """
        if not getattr(cls, "_company_list_cache_key"):
            raise NotImplementedError

        company_id = uuid2str(company_id)
        if not company_id:
            raise ServiceError(msg="company_id 参数错误")

        cache_key = cls._company_list_cache_key.format(company_id=company_id)
        # _redis = await redis_db.common_redis
        _redis = await cls.get_cache_db()
        cache_data = await _redis.get(cache_key)
        if cache_data is None:
            _data = await cls.get_company_data(company_id)
            cache_data = json.dumps(_data, default=default_json)
            await _redis.set(cache_key, cache_data, expire=cls._expire)

        cache_data = json.loads(cache_data)

        return cache_data

    @classmethod
    async def cache_company_tree(cls, company_id):
        """
        获取企业缓存数据  树形结构
        """
        if not getattr(cls, "_company_tree_cache_key"):
            raise NotImplementedError

        company_id = uuid2str(company_id)
        if not company_id:
            raise ServiceError(msg="company_id 参数错误")

        cache_key = cls._company_tree_cache_key.format(company_id=company_id)
        # _redis = await redis_db.common_redis
        _redis = await cls.get_cache_db()
        cache_data = await _redis.get(cache_key)
        if cache_data is None:
            _data = await cls.cache_company_list(company_id)
            _data = await cls.create_tree(_data)
            cache_data = json.dumps(_data, default=default_json)
            await _redis.set(cache_key, cache_data, expire=cls._expire)

        cache_data = json.loads(cache_data)

        return cache_data

    @classmethod
    async def cache_user_list(cls, company_id, user_id):
        """
        获取用户缓存信息
        """
        if not getattr(cls, "_user_list_cache_key"):
            raise NotImplementedError

        company_id = uuid2str(company_id)
        user_id = uuid2str(user_id)
        if not all([company_id, user_id]):
            raise ServiceError(msg="cache:参数缺失")

        cache_key = cls._user_list_cache_key.format(company_id=company_id, user_id=user_id)
        # _redis = await redis_db.common_redis
        _redis = await cls.get_cache_db()
        cache_data = await _redis.get(cache_key)
        if cache_data is None:
            user_data = await cls.get_user_data(company_id, user_id)
            cache_data = json.dumps(user_data, default=default_json)
            await _redis.set(cache_key, cache_data, expire=cls._expire)

        cache_data = json.loads(cache_data)

        return cache_data

    @classmethod
    async def cache_user_tree(cls, company_id, user_id):
        """
        获取用户缓存树形信息
        """
        if not getattr(cls, "_user_tree_cache_key"):
            raise NotImplementedError

        company_id = uuid2str(company_id)
        user_id = uuid2str(user_id)
        if not all([company_id, user_id]):
            raise ServiceError(msg="cache: 参数错误")

        cache_key = cls._user_tree_cache_key.format(company_id=company_id, user_id=user_id)
        # _redis = await redis_db.common_redis
        _redis = await cls.get_cache_db()
        cache_data = await _redis.get(cache_key)
        if cache_data is None:
            user_data = await cls.cache_user_list(company_id, user_id)
            user_data = await cls.create_tree(user_data)
            cache_data = json.dumps(user_data, default=default_json)
            await _redis.set(cache_key, cache_data, expire=cls._expire)

        cache_data = json.loads(cache_data)
        return cache_data

    @classmethod
    async def clear_company_cache(cls, company_id, extra_keys: list = None):
        """
        清除公司缓存
        """
        company_id = uuid2str(company_id)
        if not company_id:
            raise ServiceError(msg="company_id 参数错误")

        keys = []
        if cls._company_list_cache_key:
            keys.append(cls._company_list_cache_key.format(company_id=company_id))

        if cls._company_tree_cache_key:
            keys.append(cls._company_tree_cache_key.format(company_id=company_id))

        if cls._user_list_cache_key or cls._user_tree_cache_key:
            company_user_ids = [com.user_id for com in await get_company_user(company_id) if com.get("is_enabled")]

            for user_id in company_user_ids:
                user_id = uuid2str(user_id)
                if cls._user_list_cache_key:
                    keys.append(cls._user_list_cache_key.format(company_id=company_id, user_id=user_id))
                if cls._user_tree_cache_key:
                    keys.append(cls._user_tree_cache_key.format(company_id=company_id, user_id=user_id))

        if extra_keys:
            keys.extend(extra_keys)

        if keys:
            _redis = await redis_db.common_redis
            await _redis.delete(*keys)

    @classmethod
    async def clear_user_cache(cls, company_id, user_id, extra_keys: list = None):
        """
        清除指定用户缓存
        @:param extra_keys: 额外的缓存key, 存在格式不统一的key可以手动添加进来一起清除掉
        """
        company_id = uuid2str(company_id)
        user_id = uuid2str(user_id)

        keys = []
        if cls._user_list_cache_key:
            keys.append(cls._user_list_cache_key.format(company_id=company_id, user_id=user_id))

        if cls._user_tree_cache_key:
            keys.append(cls._user_tree_cache_key.format(company_id=company_id, user_id=user_id))

        if extra_keys:
            keys.extend(extra_keys)

        if keys:
            _redis = await redis_db.common_redis
            await _redis.delete(*keys)


def set_cache_decorate(cache_key, expire=60*60*24):
    """
    缓存装饰器
    :param cache_key: 缓存key
    :param expire: 过期时间 单位秒(s), 默认缓存时间 24个小时
    :return:
    """
    def func(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            _redis = await redis_db.common_redis
            cache_data = await _redis.get(cache_key)
            # 没有缓存
            if cache_data is None:
                _data = await fn(*args, **kwargs)
                cache_data = json.dumps(_data, default=default_json)
                await _redis.setex(cache_key, expire, cache_data)

            cache_data = json.loads(cache_data)
            return cache_data
        return wrapper
    return func


def clear_cache_decorate(cache_keys):
    """
    执行相应函数，执行完毕之后清除对应key的缓存
    :param cache_keys: 缓存key列表
    :return:
    """
    def func(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            data = await fn(*args, **kwargs)
            _redis = await redis_db.common_redis
            await _redis.delete(*cache_keys)
            return data

        return wrapper
    return func


if __name__ == "__main__":

    class DemoService(CacheKlass):
        _company_list_cache_key = "recruitment2:cache:demo:list:{company_id}"
        _user_list_cache_key = "recruitment2:cache:demo:list:{company_id}:{user_id}"

        _company_tree_cache_key = "recruitment2:cache:demo:tree:{company_id}"
        _user_tree_cache_key = "recruitment2:cache:demo:tree:{company_id}:{user_id}"

        _parent_key = "parent_id"

        @classmethod
        async def get_company_data(cls, company_id):
            return [{"id": 1, "num": 1, "parent_id": None}, {"id": 2, "num": 2, "parent_id": None},
                    {"id": 3, 'num': 3, "parent_id": 2}, {"id": 4, "num": 4, "parent_id": 1},
                    {"id": 5, "num": 5, "parent_id": 1}, {"id": 6, "num": 6, "parent_id": 2},
                    {"id": 7, "num": 7, "parent_id": 4}, {"id": 8, "num": 8, "parent_id": 3},
                    {"id": 9, "num": 9, "parent_id": 6}]

        @classmethod
        async def get_user_data(cls, company_id, user_id):
            return [{"id": 'u1', "num": 1, "parent_id": None}, {"id": 'u2', "num": 2, "parent_id": None},
                    {"id": "u3", "num": 3, "parent_id": "u1"}, {"id": "u4", "num": 4, "parent_id": "u1"},
                    {"id": "u5", "num": 5, "parent_id": "u2"}, {"id": "u6", "num": 6, "parent_id": "u3"}]

    # 测试缓存类
    async def helper():

        # res4 = await get_company_user("f79b05ee3cc94514a2f62f5cd6aa8b6e")
        # print(res4)

        res1 = await DemoService.cache_company_list("f79b05ee3cc94514a2f62f5cd6aa8b6e")
        print(f'user_cache, {res1}, {type(res1)}')

        res2 = await DemoService.cache_user_list("f79b05ee3cc94514a2f62f5cd6aa8b6e", "362f7de6128e460589ef729e7cdda774")
        print(f'{res2}, {type(res2)}')

        res3 = await DemoService.cache_company_tree("f79b05ee3cc94514a2f62f5cd6aa8b6e")
        print(f'company_tree: {res3}')

        res4 = await DemoService.cache_user_tree("f79b05ee3cc94514a2f62f5cd6aa8b6e", "362f7de6128e460589ef729e7cdda774")
        print(f'user_tree: {res4}')

        await DemoService.clear_company_cache("f79b05ee3cc94514a2f62f5cd6aa8b6e")
        await DemoService.clear_user_cache("f79b05ee3cc94514a2f62f5cd6aa8b6e", "362f7de6128e460589ef729e7cdda774")

    # 测试缓存装饰器
    @clear_cache_decorate("recruitment2:decorate:demo")
    @set_cache_decorate("recruitment2:decorate:demo", expire=60*60)
    async def helper2(name, age):
        # return f"this is test cache decorate, {name}, {age}"
        return [{"id": uuid.uuid4(), "name": ({"id": uuid.uuid4(), "name": {1, 2, 3}}, '12333', '2223')},
                {"id": uuid.uuid4(), "name": {"1222", "3333", "3333443"}},
                {"id": uuid.uuid4(), "name": [1, 2, 34, datetime.date(2020, 10, 10), datetime.datetime.today()]},
                ]

    # asyncio.run(helper2("tom", 10))
    asyncio.run(helper())


