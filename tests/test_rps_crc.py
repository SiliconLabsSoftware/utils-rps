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

from src.silabs_rps.rps_crc import crc32

TEST_FILE_DIR = "tests/testfiles/crc/"

class TestHelpers(unittest.TestCase):

    def test_crc32(self):
        expected_crc = 0xA4A3ADFD
        with open(os.path.join(TEST_FILE_DIR, "app-no-crc.rps"), "rb") as f:
            data = f.read()
        self.assertEqual(crc32(data), expected_crc)

if __name__ == "__main__":
    unittest.main()
