
"""
二叉树遍历问题
    1. 递归实现
    2. 非递归 -> 堆栈模式
"""


class TreeNode:

    def __init__(self, name: str, left=None, right=None):
        self.name = name
        self.left = left
        self.right = right


class Tree:

    def __init__(self, root: TreeNode):
        self.root = root
        self.__nodes = []
        self.__output_recursion = []

    def pre_order_traversal(self):
        """
        先序遍历
        """
        __output = []
        t = self.root
        while t or self.__nodes:
            while isinstance(t, TreeNode):
                self.__nodes.append(t)
                __output.append(t.name)
                t = t.left
            if self.__nodes:
                t = self.__nodes.pop()
                t = t.right

        self.print_output(__output)

    def in_order_traversal(self):
        """
        中序遍历树
        """
        __output = []
        t = self.root
        while t or self.__nodes:
            while isinstance(t, TreeNode):
                self.__nodes.append(t)
                t = t.left
            if self.__nodes:
                t = self.__nodes.pop()
                __output.append(t.name)
                t = t.right
        self.print_output(__output)

    def post_order_traversal(self):
        """
        后序遍历
        """
        __output = []
        t = self.root
        pre_pop = None
        while t or self.__nodes:
            while isinstance(t, TreeNode):
                self.__nodes.append(t)
                t = t.left

            if self.__nodes:
                t = self.__nodes.pop()
                if t.right is None or t.right == pre_pop:
                    __output.append(t.name)
                    pre_pop = t
                    t = None
                else:
                    self.__nodes.append(t)
                    t = t.right

        self.print_output(__output)

    def binary_tree_by_recursion(self, tree_node: TreeNode, rec_type: str = "pre"):
        """
        递归实现二叉树的遍历, 注意遍历树的路径在三种方式下都是相同的，只是输出的时机有所不同而已， 入口为根节点，出口也是根节点
        :param tree_node: 根节点
        :param rec_type: 输出类型 - 先序 pre，中序 in，后序 post
        """
        if isinstance(tree_node, TreeNode):
            if rec_type == "pre":
                self.__output_recursion.append(tree_node.name)

            self.binary_tree_by_recursion(tree_node.left, rec_type)
            if rec_type == 'in':
                self.__output_recursion.append(tree_node.name)
            self.binary_tree_by_recursion(tree_node.right, rec_type)
            if rec_type == 'post':
                self.__output_recursion.append(tree_node.name)

            if tree_node == self.root:  # 入口和出口均为根节点， 所以这里根节点处理完之后统一输出结果
                self.print_output(self.__output_recursion)

    @staticmethod
    def print_output(output: list):
        if output:
            print(f"output: {output}")
        else:
            print("output: 空树")


node_a = TreeNode('a')
node_b = TreeNode('b')
node_c = TreeNode('c')
node_d = TreeNode('d')
node_e = TreeNode('e')
node_f = TreeNode('f')
node_a.left = node_b
node_b.left = node_c
node_b.right = node_d
node_d.left = node_e
node_d.right = node_f

if __name__ == '__main__':

    tree = Tree(node_a)
    tree.pre_order_traversal()
    tree.in_order_traversal()
    tree.post_order_traversal()
    tree.binary_tree_by_recursion(tree.root, rec_type='in')


