import os
import logging

from adaptive_huffman.ada_huffman import AdaptiveHuffman


logging.basicConfig(
    level=logging.INFO
)


def main():
    with open('temp.raw', 'rb') as in_raw:
        content = in_raw.read()[:]
        print(len(content))
        logging.getLogger(__name__).info('original: %d bytes' %
                                         os.path.getsize(in_raw.name))
    ada_huff = AdaptiveHuffman(content, 256)
    code = ada_huff.encode()
    ada_huff.tree.search(-1)
    print(ada_huff.tree.pretty())
    outfilename = 'compressed.raw'
    with open(outfilename, 'wb') as raw:
        code.tofile(raw)
    logging.getLogger(__name__).info('compressed: %d bytes' %
                                     os.path.getsize(outfilename))


def show_raw_img(img, size=(512, 512)):
    from matplotlib import pyplot as plt
    img.shape = size
    plt.imshow(img, cmap='gray')
    plt.show()


if __name__ == '__main__':
    main()
