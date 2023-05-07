
"""
Rearrange an array of integers so that the calculated value U is maximized.
Among the arrangements that satisfy that test,
choose the array with minimal ordering.
The value of U for an array with n elements is calculated as :
    U = arr[1]×arr[2]×(1÷arr[3])×arr[4]×...×arr[n-1] × (1÷arr[n]) if n is odd or
    U = arr[1]×arr[2]×(1÷arr[3])×arr[4]×...×(1÷arr[n-1]) × arr[n] if n is even

The sequence of operations is the same in either case,
but the length of the array, n, determines whether the calculation ends on arr[n] or (1÷arr[n]).
Arrange the elements to maximize U and the items are in the numerically smallest possible order
"""


def rearrange(array: list) -> list:
    """
    思路： 从题目中可以看出，数组的奇数位的计算是 1÷ arr[奇数位] 因此将较小的数放入奇数位，将较大的数放入偶数位
          最后结果需要按最小顺序输出， 所以奇数位与偶数位均需要从小到大排序
    """
    length = len(array)
    if length < 3:
        array.sort()
        return array

    if length % 2 == 0:
        min_num = length // 2 - 1
    else:
        min_num = length // 2

    array.sort()
    min_array = array[0: min_num]   # 原数组中较小的数值列表
    min_array = min_array[::-1]
    max_array = array[min_num:]     # 原数组中较大的数值列表
    max_array = max_array[::-1]

    res = []
    for i in range(1, length+1):
        if i == 1 or i == 2:
            res.append(max_array.pop())
        elif i % 2 == 1:  # 奇数位 取min_array
            res.append(min_array.pop())
        else:
            res.append(max_array.pop())

    return res


if __name__ == '__main__':
    # 以下代码在python3.7.4环境运行通过
    # 特殊情况： 数组长度为 1 或者 2
    input_array = [1]
    output = rearrange(input_array)
    print(f"output of length_1: {output}")

    input_array = [4, 1]
    output = rearrange(input_array)
    print(f"output of length_2: {output}")

    # 数组长度为奇数
    input_array = [2, 1, 5, 8, 9, 3, 11, 57, 101, 3, 8]
    output = rearrange(input_array)
    print(f"output of length_odd: {output}")

    # 数组长度为偶数
    input_array = [1, 2, 4, 7, 2, 9, 3, 41, 23, 97, 3, 8]
    output = rearrange(input_array)
    print(f"output of length_even: {output}")

