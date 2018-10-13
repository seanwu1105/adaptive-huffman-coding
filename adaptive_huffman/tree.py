import collections
import sys

from bitarray import bitarray

NYT = 'NYT'


class Tree:
    def __init__(self, weight, num, data=None, nodes=None, is_root=False):
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
        self.nodes = nodes
        if is_root:
            if nodes is None:
                raise ValueError(
                    'nodes should be an empty set for root of the tree.')
            self.nodes.add(self)
        # will not be always updated
        self._code = bitarray(endian=sys.byteorder)

    def __repr__(self):
        return '#%d(%d)%s %s' % (self.num, self.weight, self.data, self._code)

    @property
    def left(self):
        return self._left

    @property
    def right(self):
        return self._right

    @left.setter
    def left(self, left):
        self._left = left
        if self._left:
            self._left.parent = self
            self.nodes.add(self._left)
            self._left.nodes = self.nodes

    @right.setter
    def right(self, right):
        self._right = right
        if self._right:
            self._right.parent = self
            self.nodes.add(self._right)
            self._right.nodes = self.nodes

    def pretty(self, indent_str='  '):
        return ''.join(self._pretty(0, indent_str))

    def _pretty(self, level, indent_str):
        if not self._left and not self._right:
            return [indent_str * level, '%s' % self, '\n']
        line = [indent_str * level, '%s' % self, '\n']
        for subtree in (self._left, self._right):
            if isinstance(subtree, Tree):
                line += subtree._pretty(level + 1, indent_str)
        return line

    def search(self, target):
        """Search a specific data according within the tree. Return the code of
        corresponding node if found. The code is the path from the root to the
        target node. If not found in the tree, return the code of NYT node.

        Args:
            target (any): The target data which needs to be found.

        Returns:
            {'first_appearance': bool, 'code': bitarray}: An dictionary which
                contain the information of searching result.
        """

        stack = collections.deque([self])
        while stack:
            current = stack.pop()
            if current.data == target:
                return {'first_appearance': False, 'code': current._code}
            if current.data == NYT:
                nyt_code = current._code
            if current.right:
                current.right._code = current._code.copy()
                current.right._code.append(1)
                stack.append(current.right)
            if current.left:
                current.left._code = current._code.copy()
                current.left._code.append(0)
                stack.append(current.left)
        return {'first_appearance': True, 'code': nyt_code}


def exchange(node1, node2):
    """Exchange the children, parent, data of two nodes but keep the number and
    weight the same. Note that this function will not change the reference of
    `node1` and `node2`.
    """

    tmp_left, tmp_right, tmp_data = node1.left, node1.right, node1.data
    node1.left, node1.right, node1.data = node2.left, node2.right, node2.data
    node2.left, node2.right, node2.data = tmp_left, tmp_right, tmp_data
