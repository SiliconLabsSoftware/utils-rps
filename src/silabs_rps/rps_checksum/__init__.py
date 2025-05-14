from ctypes import c_uint32


def checksum(data : bytes) -> int:
    """ Calculate the checksum of the given data. Proprietary algorithm. """
    sum : c_uint32 = c_uint32(1) # Initial value

    size = len(data)

    if size == 0:
        return sum.value

    dword : c_uint32 = c_uint32(0)

    cnt = 0
    for cnt in range(0, size - (size % 4), 4):
        dword = c_uint32(int.from_bytes(data[cnt:cnt+4], byteorder='little'))
        sum = c_uint32(sum.value + dword.value)
        if (sum.value < dword.value):
            sum = c_uint32(sum.value + 1)

    if size % 4 != 0:
        dword : c_uint32 = c_uint32(0xFFFFFFFF)
        dword = c_uint32(~(dword.value << (8 * (size % 4))))
        dword = c_uint32(c_uint32(int.from_bytes(data[cnt:cnt+4], byteorder='little')).value & dword.value)
        sum = c_uint32(sum.value + dword.value)
        if (sum.value < dword.value):
            sum = c_uint32(sum.value + 1)

    return c_uint32(~sum.value).value
