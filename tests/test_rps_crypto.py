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

from src.silabs_rps.rps_crypto import *

TEST_FILE_DIR = "tests/testfiles/crypto/"

KEY = b"\xf4\x45\x82\xed\x3d\xc7\x28\xbb\xce\x5e\xc4\xfc\x09\xf3\x74\xe7\xce\x5e\xc4\xfc\x09\xf3\x74\xe7\xf4\x45\x82\xed\x3d\xc7\xbb\x28"
PRIVATE_KEY = b"-----BEGIN EC PRIVATE KEY-----\nMHcCAQEEIH1tt38O7uHq/l1T5O3OwPOTo0UdoVS4qYxSZ8ZEHF3MoAoGCCqGSM49AwEHoUQDQgAEXBIYB8S0dAiYOkspCD7fennWEV0tQE8JuAkAjjob8FXsJuphJZe1Vf18F/0TXCVy/lyM6P9IVtFuQj/kDEtsyw==\n-----END EC PRIVATE KEY-----"

class TestHelpers(unittest.TestCase):

    def test_calculate_mic_default_iv(self):
        expected_mic = b"\x65\x58\x87\x83\x59\xD5\x58\x0C\x22\x27\x13\x3E\xED\x47\x41\x47"
        with open(os.path.join(TEST_FILE_DIR, "dummy-without-mic.rps"), "rb") as f:
            data = f.read()

        self.assertEqual(calculate_mic(data, KEY), expected_mic)

    def test_calculate_mic_custom_iv(self):
        expected_mic = b"\xaa\x10\xf2\x2c\xd6\x5d\x08\x77\x3a\x82\x7b\x24\x2d\xe4\xfe\x2a"
        with open(os.path.join(TEST_FILE_DIR, "dummy-without-mic.rps"), "rb") as f:
            data = f.read()

        with open(os.path.join(TEST_FILE_DIR, "iv-custom.bin"), "rb") as f:
            iv = f.read()

        self.assertEqual(calculate_mic(data, KEY, iv), expected_mic)

    def test_encrypt(self):
        with open(os.path.join(TEST_FILE_DIR, "dummy-encrypted.rps"), "rb") as f:
            expected_encrypted_data = f.read()

        with open(os.path.join(TEST_FILE_DIR, "dummy-unencrypted.rps"), "rb") as f:
            data = f.read()

        self.assertEqual(encrypt(data, KEY), expected_encrypted_data)

    def test_sign(self):
        with open(os.path.join(TEST_FILE_DIR, "dummy-signed.rps"), "rb") as f:
            data = f.read()
            unsigned_data      = data[:-72]
            expected_signature = data[-72:]

        self.assertEqual(sign(unsigned_data, PRIVATE_KEY, 256), expected_signature)


if __name__ == "__main__":
    unittest.main()
