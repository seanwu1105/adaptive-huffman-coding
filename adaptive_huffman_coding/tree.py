import collections

NYT = 'NYT'


# pylint: disable=too-many-instance-attributes
class Tree:
    def __init__(self, weight, num, data=None):
        """Use a set (`nodes`) to store all nodes in order to search the same
        weight nodes (block) iteratively which would be faster than recursive
        traversal of a tree.
        """
        self.weight = weight
        self.num = num
        self._left = None
        self._right = None
        self.parent = None
        self.data = data
        # code will not be always updated
        self.code = []

    def __repr__(self):
        return "#%d(%d)%s '%s'" % (self.num, self.weight, self.data, self.code)

    @property
    def left(self):
        return self._left

    @left.setter
    def left(self, left):
        self._left = left
        if self._left:
            self._left.parent = self

    @property
    def right(self):
        return self._right

    @right.setter
    def right(self, right):
        self._right = right
        if self._right:
            self._right.parent = self

    def pretty(self, indent_str='  '):
        return ''.join(self.pretty_impl(0, indent_str))

    def pretty_impl(self, level, indent_str):
        if not self._left and not self._right:
            return [indent_str * level, '%s' % self, '\n']
        line = [indent_str * level, '%s' % self, '\n']
        for subtree in (self._left, self._right):
            if isinstance(subtree, Tree):
                line += subtree.pretty_impl(level + 1, indent_str)
        return line

    def search(self, target):
        """Search a specific data according within the tree. Return the code of
        corresponding node if found. The code is the path from the root to the
        target node. If not found in the tree, return the code of NYT node.

        Args:
            target (any): The target data which needs to be found.

        Returns:
            {'first_appearance': bool, 'code': str}: An dictionary which
                contain the information of searching result.
        """

        stack = collections.deque([self])
        while stack:
            current = stack.pop()
            if current.data == target:
                return {'first_appearance': False, 'code': current.code}
            if current.data == NYT:
                nytcode = current.code
            if current.right:
                current.right.code = current.code + [1]
                stack.append(current.right)
            if current.left:
                current.left.code = current.code + [0]
                stack.append(current.left)
        return {'first_appearance': True, 'code': nytcode}


def exchange(node1, node2):
    """Exchange the children, data of two nodes but keep the number, parent and
    weight the same. Note that this function will not change the reference of
    `node1` and `node2`.
    """

    node1.left, node2.left = node2.left, node1.left
    node1.right, node2.right = node2.right, node1.right
    node1.data, node2.data = node2.data, node1.data
