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

import functools
import intelhex
import re

@functools.wraps(int)
def parse_int(x : str) -> int:
    """ Parse decimal ("1234") and hexadecimal ("0x1234") numbers to integers. Wrap around int() to make error messages look nice. """
    return int(x, base=0)

def is_rps_file(filename : str) -> bool:
    """ Check if a file is an RPS file. """
    return filename.endswith(".rps") or filename.endswith("_isp.bin")

def read_rps_file(filename : str) -> bytes:
    """ Read an RPS file and return its contents as a bytes object. """
    with open(filename, "rb") as f:
        return bytes(f.read())

def is_hex_file(filename : str) -> bool:
    """ Check if a file is a .hex file. """
    return filename.endswith(".hex")

def check_hex_file_sane_size(filename : str, max_size : int) -> bool:
    """ Verify that the .hex file does not constitute a too large contiguous memory block. """
    hex_parser = intelhex.IntelHex()
    hex_parser.loadhex(filename)
    if hex_parser.maxaddr() - hex_parser.minaddr() > max_size:
        return False
    return True

def read_hex_file(filename : str) -> tuple[list[int], bytes]:
    """ Read a .hex file and return the segments and the full binary contents as a bytes object. """
    hex_parser = intelhex.IntelHex()
    hex_parser.loadhex(filename)
    return hex_parser.segments(), hex_parser.tobinstr()


def is_txt_file(filename : str) -> bool:
    """ Check if a file is a text file. """
    return filename.endswith(".txt")

def read_txt_file_key(filename : str) -> bytes:
    """ Read a text file and return its contents as a string. """
    with open(filename, "r") as f:
        hexString = f.read().replace("\n", "")
    return bytes.fromhex(hexString)


def is_bin_file(filename : str) -> bool:
    """ Check if a file is a binary file. """
    return filename.endswith(".bin")

def read_bin_file_key(filename : str) -> bytes:
    """ Read a binary file and return its contents as a bytes object. """
    with open(filename, "rb") as f:
        return bytes(f.read())


def is_pem_file(filename : str) -> bool:
    """ Check if a file is a PEM file. """
    return filename.endswith(".pem")

def read_pem_file_key(filename : str) -> bytes:
    """ Read a PEM file and return its contents as a string. """
    with open(filename, "rb") as f:
        return bytes(f.read())


def is_der_file(filename : str) -> bool:
    """ Check if a file is a DER file. """
    return filename.endswith(".der")

def read_der_file_key(filename : str) -> bytes:
    """ Read a DER file and return its contents as a bytes object. """
    with open(filename, "rb") as f:
        return bytes(f.read())


def is_map_file(filename : str) -> bool:
    """ Check if a file is a map file. """
    return filename.endswith(".map")

def get_flash_start_address_from_map_file(filename : str) -> int:
    """ Parse a map file and return the flash start address. Expects a GCC-style map file. """

    flashPattern = r"^(FLASH|ROM)\s+0x(?P<start>[0-9a-f]+)\s+0x(?P<size>[0-9a-f]+)\s+xr\s*$"
    with open(filename, "r") as f:
        for line in f:
            match = re.match(flashPattern, line, re.IGNORECASE)
            if match:
                return int(match.group("start"), 16)

    return 0xFFFFFFFF
