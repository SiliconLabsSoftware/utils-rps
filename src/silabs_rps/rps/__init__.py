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

import struct

from .. import rps_consts
from .. import rps_checksum


class RPS:

    class Header:
        def __init__(self) -> None:
            self.is_m4_image    : bool  = True
            self.is_encrypted   : bool  = False
            self.mic_protected  : bool  = False
            self.is_signed      : bool  = False
            self.is_psram_image : bool  = False

            self.sha_type       : int   = rps_consts.RPS_SIGNATURE_TYPE_NONE
            self.magic          : int   = rps_consts.RPS_HEADER_MAGIC
            self.image_size     : int   = 0
            self.version        : int   = 0
            self.address        : int   = 0
            self.crc            : int   = 0
            self.mic            : bytes = b"\x00" * rps_consts.RPS_MIC_SIZE
            self.fw_info        : int   = 0
            self.counter        : int   = 0

        def set_control_flags(self, is_m4_image : bool, is_encrypted : bool, mic_protected : bool, is_signed : bool, is_psram_image : bool) -> None:
            self.is_m4_image    = is_m4_image
            self.is_encrypted   = is_encrypted
            self.mic_protected  = mic_protected
            self.is_signed      = is_signed
            self.is_psram_image = is_psram_image

        def get_control_flags(self) -> tuple[bool, bool, bool, bool, bool]:
            return self.is_m4_image, self.is_encrypted, self.mic_protected, self.is_signed, self.is_psram_image

        def set_signature_type(self, sha_type : int) -> None:
            self.sha_type = sha_type

        def set_image_size(self, image_size : int) -> None:
            self.image_size = image_size

        def set_version(self, version : int, fw_info : int) -> None:
            self.version = version
            self.fw_info = fw_info

        def set_address(self, address : int) -> None:
            self.address = address

        def set_crc(self, crc : int) -> None:
            self.crc = crc

        def set_mic(self, mic : bytes) -> None:
            self.mic = mic

        def get_binary_data(self) -> bytes:
            buffer = bytearray(rps_consts.RPS_HEADER_SIZE)
            control_flags = 0
            control_flags |= int(self.is_m4_image)    << 0
            control_flags |= int(self.is_encrypted)   << 1
            control_flags |= int(self.mic_protected)  << 2
            control_flags |= int(self.is_signed)      << 3
            control_flags |= int(self.is_psram_image) << 6
            struct.pack_into("<H", buffer, 0, control_flags)

            struct.pack_into("<H", buffer, 2, self.sha_type)
            struct.pack_into("<I", buffer, 4, self.magic)
            struct.pack_into("<I", buffer, 8, self.image_size)
            struct.pack_into("<I", buffer, 12, self.version)
            struct.pack_into("<I", buffer, 16, self.address)
            struct.pack_into("<I", buffer, 20, self.crc)
            buffer[24:40] = self.mic
            if self.is_m4_image:
                struct.pack_into("<I", buffer, 40, self.fw_info)
                # Reserved, 4 bytes
            else:
                struct.pack_into("<I", buffer, 40, self.counter)
                struct.pack_into("<I", buffer, 44, self.fw_info)
            # Reserved, 12 bytes
            struct.pack_into("<I", buffer, 60, self.magic)

            return bytes(buffer)

        def set_binary_data(self, data : bytes) -> None:
            if len(data) < rps_consts.RPS_HEADER_SIZE:
                raise ValueError("Input data is too small to be a header.")

            control_flags = struct.unpack_from("<H", data, 0)[0]
            self.is_m4_image    = bool(control_flags & 0b00000001)
            self.is_encrypted   = bool(control_flags & 0b00000010)
            self.mic_protected  = bool(control_flags & 0b00000100)
            self.is_signed      = bool(control_flags & 0b00001000)
            self.is_psram_image = bool(control_flags & 0b01000000)

            self.sha_type       = struct.unpack_from("<H", data, 2)[0]
            self.magic          = struct.unpack_from("<I", data, 4)[0]
            self.image_size     = struct.unpack_from("<I", data, 8)[0]
            self.version        = struct.unpack_from("<I", data, 12)[0]
            self.address        = struct.unpack_from("<I", data, 16)[0]
            self.crc            = struct.unpack_from("<I", data, 20)[0]
            self.mic            = data[24:40]
            if self.is_m4_image:
                self.fw_info = struct.unpack_from("<I", data, 40)[0]
                # Reserved, 4 bytes
            else:
                self.counter = struct.unpack_from("<I", data, 40)[0]
                self.fw_info = struct.unpack_from("<I", data, 44)[0]
            # Reserved, 12 bytes

            return

    class BootDescriptor:
        class BootDescriptorEntry:
            def __init__(self) -> None:
                self.length              : int  = 0
                self.control_bits        : int  = 0
                self.destination_address : int  = 0

                self.last_entry          : bool = False

            def set_length(self, length : int) -> None:
                self.length = length

            def set_last_entry(self, last_entry : bool) -> None:
                self.last_entry = last_entry

                if last_entry:
                    self.control_bits |= 1 << 31
                else:
                    self.control_bits &= ~(1 << 31)

            def set_destination_address(self, destination_address : int) -> None:
                self.destination_address = destination_address

            def get_binary_data(self) -> bytes:
                length_and_control_flags = 0
                length_and_control_flags |= self.length & 0x00FFFFFF
                length_and_control_flags |= self.control_bits & 0xFF000000

                buffer = bytearray(rps_consts.RPS_BOOT_DESCRIPTOR_ENTRY_SIZE)
                struct.pack_into("<I", buffer, 0, length_and_control_flags)
                struct.pack_into("<I", buffer, 4, self.destination_address)

                return bytes(buffer)

            def set_binary_data(self, data : bytes) -> None:
                if len(data) < rps_consts.RPS_BOOT_DESCRIPTOR_ENTRY_SIZE:
                    raise ValueError("Input data is too small to be a boot descriptor entry.")

                self.length              = struct.unpack_from("<I", data, 0)[0] & 0x00FFFFFF
                self.control_bits        = struct.unpack_from("<I", data, 0)[0] & 0xFF000000
                self.destination_address = struct.unpack_from("<I", data, 4)[0]

                self.last_entry = bool(self.control_bits & (1 << 31))


        def __init__(self) -> None:
            self.magic                  : int = rps_consts.RPS_BOOT_DESCRIPTOR_MAGIC
            self.boot_descriptor_offset : int = 0
            self.ivt_offset             : int = 0
            self.boot_descriptor_entries: list[RPS.BootDescriptorEntry] = [self.BootDescriptorEntry() for _ in range(rps_consts.RPS_NUM_BOOT_DESCRIPTOR_ENTRIES)]
            self.padding                : bytes = bytes(rps_consts.RPS_FULL_HEADER_SIZE - rps_consts.RPS_HEADER_SIZE - rps_consts.RPS_BOOT_DESCRIPTOR_SIZE)

        def set_boot_descriptor_offset(self, boot_descriptor_offset : int) -> None:
            self.boot_descriptor_offset = boot_descriptor_offset

        def set_ivt_offset(self, ivt_offset : int) -> None:
            self.ivt_offset = ivt_offset

        def get_last_entry_index(self) -> int:
            for i, entry in enumerate(self.boot_descriptor_entries):
                if entry.last_entry:
                    return i
            return -1


        def get_binary_data(self) -> bytes:
            buffer = bytearray(rps_consts.RPS_FULL_HEADER_SIZE - rps_consts.RPS_HEADER_SIZE)
            struct.pack_into("<H", buffer, 0, self.magic)
            struct.pack_into("<H", buffer, 2, self.boot_descriptor_offset)
            struct.pack_into("<I", buffer, 4, self.ivt_offset)
            for i, entry in enumerate(self.boot_descriptor_entries):
                buffer[rps_consts.RPS_BOOT_DESCRIPTOR_ENTRY_SIZE * i + 8:rps_consts.RPS_BOOT_DESCRIPTOR_ENTRY_SIZE * i + 8 + rps_consts.RPS_BOOT_DESCRIPTOR_ENTRY_SIZE] = entry.get_binary_data()

            buffer[-len(self.padding):] = self.padding
            return bytes(buffer)

        def set_binary_data(self, data : bytes) -> None:
            if len(data) < rps_consts.RPS_BOOT_DESCRIPTOR_SIZE:
                raise ValueError("Input data is too small to be a boot descriptor.")

            self.magic                  = struct.unpack_from("<H", data, 0)[0]
            self.boot_descriptor_offset = struct.unpack_from("<H", data, 2)[0]
            self.ivt_offset             = struct.unpack_from("<I", data, 4)[0]
            for i, entry in enumerate(self.boot_descriptor_entries):
                entry.set_binary_data(data[rps_consts.RPS_BOOT_DESCRIPTOR_ENTRY_SIZE * i + 8:rps_consts.RPS_BOOT_DESCRIPTOR_ENTRY_SIZE * i + 8 + rps_consts.RPS_BOOT_DESCRIPTOR_ENTRY_SIZE])

            self.padding = data[-len(self.padding):]


    class Application:
        def __init__(self) -> None:
            self.image : bytearray = bytearray()

        def set_image(self, image : bytes) -> None:
            self.image = bytearray(image)

        def calculate_and_set_checksum(self) -> bool:
            if len(self.image) <= 0xEC:
                return False

            # Calculate a checksum of the first 58 words in the image
            checksum_value = rps_checksum.checksum(self.image[:0xEC])

            # Write the checksum to the 59th word
            self.image[0xEC:0xEC + 4] = struct.pack("<I", checksum_value)

            return True

    class Signature:
        def __init__(self) -> None:
            self.signature : bytes = b""

        def set_signature(self, signature : bytes) -> None:
            self.signature = signature


    def __init__(self) -> None:
        self.header          : RPS.Header          = self.Header()
        self.boot_descriptor : RPS.BootDescriptor  = self.BootDescriptor()
        self.application     : RPS.Application     = self.Application()
        self.signature       : RPS.Signature       = self.Signature()

    def get_binary_data(self) -> bytes:
        buffer = bytearray()
        buffer += bytearray(self.header.get_binary_data())
        buffer += bytearray(self.boot_descriptor.get_binary_data())

        buffer += bytearray(self.application.image)

        if self.header.is_signed:
            buffer += bytearray(self.signature.signature)

        return bytes(buffer)

    def set_binary_data(self, data : bytes) -> None:
        if len(data) < rps_consts.RPS_HEADER_SIZE:
            raise ValueError("Input data is too small to be an RPS file.")

        self.header.set_binary_data(data[:rps_consts.RPS_HEADER_SIZE])
        self.boot_descriptor.set_binary_data(data[rps_consts.RPS_HEADER_SIZE:rps_consts.RPS_FULL_HEADER_SIZE])

        if self.header.is_signed:
            self.application.set_image(data[rps_consts.RPS_FULL_HEADER_SIZE:-rps_consts.RPS_SIGNATURE_SIZE])
            self.signature.set_signature(data[-rps_consts.RPS_SIGNATURE_SIZE:])
        else:
            self.application.set_image(data[rps_consts.RPS_FULL_HEADER_SIZE:])
