import filecmp
import os
import logging
import unittest

from adaptive_huffman.ada_huffman import compress, extract


logging.basicConfig(level=logging.DEBUG)


class TestCompressionAndExtraction(unittest.TestCase):
    in_filenames = (
        'tests/images/simple.raw',
        'tests/images/Lena.raw',
        'tests/images/Baboon.raw'
    )
    compressed_filename = 'compressed'
    extracted_filename = 'extracted.raw'

    def test_compress_and_extract(self, dpcm=False):
        for fn in self.in_filenames:
            alphabet_range = (0, 255)
            compress(fn, self.compressed_filename,
                     alphabet_range=alphabet_range, dpcm=dpcm)
            extract(self.compressed_filename, self.extracted_filename,
                    alphabet_range=alphabet_range, dpcm=dpcm)
            if os.path.getsize(fn) > 10000:
                self.assertTrue(os.path.getsize(
                    self.compressed_filename) < os.path.getsize(fn))
            self.assertTrue(filecmp.cmp(fn, self.extracted_filename))
    
    def test_compress_and_extract_dpcm(self):
        self.test_compress_and_extract(dpcm=True)
