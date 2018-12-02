import itertools

def encode_dpcm(seq):
    return (
        (item - seq[idx - 1]) & 0xff if idx else item
        for idx, item in enumerate(seq)
    )

def decode_dpcm(seq):
    return itertools.accumulate(seq, lambda x, y: (x + y) & 0xff)

def bin_str2bool_list(s):
    return [False if c == '0' else True for c in s]

def bool_list2bin_str(l):
    return ''.join('1' if i else '0' for i in l)

def bool_list2int(l):
    return int(bool_list2bin_str(l), 2)
