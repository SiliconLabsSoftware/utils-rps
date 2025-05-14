import unittest
import os

from ctypes import c_uint32

from src.silabs_rps.rps_crc import crc32, _reflect

TEST_FILE_DIR = "tests/testfiles/crc/"

class TestHelpers(unittest.TestCase):

    def test_crc32(self):
        expected_crc = 0xA4A3ADFD
        with open(os.path.join(TEST_FILE_DIR, "app-no-crc.rps"), "rb") as f:
            data = f.read()
        self.assertEqual(crc32(data), expected_crc)

    def test_reflect_helper(self):
        self.assertEqual(_reflect(c_uint32(0x01), 8).value, c_uint32(0x80).value)
        self.assertEqual(_reflect(c_uint32(0x80), 8).value, c_uint32(0x01).value)
        self.assertEqual(_reflect(c_uint32(0x00), 8).value, c_uint32(0x00).value)
        self.assertEqual(_reflect(c_uint32(0xFF), 8).value, c_uint32(0xFF).value)

        self.assertEqual(_reflect(c_uint32(0x00000001), 32).value, c_uint32(0x80000000).value)
        self.assertEqual(_reflect(c_uint32(0x80000000), 32).value, c_uint32(0x00000001).value)
        self.assertEqual(_reflect(c_uint32(0x00000000), 32).value, c_uint32(0x00000000).value)
        self.assertEqual(_reflect(c_uint32(0xFFFFFFFF), 32).value, c_uint32(0xFFFFFFFF).value)


if __name__ == "__main__":
    unittest.main()
