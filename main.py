import os
import logging

from adaptive_huffman.ada_huffman import AdaptiveHuffman


<<<<<<< HEAD
logging.basicConfig(level=logging.INFO)


def main():
    with open('Baboon.raw', 'rb') as in_raw:
        content = in_raw.read()
        logging.getLogger(__name__).info('original size: %d bytes' %
                                         os.path.getsize(in_raw.name))
    ada_huff = AdaptiveHuffman(content, (0, 255))
    code = ada_huff.encode()

    out_filename = 'compressed.raw'
    with open(out_filename, 'wb') as out_raw:
        code.tofile(out_raw)
    logging.getLogger(__name__).info('compressed size: %d bytes' %
                                     os.path.getsize(out_filename))
    
    # XXX: decoder should be a new AdaptiveHuffman() object!

    ada_huff.tree.search(-1) # only for debugging
    logging.getLogger(__name__).debug('tree:\n%s' % ada_huff.tree.pretty())
=======
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
>>>>>>> master


def show_raw_img(img, size=(512, 512)):
    from matplotlib import pyplot as plt
    img.shape = size
    plt.imshow(img, cmap='gray')
    plt.show()


if __name__ == '__main__':
    main()
