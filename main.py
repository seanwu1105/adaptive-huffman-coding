import logging

from matplotlib import pyplot as plt
import numpy as np


logging.basicConfig(
    level=logging.INFO
)


# Use a list to store all nodes in order to search the same weight nodes (block)
# iteratively which would be faster than recursive traversal of a tree.


class Node:
    def __init__(self, weight, left=None, right=None, data=None):
        self.weight = weight
        self.left = left
        self.right = right
        self.data = data


class AdaptiveHuffman:
    def __init__(self, filename):
        self.image = np.fromfile(open(filename, 'rb'), dtype=np.uint8)


def show_raw_img(img, size=(512, 512)):
    img.shape = size
    plt.imshow(img, cmap='gray')
    plt.show()

if __name__ == '__main__':
    AdaptiveHuffman('Lena.raw')
