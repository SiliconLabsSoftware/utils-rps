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

from src.silabs_rps.rps import RPS
from src.silabs_rps.rps_consts import RPS_BOOT_DESCRIPTOR_PADDING_SIZE

class TestRPS(unittest.TestCase):

    def test_header_default_parameters(self):
        rps_header = RPS().Header()
        self.assertEqual(rps_header.is_m4_image, True)
        self.assertEqual(rps_header.is_encrypted, False)
        self.assertEqual(rps_header.mic_protected, False)
        self.assertEqual(rps_header.is_signed, False)
        self.assertEqual(rps_header.is_psram_image, False)
        self.assertEqual(rps_header.sha_type, 0)
        self.assertEqual(rps_header.magic, 0x900D900D)
        self.assertEqual(rps_header.image_size, 0)
        self.assertEqual(rps_header.version, 0)
        self.assertEqual(rps_header.address, 0)
        self.assertEqual(rps_header.crc, 0)
        self.assertEqual(rps_header.mic, b"\x00" * 16)
        self.assertEqual(rps_header.fw_info, 0)

    def test_header_set_control_flags(self):
        rps_header = RPS().Header()
        rps_header.set_control_flags(False, True, True, True, True)
        self.assertEqual(rps_header.is_m4_image, False)
        self.assertEqual(rps_header.is_encrypted, True)
        self.assertEqual(rps_header.mic_protected, True)
        self.assertEqual(rps_header.is_signed, True)
        self.assertEqual(rps_header.is_psram_image, True)

    def test_header_set_signature_type(self):
        rps_header = RPS().Header()
        rps_header.set_signature_type(1)
        self.assertEqual(rps_header.sha_type, 1)

    def test_header_set_image_size(self):
        rps_header = RPS().Header()
        rps_header.set_image_size(100)
        self.assertEqual(rps_header.image_size, 100)

    def test_header_set_version(self):
        rps_header = RPS().Header()
        rps_header.set_version(1, 2)
        self.assertEqual(rps_header.version, 1)
        self.assertEqual(rps_header.fw_info, 2)

    def test_header_set_address(self):
        rps_header = RPS().Header()
        rps_header.set_address(0x08000000)
        self.assertEqual(rps_header.address, 0x08000000)

    def test_header_set_crc(self):
        rps_header = RPS().Header()

        rps_header.set_crc(0x1234)

        self.assertEqual(rps_header.crc, 0x1234)

    def test_header_set_mic(self):
        rps_header = RPS().Header()

        rps_header.set_mic(b"\x12\x34\x56\x78\x12\x34\x56\x78\x12\x34\x56\x78\x12\x34\x56\x78")

        self.assertEqual(rps_header.mic, b"\x12\x34\x56\x78\x12\x34\x56\x78\x12\x34\x56\x78\x12\x34\x56\x78")

    def test_header_get_binary_data(self):
        rps_header = RPS().Header()

        rps_header.set_control_flags(False, True, True, True, True)
        rps_header.set_signature_type(1)
        rps_header.set_image_size(100)
        rps_header.set_version(1, 2)
        rps_header.set_address(0x08000000)
        rps_header.set_crc(0x1234)
        rps_header.set_mic(b"\x12\x34\x56\x78\x12\x34\x56\x78\x12\x34\x56\x78\x12\x34\x56\x78")

        expected_binary_data = \
            b"\x4e\x00\x01\x00\x0d\x90\x0d\x90\x64\x00\x00\x00\x01\x00\x00\x00" \
            b"\x00\x00\x00\x08\x34\x12\x00\x00\x12\x34\x56\x78\x12\x34\x56\x78" \
            b"\x12\x34\x56\x78\x12\x34\x56\x78\x00\x00\x00\x00\x02\x00\x00\x00" \
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0d\x90\x0d\x90"

        self.assertEqual(rps_header.get_binary_data(), expected_binary_data)

    def test_boot_descriptor_entry_default_parameters(self):
        rps_boot_descriptor_entry = RPS().BootDescriptor().BootDescriptorEntry()
        self.assertEqual(rps_boot_descriptor_entry.length, 0)
        self.assertFalse(rps_boot_descriptor_entry.last_entry)
        self.assertEqual(rps_boot_descriptor_entry.destination_address, 0)

    def test_boot_descriptor_entry_set_length(self):
        rps_boot_descriptor_entry = RPS().BootDescriptor().BootDescriptorEntry()
        rps_boot_descriptor_entry.set_length(100)
        self.assertEqual(rps_boot_descriptor_entry.length, 100)

    def test_boot_descriptor_entry_set_last_entry(self):
        rps_boot_descriptor_entry = RPS().BootDescriptor().BootDescriptorEntry()
        rps_boot_descriptor_entry.set_last_entry(True)
        self.assertTrue(rps_boot_descriptor_entry.last_entry)

    def test_boot_descriptor_entry_set_destination_address(self):
        rps_boot_descriptor_entry = RPS().BootDescriptor().BootDescriptorEntry()
        rps_boot_descriptor_entry.set_destination_address(0x08000000)
        self.assertEqual(rps_boot_descriptor_entry.destination_address, 0x08000000)

    def test_boot_descriptor_entry_get_binary_data(self):
        rps_boot_descriptor_entry = RPS().BootDescriptor().BootDescriptorEntry()

        rps_boot_descriptor_entry.set_length(100)
        rps_boot_descriptor_entry.set_last_entry(True)
        rps_boot_descriptor_entry.set_destination_address(0x08000000)

        expected_binary_data = b"\x64\x00\x00\x80\x00\x00\x00\x08"

        self.assertEqual(rps_boot_descriptor_entry.get_binary_data(), expected_binary_data)

    def test_boot_descriptor_default_parameters(self):
        rps_boot_descriptor = RPS().BootDescriptor()
        self.assertEqual(rps_boot_descriptor.magic, 0x5AA5)
        self.assertEqual(rps_boot_descriptor.boot_descriptor_offset, 0)
        self.assertEqual(rps_boot_descriptor.ivt_offset, 0)

        self.assertEqual(len(rps_boot_descriptor.boot_descriptor_entries), 7)
        for entry in rps_boot_descriptor.boot_descriptor_entries:
            self.assertEqual(entry.length, 0)
            self.assertFalse(entry.last_entry)
            self.assertEqual(entry.destination_address, 0)

    def test_boot_descriptor_set_boot_descriptor_offset(self):
        rps_boot_descriptor = RPS().BootDescriptor()
        rps_boot_descriptor.set_boot_descriptor_offset(100)
        self.assertEqual(rps_boot_descriptor.boot_descriptor_offset, 100)

    def test_boot_descriptor_set_ivt_offset(self):
        rps_boot_descriptor = RPS().BootDescriptor()
        rps_boot_descriptor.set_ivt_offset(100)
        self.assertEqual(rps_boot_descriptor.ivt_offset, 100)

    def test_boot_descriptor_get_binary_data(self):
        rps_boot_descriptor = RPS().BootDescriptor()

        rps_boot_descriptor.set_boot_descriptor_offset(100)
        rps_boot_descriptor.set_ivt_offset(200)

        for i, entry in enumerate(rps_boot_descriptor.boot_descriptor_entries):
            entry.set_length(i + 1)
            entry.set_last_entry(i == 6)
            entry.set_destination_address((i + 1) * 0x1000000)

        expected_binary_data = \
            b"\xa5\x5a\x64\x00\xc8\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x01" \
            b"\x02\x00\x00\x00\x00\x00\x00\x02\x03\x00\x00\x00\x00\x00\x00\x03" \
            b"\x04\x00\x00\x00\x00\x00\x00\x04\x05\x00\x00\x00\x00\x00\x00\x05" \
            b"\x06\x00\x00\x00\x00\x00\x00\x06\x07\x00\x00\x80\x00\x00\x00\x07" \
            + bytes(RPS_BOOT_DESCRIPTOR_PADDING_SIZE)

        self.assertEqual(rps_boot_descriptor.get_binary_data(), expected_binary_data)


if __name__ == "__main__":
    unittest.main()
