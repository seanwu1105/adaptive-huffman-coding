import filecmp
import os
import logging
import unittest

from adaptive_huffman_coding import __version__, compress, extract

logging.basicConfig(level=logging.DEBUG)


def test_version():
    assert __version__ == '0.1.0'


class TestCompressionAndExtraction(unittest.TestCase):
    in_filenames = (
        'tests/images/simple.raw',
        'tests/images/Lena.raw',
        'tests/images/Baboon.raw'
    )
    compressed_filename = 'compressed'
    extracted_filename = 'extracted.raw'

    def test_compress_and_extract(self, dpcm=False):
        for filename in self.in_filenames:
            alphabet_range = (0, 255)
            compress(filename, self.compressed_filename,
                     alphabet_range=alphabet_range, dpcm=dpcm)
            extract(self.compressed_filename, self.extracted_filename,
                    alphabet_range=alphabet_range, dpcm=dpcm)
            if os.path.getsize(filename) > 10000:
                self.assertTrue(os.path.getsize(
                    self.compressed_filename) < os.path.getsize(filename))
            self.assertTrue(filecmp.cmp(filename, self.extracted_filename))

    def test_compress_and_extract_dpcm(self):
        self.test_compress_and_extract(dpcm=True)
