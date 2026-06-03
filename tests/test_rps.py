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

from src.silabs_rps.rps import RPS
from src.silabs_rps.rps_consts import RPS_BOOT_DESCRIPTOR_PADDING_SIZE

TEST_FILE_DIR = "tests/testfiles/crypto/"

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

    def test_header_get_control_flags(self):
        rps_header = RPS().Header()
        rps_header.set_control_flags(False, True, False, True, False)
        self.assertEqual(
            rps_header.get_control_flags(),
            (False, True, False, True, False),
        )

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

    def test_header_get_binary_data_default_m4(self):
        # The default header is an m4 image; this exercises the m4 branch in get_binary_data
        rps_header = RPS().Header()

        binary_data = rps_header.get_binary_data()

        self.assertEqual(len(binary_data), 64)
        # control_flags only has the m4 bit set, then sha_type, then magic
        self.assertEqual(binary_data[:8], b"\x01\x00\x00\x00\x0d\x90\x0d\x90")
        # Trailing magic
        self.assertEqual(binary_data[60:64], b"\x0d\x90\x0d\x90")

    def test_header_set_binary_data_round_trip_m4(self):
        src = RPS().Header()
        src.set_control_flags(True, False, False, False, False)
        src.set_signature_type(1)
        src.set_image_size(0x12345678)
        src.set_version(0xAABBCCDD, 0x55667788)
        src.set_address(0x08001234)
        src.set_crc(0xDEADBEEF)
        src.set_mic(b"\x12\x34\x56\x78\x9A\xBC\xDE\xF0\x12\x34\x56\x78\x9A\xBC\xDE\xF0")

        dst = RPS().Header()
        dst.set_binary_data(src.get_binary_data())

        self.assertEqual(dst.get_control_flags(), src.get_control_flags())
        self.assertEqual(dst.sha_type, src.sha_type)
        self.assertEqual(dst.magic, src.magic)
        self.assertEqual(dst.image_size, src.image_size)
        self.assertEqual(dst.version, src.version)
        self.assertEqual(dst.address, src.address)
        self.assertEqual(dst.crc, src.crc)
        self.assertEqual(dst.mic, src.mic)
        self.assertEqual(dst.fw_info, src.fw_info)

    def test_header_set_binary_data_round_trip_nwp(self):
        # When is_m4_image is False the counter field is serialised at offset 40
        src = RPS().Header()
        src.set_control_flags(False, True, True, True, True)
        src.set_signature_type(2)
        src.set_image_size(100)
        src.set_version(0x11223344, 0x55667788)
        src.set_address(0x0A001234)
        src.set_crc(0x1234)
        src.counter = 0xCAFEBABE

        dst = RPS().Header()
        dst.set_binary_data(src.get_binary_data())

        self.assertEqual(dst.get_control_flags(), src.get_control_flags())
        self.assertEqual(dst.counter, src.counter)
        self.assertEqual(dst.fw_info, src.fw_info)
        self.assertEqual(dst.version, src.version)
        self.assertEqual(dst.address, src.address)

    def test_header_set_binary_data_too_small_raises(self):
        rps_header = RPS().Header()
        with self.assertRaises(ValueError):
            rps_header.set_binary_data(b"\x00" * 16)

    def test_boot_descriptor_entry_set_binary_data_round_trip(self):
        src = RPS().BootDescriptor().BootDescriptorEntry()
        src.set_length(0x123456)
        src.set_last_entry(True)
        src.set_destination_address(0x08001234)

        dst = RPS().BootDescriptor().BootDescriptorEntry()
        dst.set_binary_data(src.get_binary_data())

        self.assertEqual(dst.length, src.length)
        self.assertEqual(dst.last_entry, src.last_entry)
        self.assertEqual(dst.destination_address, src.destination_address)

    def test_boot_descriptor_entry_set_binary_data_too_small_raises(self):
        entry = RPS().BootDescriptor().BootDescriptorEntry()
        with self.assertRaises(ValueError):
            entry.set_binary_data(b"\x00" * 4)

    def test_boot_descriptor_entry_unset_last_entry(self):
        # Toggling last_entry off should clear the control bit again
        entry = RPS().BootDescriptor().BootDescriptorEntry()
        entry.set_last_entry(True)
        entry.set_last_entry(False)
        self.assertFalse(entry.last_entry)
        self.assertEqual(entry.control_bits & (1 << 31), 0)

    def test_boot_descriptor_get_last_entry_index(self):
        rps_boot_descriptor = RPS().BootDescriptor()
        rps_boot_descriptor.boot_descriptor_entries[3].set_last_entry(True)
        self.assertEqual(rps_boot_descriptor.get_last_entry_index(), 3)

    def test_boot_descriptor_get_last_entry_index_no_last(self):
        rps_boot_descriptor = RPS().BootDescriptor()
        self.assertEqual(rps_boot_descriptor.get_last_entry_index(), -1)

    def test_boot_descriptor_set_binary_data_round_trip(self):
        src = RPS().BootDescriptor()
        src.set_boot_descriptor_offset(100)
        src.set_ivt_offset(200)
        for i, entry in enumerate(src.boot_descriptor_entries):
            entry.set_length(i + 1)
            entry.set_last_entry(i == 6)
            entry.set_destination_address((i + 1) * 0x1000000)

        dst = RPS().BootDescriptor()
        dst.set_binary_data(src.get_binary_data())

        self.assertEqual(dst.magic, src.magic)
        self.assertEqual(dst.boot_descriptor_offset, src.boot_descriptor_offset)
        self.assertEqual(dst.ivt_offset, src.ivt_offset)
        for src_entry, dst_entry in zip(src.boot_descriptor_entries, dst.boot_descriptor_entries):
            self.assertEqual(dst_entry.length, src_entry.length)
            self.assertEqual(dst_entry.last_entry, src_entry.last_entry)
            self.assertEqual(dst_entry.destination_address, src_entry.destination_address)

    def test_boot_descriptor_set_binary_data_too_small_raises(self):
        rps_boot_descriptor = RPS().BootDescriptor()
        with self.assertRaises(ValueError):
            rps_boot_descriptor.set_binary_data(b"\x00" * 16)

    def test_application_default_parameters(self):
        rps_app = RPS().Application()
        self.assertEqual(rps_app.image, bytearray())

    def test_application_set_image(self):
        rps_app = RPS().Application()
        rps_app.set_image(b"\x01\x02\x03\x04")
        self.assertEqual(rps_app.image, bytearray(b"\x01\x02\x03\x04"))

    def test_application_calculate_and_set_checksum(self):
        # Image must be larger than 0xEC bytes for the checksum to be written
        rps_app = RPS().Application()
        rps_app.set_image(b"\xAA" * 240)

        self.assertTrue(rps_app.calculate_and_set_checksum())
        # The 4 checksum bytes at offset 0xEC should now differ from the original 0xAA filler
        self.assertNotEqual(rps_app.image[0xEC:0xEC + 4], b"\xAA\xAA\xAA\xAA")

    def test_application_calculate_and_set_checksum_too_small(self):
        rps_app = RPS().Application()
        rps_app.set_image(b"\xAA" * 0xEC)
        self.assertFalse(rps_app.calculate_and_set_checksum())

    def test_signature_default_parameters(self):
        rps_signature = RPS().Signature()
        self.assertEqual(rps_signature.signature, b"")

    def test_signature_set_signature(self):
        rps_signature = RPS().Signature()
        rps_signature.set_signature(b"\xAB" * 72)
        self.assertEqual(rps_signature.signature, b"\xAB" * 72)

    def test_rps_default_parameters(self):
        rps_image = RPS()
        self.assertIsInstance(rps_image.header, RPS.Header)
        self.assertIsInstance(rps_image.boot_descriptor, RPS.BootDescriptor)
        self.assertIsInstance(rps_image.application, RPS.Application)
        self.assertIsInstance(rps_image.signature, RPS.Signature)

    def test_rps_get_binary_data_unsigned(self):
        # An unsigned RPS image is header + boot descriptor + application image (no signature appended)
        rps_image = RPS()
        rps_image.application.set_image(b"\x11" * 16)

        binary_data = rps_image.get_binary_data()

        self.assertEqual(
            binary_data,
            rps_image.header.get_binary_data()
            + rps_image.boot_descriptor.get_binary_data()
            + b"\x11" * 16,
        )

    def test_rps_get_binary_data_signed_appends_signature(self):
        rps_image = RPS()
        rps_image.header.set_control_flags(True, False, False, True, False)
        rps_image.application.set_image(b"\x22" * 16)
        rps_image.signature.set_signature(b"\x33" * 72)

        binary_data = rps_image.get_binary_data()

        self.assertEqual(binary_data[-72:], b"\x33" * 72)

    def test_rps_set_binary_data_too_small_raises(self):
        rps_image = RPS()
        with self.assertRaises(ValueError):
            rps_image.set_binary_data(b"\x00" * 32)

    def test_rps_set_binary_data_unsigned_round_trip(self):
        # dummy-without-mic.rps is an unsigned RPS image that round-trips cleanly
        with open(os.path.join(TEST_FILE_DIR, "dummy-without-mic.rps"), "rb") as f:
            data = f.read()

        rps_image = RPS()
        rps_image.set_binary_data(data)

        self.assertFalse(rps_image.header.is_signed)
        self.assertEqual(rps_image.signature.signature, b"")
        self.assertEqual(rps_image.get_binary_data(), data)

    def test_rps_set_binary_data_signed_round_trip(self):
        # dummy-signed.rps has a 72-byte ECDSA signature appended
        with open(os.path.join(TEST_FILE_DIR, "dummy-signed.rps"), "rb") as f:
            data = f.read()

        rps_image = RPS()
        rps_image.set_binary_data(data)

        self.assertTrue(rps_image.header.is_signed)
        self.assertEqual(len(rps_image.signature.signature), 72)
        self.assertEqual(rps_image.signature.signature, data[-72:])
        self.assertEqual(rps_image.get_binary_data(), data)


if __name__ == "__main__":
    unittest.main()
