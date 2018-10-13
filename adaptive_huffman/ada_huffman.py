import operator
import sys

from bitarray import bitarray
from progress.bar import Bar
import numpy as np

from .tree import Tree, NYT, exchange


class AdaptiveHuffman:
    def __init__(self, byte_seq, alphabet_size):
        self.byte_seq = byte_seq
        self.alphabet_size = alphabet_size

        # Initialize the current node # as the maximum number of nodes with
        # `alphabet_size` leaves in a complete binary tree.
        self.current_node_num = alphabet_size * 2 - 1

        self.all_nodes = list()
        self.tree = Tree(
            0, self.current_node_num,
            data=NYT, nodes=self.all_nodes, is_root=True
        )
        self.nyt = self.tree  # initialize the NYT node tracker

    def encode(self):
        progressbar = Bar('encoding', max=len(self.byte_seq),
                          suffix='%(index)d/%(max)d\t%(elapsed_td)ss')
        ret = bitarray(endian=sys.byteorder)
        for symbol in self.byte_seq:
            result = self.tree.search(symbol)
            if result['first_appearance']:
                ret.extend(result['code'])  # send code of NYT
                ret.frombytes(bytes([symbol]))  # send fixed code of symbol
            else:
                # send code which is path from root to the node of symbol
                ret.extend(result['code'])
            self.update(symbol, result['first_appearance'])
            progressbar.next()
        progressbar.finish()
        return ret

    def decode(self):
        pass

    def update(self, symbol, first_appearance):
        current_node = None
        while True:
            if first_appearance:
                current_node = self.nyt
                self.current_node_num -= 1
                current_node.right = Tree(
                    1, self.current_node_num, data=symbol)
                self.current_node_num -= 1
                current_node.left = Tree(
                    0, self.current_node_num, data=NYT)
                current_node.weight += 1
                current_node.data = None
                self.nyt = current_node.left
            else:
                if not current_node:
                    # first time as `current_node` is None
                    current_node = self.find_node_data(symbol)
                node_max_num_in_block = max((
                    n for n in self.all_nodes
                    if n.weight == current_node.weight),
                    key=operator.attrgetter('num'))
                if (current_node != node_max_num_in_block
                        and node_max_num_in_block != current_node.parent):
                    current_node = node_max_num_in_block
                current_node.weight += 1
            if not current_node.parent:
                break
            current_node = current_node.parent
            first_appearance = False
            # self.tree.search(-1)  # TODO: only for testing

    def find_node_data(self, data):
        for node in self.all_nodes:
            if node.data == data:
                return node
        raise KeyError('Cannot find such node containing the data %s' % data)
