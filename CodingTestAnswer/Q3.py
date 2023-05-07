

"""
Implement a stack that accepts the following commands and performs the operations described:
push v: Push integer v onto the top of the stack
pop: Pop the top element from the stack
inc i v: Add v to each of the bottom i elements of the stack
After each operation, print the value at the top of the stack. If the stack is empty, print the string 'EMPTY'.
"""


class StackUnderFlow(ValueError):
    pass


class Stack(object):
    def __init__(self):
        self.__items = list()

    def push(self, v):
        self.__items.append(v)
        self.print_top()

    def pop(self, raise_error=True):
        if self.is_empty():
            if raise_error:
                raise StackUnderFlow("stack underflow")
        else:
            value = self.__items.pop()
            self.print_top()
            return value

    def inc(self, i, v):
        new_items = []
        for x in self.__items:
            if x == i:
                x += v
            new_items.append(x)
        self.__items = new_items
        self.print_top()

    def is_empty(self):
        return len(self.__items) == 0

    def print_top(self):
        top = 'EMPTY'
        if not self.is_empty():
            top = self.__items[-1]
        print(f"the top value: {top}")

    def __str__(self):
        return f"{self.__items}"


if __name__ == '__main__':
    # python3.7.4环境运行通过

    stack = Stack()
    stack.push(1)       # output 1
    stack.push(3)       # output 3
    stack.pop()         # output 1
    stack.pop()         # output 'EMPTY'
    stack.push(1)       # output 1
    stack.push(2)       # output 2
    stack.push(1)       # output 1
    stack.inc(1, 4)     # output: 5
    print(stack)        # output: [5, 2, 5]
    stack.pop()         # output 2
    stack.pop()         # output 5
    stack.pop()         # output: EMPTY
    # stack.pop()         # output: stack underflow

