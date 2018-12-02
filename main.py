import logging

from adaptive_huffman import compress, extract
from adaptive_huffman.utils import show_raw_img


logging.basicConfig(level=logging.INFO)


def main():
    # for fn in ('tests/images/Lena.raw', 'tests/images/Baboon.raw'):
    for fn in ('tests/images/simple.raw', ):
        alphabet_range = (0, 255)
        dpcm = False
        compress(fn, 'compressed', alphabet_range=alphabet_range, dpcm=dpcm)
        extract('compressed', 'extracted.raw',
                alphabet_range=alphabet_range, dpcm=dpcm)
        # show_raw_img(fn, 'extracted.raw', size=(512, 512))


if __name__ == '__main__':
    main()
