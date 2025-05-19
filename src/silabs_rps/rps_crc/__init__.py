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

from ctypes import c_uint32


POLYNOMIAL = c_uint32(0xD95EAAE5)
MSB_MASK   = c_uint32(0x80000000)
CRC_MASK   = c_uint32(0xFFFFFFFF)

def crc32(data : bytes) -> int:
    """ Calculate the 32 bit CRC of the given data. Proprietary algorithm. """

    crc : c_uint32 = c_uint32(0x0)

    for _ in range (0, 32):
        if (crc.value & 0x01):
            crc = c_uint32(((crc.value ^ POLYNOMIAL.value) >> 1) | MSB_MASK.value)
        else:
            crc = c_uint32(crc.value >> 1)

    for byte in data:
        c = _reflect(c_uint32(byte), 8)

        for i in range(0, 8):
            bit : int = crc.value & MSB_MASK.value
            crc = c_uint32(
                c_uint32(crc.value << 1).value | ((c.value >> (7 - i)) & 0x01)
            )
            if bit:
                crc = c_uint32(crc.value ^ POLYNOMIAL.value)

        crc = c_uint32(crc.value & CRC_MASK.value)

    for _ in range(0, 32):
        bit : int = crc.value & MSB_MASK.value
        crc = c_uint32(crc.value << 1)
        if bit:
            crc = c_uint32(crc.value ^ POLYNOMIAL.value)

    crc = _reflect(crc, 32)

    return c_uint32(crc.value & CRC_MASK.value).value 


def _reflect(number : c_uint32, width : int) -> c_uint32:
    """ Reflect the bits of the given number. """
    ret : c_uint32 = c_uint32(number.value & 0x01)

    for _ in range(1, width):
        number = c_uint32(number.value >> 1)
        ret = c_uint32((ret.value << 1) | (number.value & 0x01))

    return ret
