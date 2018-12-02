import logging
import operator
import os

from bitarray import bitarray, bits2bytes
from progress.bar import ShadyBar

from .tree import Tree, NYT, exchange
from .utils import (encode_dpcm, decode_dpcm, bin_str2bool_list,
                    bool_list2bin_str, bool_list2int, entropy)


class AdaptiveHuffman:
    def __init__(self, byte_seq, alphabet_range=(0, 255), dpcm=False):
        """Create an adaptive huffman encoder and decoder.

        Args:
            byte_seq (bytes): The bytes sequence to encode or decode.
            alphabet_range (tuple or integer): The range of alphabet
                inclusively.
        """

        self.byte_seq = byte_seq
        self._bits = None  # Only used in decode().
        self.dpcm = dpcm

        # Get the first decimal number of all alphabets
        self._alphabet_first_num = min(alphabet_range)
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

    @profile
    def encode(self):
        """Encode the target byte sequence into compressed bit sequence by
        adaptive Huffman coding.

        Returns:
            bitarray: The compressed bitarray. Use `bitarray.tofile()` to save
                to file.
        """

        def encode_fixed_code(dec):
            """Convert a decimal number into specified fixed code.

            Arguments:
                dec {int} -- The alphabet need to be converted into fixed code.

            Returns:
                list of bool -- Fixed codes.
            """

            alphabet_idx = dec - (self._alphabet_first_num - 1)
            if alphabet_idx <= 2 * self.rem:
                fixed_str = '{:0{padding}b}'.format(
                    alphabet_idx - 1,
                    padding=self.exp + 1
                )
            else:
                fixed_str = '{:0{padding}b}'.format(
                    alphabet_idx - self.rem - 1,
                    padding=self.exp
                )
            return bin_str2bool_list(fixed_str)

        progressbar = ShadyBar(
            'encoding',
            max=len(self.byte_seq),
            suffix='%(percent).1f%% - %(elapsed_td)ss'
        )

        if self.dpcm:
            self.byte_seq = tuple(encode_dpcm(self.byte_seq))

        logging.getLogger(__name__).info(
            'entropy: %f' % entropy(self.byte_seq)
        )

        code = []
        for symbol in self.byte_seq:
            fixed_code = encode_fixed_code(symbol)
            result = self.tree.search(fixed_code)
            if result['first_appearance']:
                code.extend(result['code'])  # send code of NYT
                code.extend(fixed_code)  # send fixed code of symbol
            else:
                # send code which is path from root to the node of symbol
                code.extend(result['code'])
            self.update(fixed_code, result['first_appearance'])
            progressbar.next()

        # Add remaining bits length info at the beginning of the code in order
        # to avoid the decoder regarding the remaining bits as actual data. The
        # remaining bits length info require 3 bits to store the length. Note
        # that the first 3 bits are stored as big endian binary string.
        remaining_bits_length = (
            bits2bytes(len(code) + 3) * 8 - (len(code) + 3)
        )
        code = (bin_str2bool_list('{:03b}'.format(remaining_bits_length))
                + code)

        progressbar.finish()
        return bitarray(code)

    @profile
    def decode(self):
        """Decode the target byte sequence which is encoded by adaptive Huffman
        coding.

        Returns:
            list: A list of integer representing the number of decoded byte
                sequence.
        """

        def pop_bits(n):
            progressbar.next(n)
            ret, self._bits = self._bits[:n], self._bits[n:]
            return ret

        def decode_fixed_code():
            fixed_code = pop_bits(self.exp)
            integer = bool_list2int(fixed_code)
            if integer < self.rem:
                fixed_code.extend(pop_bits(1))
                integer = bool_list2int(fixed_code)
            else:
                integer += self.rem
            return integer + 1 + (self._alphabet_first_num - 1)

        # Get boolean list ([True, False, ...]) from bytes.
        self._bits = bitarray()
        self._bits.frombytes(self.byte_seq)
        self._bits = self._bits.tolist()

        progressbar = ShadyBar(
            'decoding',
            max=len(self._bits),
            suffix='%(percent).1f%% - %(elapsed_td)ss'
        )

        # Remove the remaining bits in the last of bit sequence generated by
        # bitarray.tofile() to fill up to complete byte size (8 bits). The
        # remaining bits length could be retrieved by reading the first 3 bits.
        # Note that the first 3 bits are stored as big endian binary string.
        remaining_bits_length = bool_list2int(pop_bits(3))
        if remaining_bits_length:
            del self._bits[-remaining_bits_length:]
            progressbar.next(remaining_bits_length)

        code = []
        while self._bits:
            current_node = self.tree  # go to root
            while current_node.left or current_node.right:
                bit = pop_bits(1)[0]
                current_node = current_node.right if bit else current_node.left
            if current_node.data == NYT:
                first_appearance = True
                dec = decode_fixed_code()
                code.append(dec)
            else:
                # decode element corresponding to node
                first_appearance = False
                dec = current_node.data
                code.append(current_node.data)
            self.update(dec, first_appearance)

        progressbar.finish()
        return decode_dpcm(code) if self.dpcm else code

    def update(self, data, first_appearance):

        def find_node_data(data):
            for node in self.all_nodes:
                if node.data == data:
                    return node
            raise KeyError(f'Cannot find the target node given {data}.')

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
                    (
                        n for n in self.all_nodes
                        if n.weight == current_node.weight
                    ),
                    key=operator.attrgetter('num')
                )
                if (current_node != node_max_num_in_block and
                        node_max_num_in_block != current_node.parent):
                    exchange(current_node, node_max_num_in_block)
                    current_node = node_max_num_in_block
                current_node.weight += 1
            if not current_node.parent:
                break
            current_node = current_node.parent
            first_appearance = False


def compress(in_filename, out_filename, alphabet_range, dpcm):
    with open(in_filename, 'rb') as in_file:
        logging.getLogger(__name__).info(f'open file: "{in_filename}"')
        content = in_file.read()
        logging.getLogger(__name__).info('original size: '
                                         f'{os.path.getsize(in_file.name)} '
                                         'bytes')
    ada_huff = AdaptiveHuffman(content, alphabet_range, dpcm)
    code = ada_huff.encode()

    with open(out_filename, 'wb') as out_file:
        logging.getLogger(__name__).info(f'write file: "{out_filename}"')
        code.tofile(out_file)
    logging.getLogger(__name__).info('compressed size: '
                                     f'{os.path.getsize(out_filename)} bytes')


def extract(in_filename, out_filename, alphabet_range, dpcm):
    with open(in_filename, 'rb') as in_file:
        logging.getLogger(__name__).info(f'open file: "{in_filename}"')
        content = in_file.read()
        logging.getLogger(__name__).info('original size: '
                                         f'{os.path.getsize(in_file.name)} '
                                         'bytes')
    ada_huff = AdaptiveHuffman(content, alphabet_range, dpcm)
    code = ada_huff.decode()

    with open(out_filename, 'wb') as out_file:
        logging.getLogger(__name__).info(f'write file: "{out_filename}"')
        out_file.write(bytes(code))
    logging.getLogger(__name__).info('extract size: '
                                     f'{os.path.getsize(out_filename)} bytes')
