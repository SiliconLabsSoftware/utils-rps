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

from src.silabs_rps.rps_helpers import *

TEST_FILE_DIR = "tests/testfiles/helpers/"

class TestHelpers(unittest.TestCase):

    def test_parse_int(self):
        self.assertEqual(parse_int("1234"), 1234)
        self.assertEqual(parse_int("0x1234"), 0x1234)

    def test_is_hex_file(self):
        self.assertTrue(is_hex_file("file.hex"))
        self.assertFalse(is_hex_file("file.bin"))

    def test_check_hex_file_sane_size(self):
        self.assertTrue(check_hex_file_sane_size(os.path.join(TEST_FILE_DIR, "dummy.hex"), 20000))
        self.assertFalse(check_hex_file_sane_size(os.path.join(TEST_FILE_DIR, "dummy.hex"),  100))

    def test_read_hex_file(self):
        segments, data = read_hex_file(os.path.join(TEST_FILE_DIR, "dummy.hex"))
        self.assertEqual(segments, [(0x08212000, 0x08212000 + 14556)])

        with open(os.path.join(TEST_FILE_DIR, "dummy.bin"), "rb") as f:
            self.assertEqual(data, f.read())

    def test_is_txt_file(self):
        self.assertTrue(is_txt_file("file.txt"))
        self.assertFalse(is_txt_file("file.bin"))

    def test_read_txt_file_key(self):
        expectedKey = bytes.fromhex("3a1694d90f43848365866ebf388d413b")
        self.assertEqual(read_txt_file_key(os.path.join(TEST_FILE_DIR, "key.txt")), expectedKey)

    def test_is_bin_file(self):
        self.assertTrue(is_bin_file("file.bin"))
        self.assertFalse(is_bin_file("file.hex"))
        self.assertFalse(is_bin_file("file.txt"))

    def test_read_bin_file_key(self):
        expectedKey = bytes.fromhex("9afbdf77894c20b74093f5ed9202aaca")
        self.assertEqual(read_bin_file_key(os.path.join(TEST_FILE_DIR, "key.bin")), expectedKey)

    def test_is_pem_file(self):
        self.assertTrue(is_pem_file("file.pem"))
        self.assertFalse(is_pem_file("file.bin"))
        self.assertFalse(is_pem_file("file.der"))

    def test_read_pem_file_key(self):
        expectedKey = b"-----BEGIN EC PRIVATE KEY-----\nMHcCAQEEIH1tt38O7uHq/l1T5O3OwPOTo0UdoVS4qYxSZ8ZEHF3MoAoGCCqGSM49\nAwEHoUQDQgAEXBIYB8S0dAiYOkspCD7fennWEV0tQE8JuAkAjjob8FXsJuphJZe1\nVf18F/0TXCVy/lyM6P9IVtFuQj/kDEtsyw==\n-----END EC PRIVATE KEY-----\n"
        self.assertEqual(read_pem_file_key(os.path.join(TEST_FILE_DIR, "key.pem")), expectedKey)

    def test_is_der_file(self):
        self.assertTrue(is_der_file("file.der"))
        self.assertFalse(is_der_file("file.bin"))
        self.assertFalse(is_der_file("file.pem"))

    def test_read_der_file_key(self):
        expectedKey = bytes.fromhex("3059301306072a8648ce3d020106082a8648ce3d03010703420004004ecccdaf0167e579b75c7c6384f8530f358f28c6e1731dca80013ff672059dc791236b34f2cab42ec111c7f730ae49ff81fdfe5e7cad341ed76dfd0906f070")
        self.assertEqual(read_der_file_key(os.path.join(TEST_FILE_DIR, "key.der")), expectedKey)

    def test_is_map_file(self):
        self.assertTrue(is_map_file("file.map"))
        self.assertFalse(is_map_file("file.bin"))

    def test_get_flash_start_address_from_map_file(self):
        self.assertEqual(get_flash_start_address_from_map_file(os.path.join(TEST_FILE_DIR, "mapfile.map")), 0x08212000)

    def test_get_flash_start_address_from_map_file_invalid_file(self):
        self.assertEqual(get_flash_start_address_from_map_file(os.path.join(TEST_FILE_DIR, "mapfile-invalid.map")), 0xFFFFFFFF)


if __name__ == "__main__":
    unittest.main()
