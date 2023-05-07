from abc import ABCMeta, abstractmethod


class Super(metaclass=ABCMeta):

    @abstractmethod
    def abs_method(self):
        print("this is super abs_method")


class TreeNode:

    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


class Solution:

    def pre_traversal(self, root: TreeNode) -> list:
        if not root:
            return []

        # 根节点
        res = [root.value]
        # 遍历左子树
        left = self.pre_traversal(root.left)
        # 遍历右子树
        right = self.pre_traversal(root.right)

        res.extend(left)
        res.extend(right)
        return res


if __name__ == "__main__":

    s = Super()
    s.abs_method()
