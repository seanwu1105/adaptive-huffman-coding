class Tree:
    NYT = 'NYT'

    def __init__(self, weight, num, data=None, nodes=None, root=False):
        """ Use a set (`nodes`) to store all nodes in order to search the same
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
        if root:
            self.nodes.add(self)
        self.code = list()

    def __repr__(self):
        return '#%d(%d)[%s]%s' % (self.num, self.weight, self.data, self.code)

    @property
    def left(self):
        return self._left

    @property
    def right(self):
        return self._right

    @left.setter
    def left(self, left):
        self._left = left
        self._left.parent = self
        self.nodes.add(self._left)
        self._left.nodes = self.nodes

    @right.setter
    def right(self, right):
        self._right = right
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

    def build_codes(self):
        stack = [self]
        while stack:
            current = stack.pop()
            if current.right:
                current.right.code = [*current.code, 1]
                stack.append(current.right)
            if current.left:
                current.left.code = [*current.code, 0]
                stack.append(current.left)
