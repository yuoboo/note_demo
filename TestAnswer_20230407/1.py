import os


def mm():
    return [lambda x: i * x for i in range(4)]


# s = mm()
# print([m(2) for m in s])

path = "./a.json"


def get_lines(path):
    if not path:
        return []

    with open(path, 'rb') as f:
        lines = f.readlines(2)
        yield lines


for l in get_lines(path):
    print(l)


def print_dir_path(path):
    for s_child in os.listdir(path):
        s_c_path = os.path.join(path, s_child)
        if os.path.isdir(s_c_path):
            print_dir_path(s_c_path)
        else:
            print(s_c_path)


import datetime
def dayofyear():
    year = input("请输入年份: ")
    month = input("请输入月份：")
    day = input("请输入天：")
    date1 = datetime.date(year=int(year), month=int(month), day=int(day))
    date2 = datetime.date(year=int(year), month=1, day=1)
    return (date1 - date2).days +1

"""
将字符串 "k:1 |k1:2|k2:3|k3:4"，处理成字典 {k:1,k1:2,...}
"""


def str2dict(a: str) -> dict:
    if not str:
        return dict()

    tmp_list = []
    for i in a.split("|"):
        if ":" in i:
            tmp_list.append(i.strip().split(":"))

    # return dict(tmp_list)
    return dict(map(lambda x: x.strip().split(":"), a.split("|")))


param_10 = [{'name':'a','age':20},{'name':'b','age':30},{'name':'c','age':25}]
sorted(param_10, key=lambda x: x["age"], reverse=True)

param_11 = [i for i in range(0, 100, 11)]
print(param_11)


"""
找相同元素和不同元素
"""
param_12 = [1,2,3]
param_13 = [2,3,5,6]
eq = set(param_12) & set(param_13)
diff = set(param_12) ^ (set(param_13))
print(eq, diff)



if __name__ == "__main__":

    # dir_path = "/Users/bing/code/example_py3"
    # print_dir_path(dir_path)
    # days = dayofyear()
    # print(days)

    a = [1, 2, 3, 4, 5]
    import random

    # random.shuffle(a)
    # print(a)

    # d = {"a": 24, "g": 52, "i": 12, "k": 33}
    # print(sorted(d.items(), key=lambda x: x[1]))

    param_a = "k:1 |k1:2|k2:3|k3:4"
    ret_a = str2dict(param_a)
    print(ret_a)
