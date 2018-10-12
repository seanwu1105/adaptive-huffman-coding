import logging
import sys

from bitarray import bitarray
import numpy as np

from adaptive_huffman.tree import Tree, NYT, exchange


logging.basicConfig(
    level=logging.INFO
)


class AdaptiveHuffman:
    def __init__(self, filename, alphabet_size):
        with open(filename, 'rb') as raw:
            self.dataflow = np.fromfile(raw, dtype=np.uint8)
        self.alphabet_size = alphabet_size

        # Initialize the current node # as the maximum number of nodes with
        # `alphabet_size` leaves in a complete binary tree.
        self.current_node_num = alphabet_size * 2 - 1

        self.all_nodes = set()
        self.tree = Tree(
            0, self.current_node_num,
            data=NYT, nodes=self.all_nodes, is_root=True
        )
        # self.tree.left = Tree(0, 1, data='a')
        # self.tree.left.left = Tree(0, 1, data='b')
        # self.tree.left.right = Tree(0, 1, data='c')
        # self.tree.right = Tree(0, 1, data='d')
        # self.tree.right.left = Tree(0, 1, data='e')
        # self.tree.right.right = Tree(0, 1, data='f')
        # print(self.tree.search('f'))
        # print(self.tree.pretty())

    def encode(self):
        ret = bitarray(endian=sys.byteorder)
        for symbol in self.dataflow:
            print(symbol)
            result = self.tree.search(symbol)
            if result['first_appearance']:
                ret.extend(result['code'])
                ret.frombytes(symbol.tobytes())
            else:
                # code is path from root to the node
                ret.extend(result['code'])
            self.update(symbol, result['first_appearance'])
            print('ret', ret)
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
                current_node.right = Tree(
                    1, self.current_node_num, data=symbol)
                self.current_node_num -= 1
                current_node.left = Tree(
                    0, self.current_node_num, data=NYT)
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
        self.tree.search(-1)
        print(self.tree.pretty())
        print(self.all_nodes)


def show_raw_img(img, size=(512, 512)):
    from matplotlib import pyplot as plt
    img.shape = size
    plt.imshow(img, cmap='gray')
    plt.show()


if __name__ == '__main__':
    print('result: %s' % AdaptiveHuffman('temp.raw', 256).encode())
