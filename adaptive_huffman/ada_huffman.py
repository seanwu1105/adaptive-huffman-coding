import operator
import sys

from bitarray import bitarray
from progress.bar import ShadyBar
import numpy as np

from .tree import Tree, NYT, exchange


class AdaptiveHuffman:
    def __init__(self, byte_seq, alphabet_range):
        """Create an adaptive huffman encoder and decoder.

        Args:
            byte_seq (bytes): The bytes sequence to encode or decode.
            alphabet_range (tuple or integer): The range of alphabet
                inclusively.
        """

        self.byte_seq = byte_seq
        # Get the first decimal number of all alphabets
        self.alphabet_first_num = min(alphabet_range)
        alphabet_size = abs(alphabet_range[0] - alphabet_range[1]) + 1
        # Select an `exp` and `rem` which meet `alphabet_size = 2**exp + rem`.
        # Get the largest `exp` smaller than `alphabet_size`.
        self.exp = alphabet_size.bit_length() - 1
        self.rem = alphabet_size - 2**self.exp

        # Initialize the current node # as the maximum number of nodes with
        # `alphabet_size` leaves in a complete binary tree.
        self.current_node_num = alphabet_size * 2 - 1

        self.tree = Tree(0, self.current_node_num, data=NYT)
        self.all_nodes = [self.tree]
        self.nyt = self.tree  # initialize the NYT reference

    def encode(self):
        progressbar = ShadyBar('encoding', max=len(self.byte_seq),
                               suffix='%(percent).1f%% - %(elapsed_td)ss')
        ret = bitarray(endian=sys.byteorder)
        for symbol in self.byte_seq:
            fixed_code = self.to_fixed_code(symbol)
            result = self.tree.search(fixed_code)
            if result['first_appearance']:
                ret.extend(result['code'])  # send code of NYT
                ret.extend(fixed_code)  # send fixed code of symbol
            else:
                # send code which is path from root to the node of symbol
                ret.extend(result['code'])
            self.update(fixed_code, result['first_appearance'])
            progressbar.next()
        print(self.tree.pretty())
        progressbar.finish()
        return ret

    def decode(self):

        def read_bit(n):
            bits = bit_seq[:n]
            del bit_seq[:n]
            return bits

        bit_seq = bitarray(endian=sys.byteorder)
        bit_seq.frombytes(self.byte_seq)
        ret = []
        while bit_seq:
            print('bef', bit_seq)
            current_node = self.tree  # go to root
            while current_node.left or current_node.right:
                bit = read_bit(1)[0]
                print('bit', bit)
                current_node = current_node.right if bit else current_node.left
                if current_node is None:
                    raise ValueError('decoding fatal error: current_node should'
                                     ' never be None.')
            print('aft', bit_seq)
            print('curr', current_node)
            if current_node.data == NYT:
                print('NEW')
                first_appearance = True
                # Convert fixed code into integer
                bits = read_bit(self.exp)
                dec = ord(bits.tobytes())
                if dec < self.rem:
                    bits.extend(read_bit(1))
                    dec = ord(bits.tobytes())
                else:
                    dec += self.rem
                dec += 1 + (self.alphabet_first_num - 1)
                if dec < 0 or dec >= 256:
                    raise ValueError('decoding fatal error: decoded integer '
                                     'must be in range[0, 256).')
                print('send', chr(dec))
                ret.append(dec)
            else:
                print('OLD')
                # decode element corresponding to node
                first_appearance = False
                print('send', chr(current_node.data))
                ret.append(current_node.data)
            self.update(dec, first_appearance)
            print('end', bit_seq)
            print(self.tree.pretty())
            # input()
        return ret

    def update(self, data, first_appearance):

        def find_node_data(data):
            for node in self.all_nodes:
                if node.data == data:
                    return node
            raise KeyError(
                'Cannot find the target node with given data %s' % data)

        current_node = None
        while True:
            if first_appearance:
                current_node = self.nyt

                self.current_node_num -= 1
                new_external = Tree(1, self.current_node_num, data=data)
                current_node.right = new_external
                self.all_nodes.append(new_external)

                self.current_node_num -= 1
                self.nyt = Tree(0, self.current_node_num, data=NYT)
                current_node.left = self.nyt
                self.all_nodes.append(self.nyt)

                current_node.weight += 1
                current_node.data = None
                self.nyt = current_node.left
            else:
                if not current_node:
                    # First time as `current_node` is None.
                    current_node = find_node_data(data)
                node_max_num_in_block = max(
                    (n for n in self.all_nodes if n.weight == current_node.weight),
                    key=operator.attrgetter('num'))
                if (current_node != node_max_num_in_block
                        and node_max_num_in_block != current_node.parent):
                    exchange(current_node, node_max_num_in_block)
                    current_node = node_max_num_in_block
                current_node.weight += 1
            if not current_node.parent:
                break
            current_node = current_node.parent
            first_appearance = False

    def to_fixed_code(self, dec):
        alphabet_idx = dec - (self.alphabet_first_num - 1)
        ret = bitarray(endian=sys.byteorder)
        if alphabet_idx <= 2 * self.rem:
            ret.frombytes(int2bytes(alphabet_idx - 1))
            return ret[:self.exp + 1] if sys.byteorder == 'little' else ret[-(self.exp + 1):]
        ret.frombytes(int2bytes(alphabet_idx - self.rem - 1))
        return ret[:self.exp] if sys.byteorder == 'little' else ret[-(self.exp):]


def int2bytes(x):
    # NOTE: Do NOT use int.to_byte() directly. Use this function instead.
    if x == 0:
        return b'\x00'
    return x.to_bytes((x.bit_length() + 7) // 8, sys.byteorder)
