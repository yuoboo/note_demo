import os

"""
请写出一个单例，用两种方法
"""


def singleton(cls):
    instances = dict()
    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return wrapper


class Singleton(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance


class Foo(Singleton):
    pass

# r'(?P<ip>.*?) - - \[(?P<time>.*?)\] "(?P<request>.*?)" (?P<status>.*?)
class Singleton3(type):
    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super(Singleton3, cls).__call__(cls, *args, **kwargs)
        return cls._instance


class Foo3(metaclass=Singleton3):
    pass


"""
抓取目录下所有的.pyc文件
"""


def get_files(path: str, suffix: str = '.pyc') -> list:
    ret = []
    for root, dirs, files in os.walk(path):
        for filename in files:
            name, suff = os.path.splitext(filename)
            if suff == suffix:
                ret.append(os.path.join(root, filename))
    return ret


def get_files2(path, suffix):

    files = os.listdir(path)
    for file in files:
        if os.path.isfile(file):
            if file.endswith(suffix):
                print(file)
        elif os.path.isdir(file):
            get_files2(file, suffix)


from functools import reduce
params_sum = reduce(lambda x,y: x+y, [1,2,3,10248])



def atoi(s):
    num = 0
    demo = '0123456789'
    for v in s:
        # for j in range(10):
        #     if v == str(j):
        #         num = num * 10 + j
        num = num * 10 + demo.index(v)
    return num

ret_atoi = atoi('123')
print(ret_atoi)


"""
给定一个整数数组和一个目标值，找出数组中和为目标值的两个数。
你可以假设每个输入只对应一种答案，且同样的元素不能被重复利用。
示例:给定nums = [2,7,11,15],target=9 因为 nums[0]+nums[1] = 2+7 =9,所以返回[0,1]
"""


def get_target(nums: list, target: int) -> list:
    ret = []
    for index, num in enumerate(nums):
        for num_j in nums[index+1:]:
            if num + num_j == target:
                ret.append((index, nums.index(num_j)))

    return ret


nums = [2,7,11,15, 4, 5]
target= 9
params_ret = get_target(nums, target)
print(params_ret)


params_nums2 = [1,3,2,1,5,7,6,0,1,3]


def get_oushu(nums: list) -> list:
    return list(filter(lambda x: x % 2 == 0 and nums.index(x) % 2 == 0, nums))


print(get_oushu(params_nums2))

"""
[1,4,9,16,25,36,49,64,81,100]
"""
l = [(i+1)*(i+1) for i in range(10)]

param_str2 = 'aaabbdddccc'
print(param_str2.count('a'))


import time
import asyncio

async def test_sync():
    await asyncio.sleep(1)
    print(1)


async def test_sleep2(t=2):
    await asyncio.sleep(t)
    print(t)


async def main():
    t1 = time.time()
    # await test_sync()
    # await test_sleep2()

    # await asyncio.gather(
    #     test_sync(), test_sleep2()
    # )
    # task_1 = asyncio.create_task(test_sync())
    # task_2 = asyncio.create_task(test_sleep2())
    # await task_1
    # await task_2
    # await asyncio.shield(test_sleep2(5))
    #
    done, pending = await asyncio.wait([test_sync(), test_sleep2(5), test_sleep2(10)], return_when="FIRST_COMPLETED")
    print(done)
    print(pending)
    print(time.time() - t1)
    for pend in pending:
        await pend
    print(111, time.time() - t1)
# asyncio.run(main())


@asyncio.coroutine
def test_coroutine():
    yield from asyncio.sleep(1)


test_a = asyncio.iscoroutine(test_coroutine())
print(test_a)


class Array:
    __list = []

    def __new__(cls, *args, **kwargs):
        return super(Array, cls).__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        print(f'参数-{args}, {kwargs}')

    def __getattribute__(self, item):
        pass

    def __getattr__(self, item):
        pass


import functools


def time_func(func):

    @functools.wraps
    def wrapper(*args, **kwargs):
        t1 = time.time()
        ret = func(*args, **kwargs)
        print(f"function {func.name} 执行时间: {time.time() - t1}")
        return ret
    return wrapper


import re


pattern = r'^HTTP/1.1\s\d{3}\s\d{3,}?"$'
pattern_1 = r'\d{3}\s+\d{3,}'
pattern_2 = re.compile(r'(\d+\.\d+\.\d+\.\d+).*(\d{3}\s+\d{3,})')

param = '8.215.71.118 - - [26/Oct/202207:01:53 +0800 ] "GET http://www.baidu.com/ HTTP/1.1 400 2712 "-" "-"'
ret = re.findall(pattern_1, param)
ip_ = re.findall(pattern_2, param)
print(ip_)




ret_1 = re.match('c', 'abcdef')
print(ret_1, 333)






