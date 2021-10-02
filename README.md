# Adaptive Huffman Coding Compression

[![build](https://github.com/seanwu1105/adaptive-huffman-coding/workflows/build/badge.svg)](https://github.com/seanwu1105/adaptive-huffman-coding/actions?query=workflow%3Abuild)

Adaptive Huffman coding algorithm in Python.

## Testing Files and Compressing Results

|                                         File Name                                         |  Compressed  | Compressing/Extracting Time | First-Order Entropy | Compressed File Size (DPCM) | Compressing/Extracting Time (DPCM) | First-Order Entropy (DPCM) |
|:-----------------------------------------------------------------------------------------:|:------------:|:---------------------------:|:-------------------:|:---------------------------:|:----------------------------------:|:--------------------------:|
| `Lena.raw` ![Lena.raw Preview ](https://i.imgur.com/gLSTp61.png  "Lena.raw Preview" )       | 245153 Bytes | 02:12s/01:50s               | 7.447359            | 167384 Bytes                | 01:50s/01:11s                      | 5.064970                   |
| `Baboon.raw` ![Baboon.raw Preview ](https://i.imgur.com/zDWHGXN.png  "Baboon.raw Preview" ) | 242230 Bytes | 02:15s/01:50s               | 7.357734            | 209341 Bytes                | 02:15s/01:47s                      | 6.352999                   |

## Getting Started

### Environment

* Visual Studio Code
* Poetry 1.0.10 or later

### Installation

Clone this repositroy.

``` bash
git clone https://github.com/seanwu1105/adaptive_huffman_coding
```

Open the root directory.

``` bash
cd adaptive_huffman_coding
```

Install the dependencies with Poetry.

``` bash
poetry install --no-root
```

### Uses

This project is fully written in Python 3. For data compression given specific alphabet size,

``` python
from adaptive_huffman.ada_huffman import compress

alphabet_range = (0, 255)  # from 0 to 255 inclusively
dpcm = False  # preprocess the target data with DPCM
compress(fn, 'compressed', alphabet_range=alphabet_range, dpcm=dpcm)
```

For data extraction given specific alphabet size,

``` python
from adaptive_huffman.ada_huffman import extract

alphabet_range = (0, 255)  # from 0 to 255 inclusively
dpcm = False  # postprocess the target data with DPCM
extract('compressed', 'extracted.raw', alphabet_range=alphabet_range, dpcm=dpcm)
```

You could find the demo in [`main.py`](/main.py), which will compress and extract the target data (`Lena.raw` and `Baboon.raw`) then show the original and after-processing images for comparison with Matplotlib. To run the demo in **Ubuntu 18.04**,

``` bash
python3 main.py
```

> Note that in Windows, this project requires **Visual C++ 14.0** as it requires **bitarray** module which needs C source codes compilation.

Furthermore, for simple testing (whether the file after compression and extraction is the same as the original),

``` bash
pytest
```

## Caveat

* This algorithm will read **ALL** image into memory and **ALL** encoded bits would be saved as **Python String**, and thus it is possible to cause memory overflow if the input image file is too large.
* [Details Report](https://is.gd/VMCLWw)

## Algorithm and Implementation

### Encoding Procedure

Assume the input stream is a sequence of bytes. First, if we use DPCM as symbol set, we use the following method for differentiation.

``` python
# `seq` is byte array originally. For indexing, we need to convert it into list.
seq = list(seq)
return ((item - seq[idx - 1]) & 0xff if idx else seq[idx] for idx, item in enumerate(seq))
```

Second, we convert every byte in the sequence into a fixed code by the following method:

Assume the source has an alphabet (`a[1]`, `a[2]`, ..., `a[m]`) of size `m`, then pick `e` and `r` such that `m = 2^e + r` and `0 <= r < 2^e`. We calculate `e` and `r` by the following Python codes.

``` python
# Get the largest `e` smaller than `alphabet_size`.
e = m.bit_length() - 1
r = m - 2**e
```

Let `k` to be the index of a certain alphabet. If `1 <= k <= 2r`, the symbol `a[k]` is encoded as the `(e + 1)`-bit binary representation of `k - 1`. Else, `a[k]` is encoded as `e`-bit representation of `k - r - 1`. After converting byte symbols into fixed codes, we encode the whole sequence into bit sequence by the following flowchart.

![Encoding Flowchart](https://i.imgur.com/5xzPKiO.png "Encoding Flowchart")

Finally, as the length of the bit sequence might not be a multiple of 8, the few remaining bits (1..7) are set to 0. We need to **add the length of remaining bits we filled to the head of output bit sequence** in order to notify the exact file size for decoding procedure. To implement this, we could simply insert 3-bit at the beginning of the output bit sequence to represent the length of fill-up remaining bits.

``` python
# Get the length of remaining bits.
remaining_bits_length = (bits2bytes(code.length() + 3) * 8 - (code.length() + 3))
# Insert the length information into the beginning of output sequence.
for bit in '{:03b}'.format(remaining_bits_length)[::-1]:
    code.insert(0, False if bit == '0' else True)
```

### Decoding Procedure

First, we need to get the actual file size from the first 3-bit of the input bit sequence and remove them as well as the fill-up remaining bits appending to the sequence.

``` python
# Get the actual file size and remove the information.
remaining_bits_length = int(read_bit(3).to01(), 2)
# Remove the remaining bits.
del bit_seq[-remaining_bits_length:]
```

After that, we could decode the content of the file as the following flowchart.

![Decoding Flowchart](https://i.imgur.com/x1OSKbe.png "Decoding Flowchart")

Finally, if the file is encoded with DPCM, we need to convert the content back into the real data.

``` python
# `seq` is the byte sequence of decoded data.
return itertools.accumulate(seq, lambda x, y: (x + y) & 0xff)
```

### Updating Procedure

The updating procedure used by both encoding and decoding procedure is the following flowchart.

![Update Flowchart](https://i.imgur.com/hmCA8jT.png "Update Flowchart")

### Data Structure

We use a DAG, which has 2 children and parent pointer for every node, to implement Huffman tree. The code of a node is generated when we search for it (`Tree.search()` in class `Tree` of [`tree.py`](/adaptive_huffman/tree.py)), and thus the code for every node will not be updated when exchanging or appending. Furthermore, we use an array (`self.all_nodes` in class `AdaptiveHuffman` of [`ada_huffman.py`](/adaptive_huffman/ada_huffman.py)) to keep track of each node within the tree. By doing this, we could search a node within the tree iteratively instead of recursively traversal.
