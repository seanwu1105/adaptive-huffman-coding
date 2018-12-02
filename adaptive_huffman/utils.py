import collections
import itertools
import math

from matplotlib import pyplot as plt
import numpy as np


def show_raw_img(original_filename, extracted_filename, size):
    with open(original_filename, 'rb') as img_file:
        original_img = np.fromfile(img_file, dtype=np.uint8)
    with open(extracted_filename, 'rb') as img_file:
        extracted_img = np.fromfile(img_file, dtype=np.uint8)
    original_img.shape = extracted_img.shape = size
    _, axarr = plt.subplots(1, 2)
    axarr[0].set_title('Original')
    axarr[0].imshow(original_img, cmap='gray')
    axarr[1].set_title('After Compression and Extraction')
    axarr[1].imshow(extracted_img, cmap='gray')
    plt.show()


def encode_dpcm(seq):
    return (
        (item - seq[idx - 1]) & 0xff if idx else item
        for idx, item in enumerate(seq)
    )


def decode_dpcm(seq):
    return itertools.accumulate(seq, lambda x, y: (x + y) & 0xff)


def bin_str2bool_list(s):
    return [c == '1' for c in s]


def bool_list2bin_str(l):
    return ''.join('1' if i else '0' for i in l)


def bool_list2int(l):
    return sum(v << i for i, v in enumerate(reversed(l)))


def entropy(byte_seq):
    counter = collections.Counter(byte_seq)
    ret = 0
    for count in counter.values():
        prob = count / sum(counter.values())
        ret += prob * math.log2(prob)
    return -ret
