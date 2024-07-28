# 快速排序
from typing import List


def select_sort(nums: List[int]):
    """
    选择排序
    """
    n = len(nums)
    # 只需要排前n-1个元素 最后剩余的一个元素肯定是最大的元素 不需要排序
    for i in range(n-1):
        k = i
        for j in range(i+1, n):
            if nums[j] < nums[i]:
                k = j
        nums[i], nums[k] = nums[k], nums[i]


def _bubble_sort(nums: List[int]):
    """冒泡排序"""
    n = len(nums)
    for i in range(n-1, 0, -1):
        flag = False
        for j in range(i):
            if nums[j] > nums[j+1]:
                nums[j], nums[j+1] = nums[j+1], nums[j]
                flag = True
        if not flag:
            break


def insertion_sort(nums: List[int]):
    """插入排序"""
    n = len(nums)
    for i in range(1, n):
        base = nums[i]
        j = i - 1
        while j >= 0 and base < nums[j]:
            nums[j+1] = nums[j]
            j -= 1
        nums[j+1] = base


def bubble_sort(a: list):
    """
    冒泡排序
    """
    n = len(a)
    if n < 2:
        return

    index = n - 1
    while index > 0:
        flag = False
        for i in range(index):
            if a[i] > a[i+1]:
                a[i], a[i+1] = a[i+1], a[i]
                flag = True

        index -= 1
        if not flag:
            break


def insertion_sort(a: list):
    """
    插入排序
    :param a:
    :param n:
    """
    n = len(a)
    if n < 2:
        return a

    for i in range(1, n):
        tmp = a[i]
        j = i
        while j > 0 and tmp < a[j-1]:
            a[j] = a[j-1]
            j -= 1
        a[j] = tmp
    return a


def get_pivot(a: list, left: int, right: int):
    """
    选取主元
    """
    center = int((left + right) / 2)
    if a[left] > a[center]:
        a[left], a[center] = a[center], a[left]

    if a[left] > a[right]:
        a[left], a[right] = a[right], a[left]

    if a[center] > a[right]:
        a[center], a[right] = a[right], a[center]

    a[center], a[right - 1] = a[right - 1], a[center]
    return a[right - 1], right - 1


def quick_sort(a: list, left: int, right: int):
    """
    快速排序
    :param a: 需要排序的对象
    :param left: 左边起点位置
    :param right: 右边起点位置
    """
    if right - left < 1:
        return

    pivot, pivot_index = get_pivot(a, left, right)
    left_i = left
    right_i = pivot_index - 1

    while True:
        while a[left_i] < pivot:
            left_i += 1

        while a[right_i] > pivot:
            right_i -= 1

        if left_i < right_i:
            a[left_i], a[right_i] = a[right_i], a[left_i]
            left_i += 1
        else:
            break

    a[left_i], a[pivot_index] = a[pivot_index], a[left_i]

    quick_sort(a, left, left_i-1)
    quick_sort(a, left_i + 1, right)


if __name__ == '__main__':
    # a = [2, 3, 5, 7, 1, 24, 5, 220, 5, 9, 0, 11]
    # b = [1,1,1,1,1,1,1,1,1,1,1,1]

    # insertion_sort(a)
    # print(f"this is insertion_sort: {a}")

    # bubble_sort(a)
    # print(f'bubble_sort:{a}')
    import time

    t1 = time.time()
    for i in range(10000):
        a_a = [2, 3, 5, 7, 1, 24, 5, 220, 5, 9, 0, 11, 33, 222, 12355, 556, 345453, 435345, 345232, 1, 1, 23, 4, 5, 3,
               32, 5,
               5]
        # quick_sort(a_a, 0, len(a_a)-1)
        bubble_sort(a_a)
    print(f"时间：{time.time() - t1}")

    # quick_sort(a, 0, len(b) - 1)
    #
    # print(a)
