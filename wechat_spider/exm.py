
import time


def demo(cls):
    instance = {}

    def wrapper(*args, **kwargs):
        if cls not in instance:
            instance[cls] = cls(*args, **kwargs)
        return instance[cls]
    return wrapper


class Single:
    _instance = dict()

    def __new__(cls, *args, **kwargs):
        if cls not in Single._instance:
            Single._instance[cls] = object.__new__(*args, **kwargs)
        return Single._instance[cls]


class SingleMeta(type):

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super(SingleMeta, cls).__call__(*args, **kwargs)
        return cls._instance


class Foo(metaclass=SingleMeta):
    pass


@demo
class Foo:
    pass


import threading


class SingletonType(type):
    _instance_lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with SingletonType._instance_lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = super(SingletonType, cls).__call__(*args, **kwargs)
        return cls._instance


# class Foo(metaclass=SingleMeta):
#     def __init__(self, name):
#         self.name = name


if __name__ == '__main__':
    obj1 = Foo()
    obj2 = Foo()
    print(obj1, obj2)
