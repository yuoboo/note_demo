# -*- coding: utf-8 -*-
import uuid
from typing import Optional


def str2uuid(val):
    return uuid.UUID(val)


def str2uuid2str(val):
    if val:
        return str(uuid.UUID(val))
    return val


def uuid2str(val):
    if not val:
        return val
    if isinstance(val, uuid.UUID):
        return val.hex
    return str(val).replace('-', '')


def rm_line(uid: str) -> Optional[str]:
    """ uuid remove mid-line
    :param uid:
    :return:
    """
    if uid is None:
        return
    return uid.replace("-", "")


def add_line(uid: str) -> Optional[str]:
    """ uuid add mid-line
    :param uid:
    :return:
    """
    if uid is None:
        return
    return uuid.UUID(uid).__str__()


def gen_uuid() -> str:
    """
    产生一个uuid，并去除下划线
    """
    _id = uuid.uuid4()
    return _id.hex


def create_tree(data: list,
                pk: str = "id",
                children_key: str = "children",
                parent_key: str = "parent_id") -> list:
    """
    组装树形数据
    :param data:
    :param pk: 唯一主键
    :param children_key: 子集数据key, eg: childrens
    :param parent_key: 父级id key, eg: sup_department_id
    """
    if not data:
        return []

    _dict = {d[pk]: d for d in data}
    res = []
    for i in data:
        obj = _dict.get(i[pk])
        # 加入下级key
        obj.setdefault(children_key, [])
        # 加入上级
        parent_pk = obj.get(parent_key)
        parent = _dict.get(parent_pk)
        if not parent:
            res.append(obj)
        else:
            parent.setdefault(children_key, []).append(obj)

    return res
