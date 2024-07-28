import json
import ujson
import uuid
import datetime


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

    raise TypeError("{} {} is Not JSON Serializer".format(type(obj), obj))


def json_dumps(data):
    return json.dumps(data, default=default_json)


def json_loads(data):
    return ujson.loads(data)