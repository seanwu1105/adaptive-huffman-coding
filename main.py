from adaptive_huffman.ada_huffman import AdaptiveHuffman

def main():
    with open('temp.raw', 'rb') as in_raw:
        content = in_raw.read()
    ada_huff = AdaptiveHuffman(content, 256)
    print(ada_huff.encode())
    print(ada_huff.tree.pretty())
    # with open('compressed.raw', 'wb') as raw:
    #     ada_huff.encode().tofile(raw)

def show_raw_img(img, size=(512, 512)):
    from matplotlib import pyplot as plt
    img.shape = size
    plt.imshow(img, cmap='gray')
    plt.show()

if __name__ == '__main__':
    main()