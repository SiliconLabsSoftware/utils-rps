"""
License
Copyright 2025 Silicon Laboratories Inc. www.silabs.com
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


if __name__ == "__main__":
    unittest.main()
