import uuid
from collections.abc import Iterable
from functools import cached_property
from typing import Union

import redis


EncodedT = Union[bytes, memoryview]
DecodedT = Union[str, int, float]
EncodableT = Union[EncodedT, DecodedT]


class DataError(Exception):
    pass


class Encoder:
    """Encode strings to bytes-like and decode bytes-like to strings"""

    __slots__ = "encoding", "encoding_errors"

    def __init__(self, encoding: str, encoding_errors: str):
        self.encoding = encoding
        self.encoding_errors = encoding_errors

    def encode(self, value: EncodableT) -> EncodedT:
        """Return a bytestring or bytes-like representation of the value"""
        if isinstance(value, str):
            return value.encode(self.encoding, self.encoding_errors)
        if isinstance(value, (bytes, memoryview)):
            return value
        if isinstance(value, (int, float)):
            if isinstance(value, bool):
                # special case bool since it is a subclass of int
                raise DataError(
                    "Invalid input of type: 'bool'. "
                    "Convert to a bytes, string, int or float first."
                )
            return repr(value).encode()
        # a value we don't know how to deal with. throw an error
        typename = value.__class__.__name__
        raise DataError(
            f"Invalid input of type: {typename!r}. "
            "Convert to a bytes, string, int or float first."
        )

    def decode(self, value: EncodableT) -> EncodableT:
        """Return a unicode string from the bytes-like representation"""
        if isinstance(value, bytes):
            return value.decode(self.encoding, self.encoding_errors)
        if isinstance(value, memoryview):
            return value.tobytes().decode(self.encoding, self.encoding_errors)
        return value


class StrKit:
    __encode = "utf8"

    @classmethod
    def de2str(cls, data, encode=None):
        _code = cls.__encode if encode is None else encode

        if isinstance(data, bytes):
            return data.decode(_code)

        elif isinstance(data, memoryview):
            return data.tobytes().decode(_code)

        elif isinstance(data, str):
            return data

        elif isinstance(data, dict):
            tmp_dict = dict()
            for k, v in data.items():
                k = cls.de2str(k, _code)
                v = cls.de2str(v, _code)
                tmp_dict[k] = v
            return tmp_dict

        elif isinstance(data, (list, tuple, set)):
            tmp_list = []
            for d in data:
                tmp_list.append(cls.de2str(d, _code))
            return tmp_list

        return data

    @classmethod
    def en2bytes(cls, data, encode=None):
        _code = cls.__encode if encode is None else encode
        if isinstance(data, str):
            return data.encode(_code)

        elif isinstance(data, (bytes, memoryview)):
            return data

        elif isinstance(data, dict):
            tmp_dict = dict()
            for k, v in data.items():
                k = cls.en2bytes(k, _code)
                v = cls.en2bytes(v, _code)
                tmp_dict[k] = v
            return tmp_dict

        elif isinstance(data, Iterable):
            # 这里需要区分list , tuple，set等一些容器类型
            pass

        return data


class RedisKit:
    """
    需要实现的功能为： 项目初始化之后生成一个公用的client
    特殊场景，client 支持切换db
    """

    encode = "utf8"
    __db_instance = dict()

    def __init__(self, host=None, port=None, db=None):
        self._host = host
        self._port = port
        self._db = db
        self.get_init()
        # self.client = self.get_db()

    @staticmethod
    def get_config():
        # TODO 这里可以从配置文件中获取
        return "localhost", 6379, 0

    def get_init(self):
        _h, _p, _b = self.get_config()
        if self._host is None:
            self._host = _h

        if self._port is None:
            self._port = _p

        if self._db is None:
            self._db = _b

    def get_db_instances(self):
        return self.__db_instance

    @cached_property
    def client(self):
        """单例"""
        _key = f"{self._host}:{self._port}:{self._db}"
        if _key not in self.__db_instance:
            self.__db_instance[_key] = redis.Redis(host=self._host, port=self._port, db=self._db)
        return self.__db_instance[_key]

# redis_db = redis.StrictRedis(host='localhost', port=6379, db=0)

redis_db = RedisKit()


redis_db.client.set('foo', 'bar')
foo = redis_db.client.get("foo")
print(f"this is foo {foo}")


def gen_uuid():
    return uuid.uuid4().hex


encode_str = "utf8"

uid = gen_uuid()
print(uid)
for i in range(10):
    redis_db.client.xadd(uid, {"name": f"我你他{i}", "age": i*10})

xl = redis_db.client.xlen(uid)
xr = redis_db.client.xread({uid: '0'}, count=2, block=20)
print(f"this is xread {StrKit.de2str(xr)}")


def stream2dict(streams: list, code="utf8") -> dict:
    res = dict()
    if streams:
        _key, _ = streams[0]
        # _key = _key.decode(code)
        res[_key] = dict(_)
        # for i in _:
        #     s_id = i[0].decode(code)
        #     _d = {j.decode(code): i[1][j].decode(code) for j in i[1]}
        #     res[_key].append({s_id: _d})
    return res

# key, messages = xr[0]
# last_id, data = messages[0]  # (b'1682695122165-0', {b'name': b'tom', b'age': b'10'})
#
# data_dict = {i.decode(encode_str): data[i].decode(encode_str) for i in data}
# data_dict[key.decode(encode_str)] = last_id.decode(encode_str)
data_dict = stream2dict(xr)
print(StrKit.de2str(data_dict))


class RedisStreamKit(RedisKit):
    """
    {"key": [{"stream_id": "", "data": {}}, ...], "key2": []}
    1. xadd  需不需要做批量add?
    2. xread  注意count > 1时的处理， streams={stream_key:0,stream2_key:0}
    3. xread -> dict
    4. xread 连续读，接着上次读的数据往下读
    5. xlen 查询key下的条目数量
    6. xdel 删除
    """

    @staticmethod
    def stream2dict(streams: list, is_decode) -> dict:
        res = dict()
        for _key, _mgs in streams:
            res[_key] = dict(_mgs)

        if res and is_decode:
            return StrKit.de2str(res)
        return res

    def add(self, key: str, fields: dict, **kwargs):
        self.client.xadd(name=key, fields=fields, **kwargs)

    def read(self, streams: dict, count=1, block=100) -> list:
        """
        读取流 返回list, 数据为bytes
        :param streams: {key: stream_id， key1: stream_id1}
        :param count: 返回stream的数量
        :param block: 阻塞时间 ms
        """
        return self.client.xread(streams, count=count, block=block)

    def read2dict(
            self, streams: dict,
            count: int = 1,
            block: int = 100,
            is_decode: bool = False) -> dict:
        """
        读取流，返回dict, 数据已解码为 str
        :param streams: {key: stream_id, key2: xxx}
        :param count: 返回messages的数量
        :param block: 阻塞时间单位ms
        :param is_decode: 是否需要decode成str, 默认为False
        """
        # TODO 这里count不为1时，不能这样处理
        _s = self.read(streams, count=count, block=block)
        return self.stream2dict(_s, is_decode)

    def del_key(self, key, *stream_ids):
        self.client.xdel(key, *stream_ids)

    def get_length(self, key):
        return self.client.xlen(key)

    def create_group(self, ):
        pass

    def get_stream_info(self):
        pass

    def get_group_info(self): pass



