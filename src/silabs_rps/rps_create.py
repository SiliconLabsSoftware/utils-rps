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

rps_create.py - Create RPS images for Silicon Labs SiWx91x devices

Copyright: 2025, Silicon Laboratories Inc.
Version: 1.0.3

Usage:
    rps_create <output filename> --app <filename> [--map <filename>] [--address <address>] [--app-version <version>] [--fw-info <firmware info>] [--sign <filename>] [--sha <size>] [--encrypt <filename>] [--mic <filename>] [--iv <filename>]

Options:
    <output filename>           Output RPS file.
    --app <filename>            Application binary file. Must be in .bin or .hex format.
    --map <filename>            Map file (.map) from the compilation of the provided application. Used for determining the flash start address.
    --address <address>         Application start address.
    --app-version <version>     Application version.
    --fw-info <firmware info>   Additional version information.
    --sign <filename>           Sign the RPS image using ECDSA. Key must be in .pem or .der format.
    --sha <size>                Use SHA-<size> for ECDSA. Available: 256 (default), 384 and 512 bits.
    --encrypt <filename>        Encrypt the application image using AES ECB encryption. Key must be in .bin or .txt format.
    --mic <filename>            Use MIC (AES CBC-MAC) based integrity check instead of CRC. Key must be in .bin or .txt format.
    --iv <filename>             Initialization vector for MIC calculation. Must be in .bin or .txt format.

Examples:
    $ python rps_create.py my_image.rps --app my_app.hex --app-version 1 --fw-info 0x1234 --sign my_key.pem --sha 384

"""
import argparse
import os

from . import rps
from . import rps_helpers
from . import rps_consts
from . import rps_crc
from . import rps_crypto


_parser = argparse.ArgumentParser(
    prog="rps_create",
    description="Convert application binaries for Silicon Labs SiWx91x devices into RPS images.",
)

_parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0.3")
_parser.add_argument("output",        type=str,                   metavar="<output filename>",                             help="Output RPS file.")
_parser.add_argument("--app",         type=str,                   metavar="<filename>",        required=True,              help="Application binary file. Must be in .bin or .hex format.")
_parser.add_argument("--map",         type=str,                   metavar="<filename>",                                    help="Map file (.map) from the compilation of the provided application. Used for determining the flash start address.")
_parser.add_argument("--address",     type=rps_helpers.parse_int, metavar="<address>",                                     help="Application start address.")
_parser.add_argument("--app-version", type=rps_helpers.parse_int, metavar="<version>",                        default=0,   help="Application version.")
_parser.add_argument("--fw-info",     type=rps_helpers.parse_int, metavar="<firmware info>",                  default=0,   help="Additional version information.")
_parser.add_argument("--sign",        type=str,                   metavar="<filename>",                                    help="Sign the RPS image using ECDSA. Key must be in .pem or .der format.")
_parser.add_argument("--sha",         type=int,                   metavar="<size>",                           default=256, help="Use SHA-<size> for ECDSA. Available: 256 (default), 384 and 512 bits.")
_parser.add_argument("--encrypt",     type=str,                   metavar="<filename>",                                    help="Encrypt the application image using AES ECB encryption. Key must be in .bin or .txt format.")
_parser.add_argument("--mic",         type=str,                   metavar="<filename>",                                    help="Use MIC (AES CBC-MAC) based integrity check instead of CRC. Key must be in .bin or .txt format.")
_parser.add_argument("--iv",          type=str,                   metavar="<filename>",                                    help="Initialization vector for MIC calculation. Must be in .bin or .txt format.")


def main():
    _args = _parser.parse_args()

    output_filename  : str         = _args.output
    app_filename     : str         = _args.app
    map_filename     : str  | None = _args.map
    address          : int  | None = _args.address
    app_version      : int         = _args.app_version
    fw_info          : int         = _args.fw_info
    apply_signature  : bool        = _args.sign is not None
    sign_filename    : str  | None = _args.sign
    sha_size         : int         = _args.sha
    apply_encryption : bool        = _args.encrypt is not None
    encrypt_filename : str  | None = _args.encrypt
    apply_mic        : bool        = _args.mic is not None
    mic_filename     : str  | None = _args.mic
    iv_filename      : str  | None = _args.iv

    app_size        : int   = 0
    app_data        : bytes = b""
    is_psram_app    : bool  = False
    flash_start_addr: int   = 0
    signature_type  : int   = rps_consts.RPS_SIGNATURE_TYPE_NONE

    mic_key         : bytes | None = None
    iv              : bytes | None = None
    enc_key         : bytes | None = None
    sign_key        : bytes | None = None

    # Parse the input file
    print(f"Reading application file '{app_filename}'...")
    if rps_helpers.is_hex_file(app_filename):
        # Hex file, so address is encoded in the file
        if address is not None:
            print("Warning: Application start address is provided but will be ignored for .hex files.")

        if not rps_helpers.check_hex_file_sane_size(app_filename, 100 * 1024 * 1024):
            print(f"Error: Application size is larger than 100 MB, cannot proceed.")
            exit(-1)

        chunks, app_data = rps_helpers.read_hex_file(app_filename)
        app_size = len(app_data)

        address = chunks[0][0]
    else:
        if address is None:
            _parser.error("Application start address must be provided for binary files using the --address option.")

        with open(app_filename, "rb") as f:
            app_data = f.read()
            app_size = len(app_data)

    if app_size == 0:
        _parser.error("Application image is empty.")

    # Parse the MIC key
    if apply_mic:
        print(f"Parsing MIC key '{mic_filename}'...")
        if rps_helpers.is_bin_file(mic_filename):
            mic_key = rps_helpers.read_bin_file_key(mic_filename)
        elif rps_helpers.is_txt_file(mic_filename):
            mic_key = rps_helpers.read_txt_file_key(mic_filename)
        else:
            _parser.error("MIC key must be in .bin or .txt format.")

        if iv_filename is not None:
            print(f"Parsing IV file '{iv_filename}'...")
            if rps_helpers.is_bin_file(iv_filename):
                iv = rps_helpers.read_bin_file_key(iv_filename)
            elif rps_helpers.is_txt_file(iv_filename):
                iv = rps_helpers.read_txt_file_key(iv_filename)
            else:
                _parser.error("IV file must be in .bin or .txt format.")

            if len(iv) != 16:
                _parser.error("IV must be 16 bytes long.")

    # Parse the encryption key
    if apply_encryption:
        print(f"Parsing encryption key '{encrypt_filename}'...")
        if rps_helpers.is_bin_file(encrypt_filename):
            enc_key = rps_helpers.read_bin_file_key(encrypt_filename)
        elif rps_helpers.is_txt_file(encrypt_filename):
            enc_key = rps_helpers.read_txt_file_key(encrypt_filename)
        else:
            _parser.error("Encryption key must be in .bin or .txt format.")

    # Parse the signing key
    if apply_signature:
        print(f"Parsing signing key '{sign_filename}'...")
        if rps_helpers.is_pem_file(sign_filename):
            sign_key = rps_helpers.read_pem_file_key(sign_filename)
        elif rps_helpers.is_der_file(sign_filename):
            sign_key = rps_helpers.read_der_file_key(sign_filename)
        else:
            _parser.error("Signing key must be in .pem or .der format.")


    if (address & rps_consts.RPS_PSRAM_ADDRESS_BASE) == rps_consts.RPS_PSRAM_ADDRESS_BASE:
        is_psram_app = True
        if map_filename is not None:
            print(f"Reading map file '{map_filename}'...")
            if not rps_helpers.is_map_file(map_filename):
                _parser.error("Map file must be in .map format.")

            flash_start_addr = rps_helpers.get_flash_start_address_from_map_file(map_filename)
            if flash_start_addr == 0xFFFFFFFF:
                _parser.error("Flash start address not found in the map file.")
            else:
                print(f"Flash start address found in map file: 0x{flash_start_addr:08X}")
        else:
            print(f"Warning: Flash start address is not provided. Assuming flash start address to be the same as the provided application start address (0x{address:08X})."
                    "If this is not the case, you must provide a map file using the --map option.")
            flash_start_addr = address

    elif (address & rps_consts.RPS_M4_FLASH_ADDRESS_BASE) == rps_consts.RPS_M4_FLASH_ADDRESS_BASE:
        is_psram_app = False
        flash_start_addr = address
    else:
        _parser.error("Invalid application start address. Must be in the range of the M4 flash or PSRAM. NWP images are not supported.")

    if app_size % 4 != 0:
        # Regardless of security features, the RPS image must be word-aligned
        app_data += bytes(4 - (app_size % 4))

    if (apply_encryption or apply_mic) and not app_size % 16 == 0:
        print("Warning: Application size is not a multiple of 16 bytes, which is required for encryption and MIC calculation. Padding with zeroes.")
        app_data += bytes(16 - (app_size % 16))

    app_size = len(app_data) + rps_consts.RPS_FULL_HEADER_SIZE - rps_consts.RPS_HEADER_SIZE

    if apply_signature:
        # Parse the sha size
        if sha_size == 256:
            signature_type = rps_consts.RPS_SIGNATURE_TYPE_SHA256
        elif sha_size == 384:
            signature_type = rps_consts.RPS_SIGNATURE_TYPE_SHA384
        elif sha_size == 512:
            signature_type = rps_consts.RPS_SIGNATURE_TYPE_SHA512
        else:
            _parser.error("Invalid SHA size. Available: 256, 384 and 512 bits.")

        app_size += rps_consts.RPS_SIGNATURE_SIZE


    # Start building the RPS image
    rps_image : rps.RPS = rps.RPS()

    rps_image.header.set_control_flags(
        is_m4_image    = True,
        is_encrypted   = apply_encryption,
        mic_protected  = apply_mic,
        is_signed      = apply_signature,
        is_psram_image = is_psram_app,
    )
    rps_image.header.set_signature_type(signature_type)
    rps_image.header.set_image_size(app_size)
    rps_image.header.set_version(app_version, fw_info)

    address_to_put_in_header = flash_start_addr - rps_consts.RPS_M4_FLASH_ADDRESS_BASE - rps_consts.RPS_FULL_HEADER_SIZE
    if address_to_put_in_header < 0:
        _parser.error("Application start address is not within the flash address range.")
    rps_image.header.set_address(flash_start_addr - rps_consts.RPS_M4_FLASH_ADDRESS_BASE - rps_consts.RPS_FULL_HEADER_SIZE)

    # Set the first (and only) boot descriptor
    boot_descriptor_0_controlLength       : int = 0
    boot_descriptor_0_destination_address : int = 0
    if is_psram_app:
        rps_image.boot_descriptor.set_ivt_offset(address)
        boot_descriptor_0_controlLength       = len(app_data) + rps_consts.RPS_FULL_HEADER_SIZE + (rps_consts.RPS_SIGNATURE_SIZE if apply_signature else 0)
        boot_descriptor_0_destination_address = address - rps_consts.RPS_FULL_HEADER_SIZE + rps_consts.RPS_HEADER_SIZE
    else:
        rps_image.boot_descriptor.set_ivt_offset(flash_start_addr)
        boot_descriptor_0_controlLength       = 0
        boot_descriptor_0_destination_address = 0

    rps_image.boot_descriptor.set_boot_descriptor_offset(0)
    rps_image.boot_descriptor.boot_descriptor_entries[0].set_length(boot_descriptor_0_controlLength)
    rps_image.boot_descriptor.boot_descriptor_entries[0].set_destination_address(boot_descriptor_0_destination_address)
    rps_image.boot_descriptor.boot_descriptor_entries[0].set_last_entry(True)

    rps_image.application.set_image(app_data)
    if not rps_image.application.calculate_and_set_checksum():
        _parser.error("Failed to calculate the checksum of the application image.")


    # Apply security features
    if apply_mic:
        print("Calculating MIC of image...")
        data : bytes = rps_image.get_binary_data()
        mic  : bytes = rps_crypto.calculate_mic(data, mic_key, iv)
        rps_image.header.set_mic(mic)
    else:
        print("Calculating CRC of image...")
        crc_value : int = rps_crc.crc32(rps_image.get_binary_data())
        rps_image.header.set_crc(crc_value)

    # Collect the data we're about to write to file
    data : bytearray = bytearray(rps_image.get_binary_data())

    if apply_encryption:
        print("Encrypting image...")

        # The header is not to be encrypted; start from the boot descriptors
        encrypted_data : bytes = rps_crypto.encrypt(data[rps_consts.RPS_HEADER_SIZE:], enc_key)

        data[rps_consts.RPS_HEADER_SIZE:] = encrypted_data

    if apply_signature:
        print("Signing image...")

        if apply_mic:
            # The signature is of the RPS header only (which the MIC is part of)
            data_to_sign = data[:rps_consts.RPS_HEADER_SIZE]
        else:
            data_to_sign = data

        signature : bytes = rps_crypto.sign(data_to_sign, sign_key, sha_size)

        data += signature


    # Write the RPS image to file
    if os.path.dirname(output_filename) != '' and not os.path.exists(os.path.dirname(output_filename)):
        os.makedirs(os.path.dirname(output_filename))

    with open(output_filename, "wb") as f:
        f.write(data)

    print(f"RPS image written to '{output_filename}'.")


if __name__ == '__main__':
    main()
