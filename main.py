import os
import logging

from matplotlib import pyplot as plt
import numpy as np

from adaptive_huffman import compress, extract


logging.basicConfig(level=logging.INFO)


def main():
    for fn in ('tests/images/Lena.raw', 'tests/images/Baboon.raw'):
        alphabet_range = (0, 255)
        dpcm = False
        compress(fn, 'compressed', alphabet_range=alphabet_range, dpcm=dpcm)
        extract('compressed', 'extracted.raw',
                alphabet_range=alphabet_range, dpcm=dpcm)
        show_raw_img(fn, 'extracted.raw', size=(512, 512))


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


if __name__ == '__main__':
    main()
