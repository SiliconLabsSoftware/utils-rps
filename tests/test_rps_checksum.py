import unittest
import os

from src.silabs_rps.rps_checksum import *

TEST_FILE_DIR = "tests/testfiles/checksum/"

class TestHelpers(unittest.TestCase):
    def test_checksum(self):
        expected_checksum = 0x61317D09
        with open(os.path.join(TEST_FILE_DIR, "application_header.bin"), "rb") as f:
            data = f.read()

        self.assertEqual(checksum(data), expected_checksum)


if __name__ == "__main__":
    unittest.main()
