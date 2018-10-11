import logging

import numpy as np

from adaptive_huffman.tree import Tree


logging.basicConfig(
    level=logging.INFO
)


class AdaptiveHuffman:
    def __init__(self, filename):
        with open(filename, 'rb') as raw:
            self.dataflow = np.fromfile(raw, dtype=np.uint8)

        self.all_nodes = set()
        self.tree = Tree(0, 1, data=Tree.NYT, nodes=self.all_nodes, root=True)
        self.tree.left = Tree(0, 2, data='a')
        self.tree.right = Tree(0, 2, data='b')
        self.tree.left.left = Tree(0, 2, data='c')
        self.tree.left.right = Tree(0, 2, data='d')
        self.tree.right.left = Tree(0, 2, data='e')
        self.tree.right.right = Tree(0, 2, data='g')
        print(self.tree.pretty())
        self.tree.build_codes()
        print(self.tree.pretty())

    def encode(self):
        # for symbol in self.dataflow:
        #     if symbol in {node.data for node in self.all_nodes}:
        #         first_appearance = False
        #         print('old')
        #     else:
        #         first_appearance = True
        #         print('first')
        #     self.update(first_appearance)
        self.tree
        return None

    def decode(self):
        pass

    def update(self, first_appearance):
        pass


def show_raw_img(img, size=(512, 512)):
    from matplotlib import pyplot as plt
    img.shape = size
    plt.imshow(img, cmap='gray')
    plt.show()


if __name__ == '__main__':
    AdaptiveHuffman('Lena.raw').encode()
