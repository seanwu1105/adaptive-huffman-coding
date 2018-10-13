import logging
import sys

from bitarray import bitarray
import numpy as np

from .tree import Tree, NYT, exchange


logging.basicConfig(
    level=logging.DEBUG,
    filename='debug.log',
    filemode='w'
)


class AdaptiveHuffman:
    def __init__(self, byte_seq, alphabet_size):
        self.byte_seq = byte_seq
        self.alphabet_size = alphabet_size

        # Initialize the current node # as the maximum number of nodes with
        # `alphabet_size` leaves in a complete binary tree.
        self.current_node_num = alphabet_size * 2 - 1

        self.all_nodes = set()
        self.tree = Tree(
            0, self.current_node_num,
            data=NYT, nodes=self.all_nodes, is_root=True
        )
        # self.tree.left = Tree(0, 1, data='a')
        # self.tree.left.left = Tree(0, 1, data='b')
        # self.tree.left.right = Tree(0, 1, data='c')
        # self.tree.right = Tree(0, 1, data='d')
        # self.tree.right.left = Tree(0, 1, data='e')
        # self.tree.right.right = Tree(0, 1, data='f')
        # print(self.tree.search('f'))
        # print(self.tree.pretty())

    def encode(self):
        ret = bitarray(endian=sys.byteorder)
        for symbol in self.byte_seq:
            result = self.tree.search(symbol)
            if result['first_appearance']:
                ret.extend(result['code'])
                ret.frombytes(bytes([symbol]))
            else:
                # code is path from root to the node
                ret.extend(result['code'])
            self.update(symbol, result['first_appearance'])
            logging.getLogger(__name__).debug(
                'new symbol(%s) encoded: %s' % (symbol, ret))
            logging.getLogger(__name__).debug('tree:\n%s' % self.tree.pretty())
        return ret

    def decode(self):
        pass

    def update(self, symbol, first_appearance):
        current_node = None
        while True:
            if first_appearance:
                current_node = next(
                    filter(lambda n: n.data == NYT, self.all_nodes))
                self.current_node_num -= 1
                current_node.right = Tree(
                    1, self.current_node_num, data=symbol)
                self.current_node_num -= 1
                current_node.left = Tree(
                    0, self.current_node_num, data=NYT)
                current_node.weight += 1
                current_node.data = None
            else:
                if not current_node:
                    # first time as `current_node` is None
                    current_node = next(
                        filter(lambda n: n.data == symbol, self.all_nodes))
                node_max_num_in_block = max(filter(
                    lambda n: n.weight == current_node.weight, self.all_nodes),
                    key=lambda n: n.num)
                if (current_node != node_max_num_in_block
                        and node_max_num_in_block != current_node.parent):
                    logging.getLogger(__name__).debug(
                        'switch required. curr_node: %s, max_node: %s' % (
                            current_node, node_max_num_in_block))
                    logging.getLogger(__name__).debug(
                        'curr_node.parent: %s, max_node.left: %s, max_node.right: %s' % (
                            current_node.parent, node_max_num_in_block.left, node_max_num_in_block.right))
                    try:
                        logging.getLogger(__name__).debug('#505.parent: %s' % next(
                            filter(lambda n: n.num == 505, self.all_nodes)).parent)
                    except:
                        pass
                    logging.getLogger(__name__).debug(
                        '--- Before (total ln %s)\n%s' % (self.tree.pretty().count('\n'), self.tree.pretty()))
                    exchange(current_node, node_max_num_in_block)
                    try:
                        logging.getLogger(__name__).debug('#505.parent: %s' % next(
                            filter(lambda n: n.num == 505, self.all_nodes)).parent)
                    except:
                        pass
                    logging.getLogger(__name__).debug(
                        '--- After (total ln %s)\n%s' % (self.tree.pretty().count('\n'), self.tree.pretty()))
                    current_node = node_max_num_in_block
                current_node.weight += 1
            if not current_node.parent:
                break
            current_node = current_node.parent
            first_appearance = False
            try:
                self.tree.search(-1)  # TODO: only for testing
            except UnboundLocalError:
                logging.getLogger(__name__).debug('--- error occurred ---')
                logging.getLogger(__name__).debug('symbol: %s' % symbol)
                logging.getLogger(__name__).debug(self.tree.pretty())
                raise SystemExit
