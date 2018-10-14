import os
import logging

from adaptive_huffman.ada_huffman import AdaptiveHuffman


logging.basicConfig(level=logging.INFO)


def main():
    compress('Lena.raw', 'compressed', alphabet_range=(0, 255))
    extract('compressed', 'extract.raw', alphabet_range=(0, 255))
    show_raw_img('extract.raw', size=(512, 512))


def compress(in_filename, out_filename, alphabet_range):
    with open(in_filename, 'rb') as in_file:
        content = in_file.read()
        logging.getLogger(__name__).info('original size: %d bytes' %
                                         os.path.getsize(in_file.name))
    ada_huff = AdaptiveHuffman(content, alphabet_range)
    code = ada_huff.encode()

    with open(out_filename, 'wb') as out_file:
        code.tofile(out_file)
    logging.getLogger(__name__).info('compressed size: %d bytes' %
                                     os.path.getsize(out_filename))


def extract(in_filename, out_filename, alphabet_range):
    with open(in_filename, 'rb') as in_file:
        content = in_file.read()
        logging.getLogger(__name__).info('original size: %d bytes' %
                                         os.path.getsize(in_file.name))
    ada_huff = AdaptiveHuffman(content, alphabet_range)
    code = ada_huff.decode()

    with open(out_filename, 'wb') as out_file:
        out_file.write(bytearray(code))
    logging.getLogger(__name__).info('extract size: %d bytes' %
                                     os.path.getsize(out_filename))


def show_raw_img(img_filename, size):
    from matplotlib import pyplot as plt
    import numpy as np

    with open(img_filename, 'rb') as img_file:
        img = np.fromfile(img_file, dtype=np.uint8)
    img.shape = size
    plt.imshow(img, cmap='gray')
    plt.show()


if __name__ == '__main__':
    main()
