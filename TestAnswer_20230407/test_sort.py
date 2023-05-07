
"""
冒泡排序
插入排序
希尔排序
选择排序
快速排序
堆排序
归并排序
基数排序
"""

import time
import functools


def time_func(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        t1 = time.time()
        ret = func(*args, **kwargs)
        print(f"function {func.__name__} 执行时间: {time.time() - t1}")
        return ret
    return wrapper


def quick_sort(nums):
    """
    快速排序
    选择一个主元，将数组中的元素比它小的放在左边，比它大的放在右边，然后将左右两边进行递归
    """
    if len(nums) <= 1:
        return nums

    pivot = nums[0]
    left = [i for i in nums[1:] if i <= pivot]
    right = [i for i in nums[1:] if i > pivot]
    return quick_sort(left) + [pivot] + quick_sort(right)


def bubble_sort(nums):
    """冒泡排序"""
    if not nums:
        return []

    l = len(nums)
    for i in range(l):
        for j in range(l-i-1):
            if nums[j] > nums[j+1]:
                nums[j], nums[j+1] = nums[j+1], nums[j]
    return nums


def selection_sort(arr):
    length = len(arr)
    for i in range(length):
        min_index = i
        for j in range(i + 1, length):
            if arr[j] < arr[min_index]:
                min_index = j
        arr[i], arr[min_index] = arr[min_index], arr[i]
    return arr


def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr




t1 = time.time()
for i in range(10000):
    a = [2, 3, 5, 7, 1, 24, 5, 220, 5, 9, 0, 11, 33, 222, 12355, 556, 345453, 435345, 345232, 1, 1, 23, 4, 5, 3, 32, 5,
         5]
    # a1 = quick_sort(a)
    # a1 = xuanze_sort(a)
    print(a, a1)
print(f"时间：{time.time() - t1}")


