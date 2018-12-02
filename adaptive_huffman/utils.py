def encode_dpcm(seq):
    return (
        (item - seq[idx - 1]) & 0xff if idx else item
        for idx, item in enumerate(seq)
    )
