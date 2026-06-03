"""
License
Copyright 2026 Silicon Laboratories Inc. www.silabs.com
*******************************************************************************
The licensor of this software is Silicon Laboratories Inc. Your use of this
software is governed by the terms of Silicon Labs Master Software License
Agreement (MSLA) available at
www.silabs.com/about-us/legal/master-software-license-agreement. This
software is distributed to you in Source Code format and is governed by the
sections of the MSLA applicable to Source Code.
*******************************************************************************
"""

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

    def test_checksum_empty_data(self):
        # Empty input short-circuits and returns the initial sum value (1)
        self.assertEqual(checksum(b""), 1)

    def test_checksum_unaligned_data(self):
        # Inputs whose length is not a multiple of 4 exercise the trailing-bytes branch
        self.assertEqual(checksum(b"\x01"), 0xFFFFFFFD)
        self.assertEqual(checksum(b"\x01\x02\x03"), 0xFFFCFDFD)
        self.assertEqual(checksum(b"\x01\x02\x03\x04\x05"), 0xFBFCFDFC)

    def test_checksum_unaligned_data_with_carry(self):
        # First chunk drives the running sum to 0xFFFFFF80 so that adding the
        # final 0xFF byte overflows and exercises the carry branch
        self.assertEqual(checksum(b"\x80\xfe\xff\xff\xff\x00\x00\x00\x00"), 0xFFFFFF7F)


if __name__ == "__main__":
    unittest.main()
