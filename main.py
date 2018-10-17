import os
import logging

from matplotlib import pyplot as plt
import numpy as np

from adaptive_huffman.ada_huffman import AdaptiveHuffman, entropy


logging.basicConfig(level=logging.INFO)


def main():
    for fn in ('tests/images/Lena.raw', ):
        compress(fn, 'compressed', alphabet_range=(0, 255), dpcm=True)
        extract('compressed', 'extract.raw', alphabet_range=(0, 255), dpcm=True)
        show_raw_img(fn, 'extract.raw', size=(512, 512))


def compress(in_filename, out_filename, alphabet_range, dpcm):
    with open(in_filename, 'rb') as in_file:
        logging.getLogger(__name__).info('open file: "%s"' % in_filename)
        content = in_file.read()
        logging.getLogger(__name__).info('original size: %d bytes' %
                                         os.path.getsize(in_file.name))
    ada_huff = AdaptiveHuffman(content, alphabet_range, dpcm)
    logging.getLogger(__name__).info('entropy: %f' %
                                     entropy(ada_huff.byte_seq))
    code = ada_huff.encode()

    with open(out_filename, 'wb') as out_file:
        logging.getLogger(__name__).info('write file: "%s"' % out_filename)
        code.tofile(out_file)
    logging.getLogger(__name__).info('compressed size: %d bytes' %
                                     os.path.getsize(out_filename))


def extract(in_filename, out_filename, alphabet_range, dpcm):
    with open(in_filename, 'rb') as in_file:
        logging.getLogger(__name__).info('open file: "%s"' % in_filename)
        content = in_file.read()
        logging.getLogger(__name__).info('original size: %d bytes' %
                                         os.path.getsize(in_file.name))
    ada_huff = AdaptiveHuffman(content, alphabet_range, dpcm)
    code = ada_huff.decode()

    with open(out_filename, 'wb') as out_file:
        logging.getLogger(__name__).info('write file: "%s"' % out_filename)
        out_file.write(bytes(code))
    logging.getLogger(__name__).info('extract size: %d bytes' %
                                     os.path.getsize(out_filename))


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
