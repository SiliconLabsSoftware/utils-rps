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

# For reference:
#     width=32 poly=0xd95eaae5 init=0 refin=true refout=true xorout=0
def create_table() -> list[int]:
    crc_table = [0] * 256
    for b in range(256):
        register = b
        for _ in range(8):
            lsb = register & 1
            register >>= 1
            if lsb:
                # Reflected polynomial: 0xd95eaae5
                register ^= 0xA7557A9B
        crc_table[b] = register
    return crc_table


def crc32(data: bytes) -> int:
    crc_table = create_table()
    register = 0
    for b in data:
        register = crc_table[(b ^ register) & 0xFF] ^ (register >> 8)
    return register
