import sys

from bitarray import bitarray
import numpy as np

from .tree import Tree, NYT, exchange


class AdaptiveHuffman:
    def __init__(self, byte_seq, alphabet_size):
        self.byte_seq = byte_seq
        self.alphabet_size = alphabet_size

        # Initialize the current node # as the maximum number of nodes with
        # `alphabet_size` leaves in a complete binary tree.
        self.current_node_num = alphabet_size * 2 - 1

        self.tree = Tree(0, self.current_node_num, data=NYT)
        self.all_nodes = [self.tree]

    def encode(self):
        ret = bitarray(endian=sys.byteorder)
        for symbol in self.byte_seq:
            result = self.tree.search(symbol)
            if result['first_appearance']:
                ret.extend(result['code'])
                ret.frombytes(bytes([symbol]))
            else:
                # code is path from root to the node
                ret.extend(result['code'])
            self.update(symbol, result['first_appearance'])
        return ret

    def decode(self):
        pass

    def update(self, symbol, first_appearance):
        current_node = None
        while True:
            if first_appearance:
                current_node = next(
                    filter(lambda n: n.data == NYT, self.all_nodes))

                self.current_node_num -= 1
                new_external = Tree(1, self.current_node_num, data=symbol)
                current_node.right = new_external
                self.all_nodes.append(new_external)

                self.current_node_num -= 1
                new_nyt = Tree(0, self.current_node_num, data=NYT)
                current_node.left = new_nyt
                self.all_nodes.append(new_nyt)

                current_node.weight += 1
                current_node.data = None
            else:
                if not current_node:
                    # first time as `current_node` is None
                    current_node = next(
                        filter(lambda n: n.data == symbol, self.all_nodes))
                node_max_num_in_block = max(filter(
                    lambda n: n.weight == current_node.weight, self.all_nodes),
                    key=lambda n: n.num)
                if (current_node != node_max_num_in_block
                        and node_max_num_in_block != current_node.parent):
                    exchange(current_node, node_max_num_in_block)
                    current_node = node_max_num_in_block
                current_node.weight += 1
            if not current_node.parent:
                break
            current_node = current_node.parent
            first_appearance = False
            self.tree.search(-1)  # TODO: only for testing
