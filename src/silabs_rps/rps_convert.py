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

rps_convert.py - Convert a non-secure RPS file into a signed/encrypted RPS file

Copyright: 2025, Silicon Laboratories Inc.
Version: 1.0.3

Usage:
    rps_convert <output filename> --rps <filename> [--sign <filename>] [--sha <size>] [--encrypt <filename>] [--mic <filename>] [--iv <filename>]

Options:
    <output filename>    Output RPS file.
    --rps <filename>     Input RPS file.
    --sign <filename>    Sign the RPS image using ECDSA. Key must be in .pem or .der format.
    --sha <size>         Use SHA-<size> for ECDSA. Available: 256 (default), 384 and 512 bits.
    --encrypt <filename> Encrypt the RPS image using AES ECB encryption. Key must be in .bin or .txt format.
    --mic <filename>     Use MIC (AES CBC-MAC) based integrity check instead of CRC. Key must be in .bin or .txt format.
    --iv <filename>      Initialization vector for MIC calculation. Must be in .bin or .txt format.

Examples:
    $ python rps_convert.py my_secure_image.rps --rps my_image.rps --sign my_key.pem --sha 256

"""
import argparse
import os

from . import rps
from . import rps_helpers
from . import rps_consts
from . import rps_crc
from . import rps_crypto


_parser = argparse.ArgumentParser(
    prog="rps_convert",
    description="Convert a non-secure RPS file into a signed/encrypted RPS file."
)

_parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0.3")
_parser.add_argument("output",        type=str,                   metavar="<output filename>",                             help="Output RPS file.")
_parser.add_argument("--rps",         type=str,                   metavar="<filename>",        required=True,              help="Input RPS file.")
_parser.add_argument("--sign",        type=str,                   metavar="<filename>",                                    help="Sign the RPS image using ECDSA. Key must be in .pem or .der format.")
_parser.add_argument("--sha",         type=int,                   metavar="<size>",                           default=256, help="Use SHA-<size> for ECDSA. Available: 256 (default), 384 and 512 bits.")
_parser.add_argument("--encrypt",     type=str,                   metavar="<filename>",                                    help="Encrypt the RPS image using AES ECB encryption. Key must be in .bin or .txt format.")
_parser.add_argument("--mic",         type=str,                   metavar="<filename>",                                    help="Use MIC (AES CBC-MAC) based integrity check instead of CRC. Key must be in .bin or .txt format.")
_parser.add_argument("--iv",          type=str,                   metavar="<filename>",                                    help="Initialization vector for MIC calculation. Must be in .bin or .txt format.")


def main():
    _args = _parser.parse_args()

    output_filename  : str         = _args.output
    input_filename   : str         = _args.rps
    apply_signature  : bool        = _args.sign is not None
    sign_filename    : str  | None = _args.sign
    sha_size         : int         = _args.sha
    apply_encryption : bool        = _args.encrypt is not None
    encrypt_filename : str  | None = _args.encrypt
    apply_mic        : bool        = _args.mic is not None
    mic_filename     : str  | None = _args.mic
    iv_filename      : str  | None = _args.iv

    signature_type : int          = rps_consts.RPS_SIGNATURE_TYPE_NONE
    mic_key        : bytes | None = None
    iv             : bytes | None = None
    enc_key        : bytes | None = None
    sign_key       : bytes | None = None

    # Parse the input RPS file
    print(f"Reading RPS file '{input_filename}'...")
    if not rps_helpers.is_rps_file(input_filename):
        _parser.error(f"Input file '{input_filename}' is not an RPS file.")

    rps_data = rps_helpers.read_rps_file(input_filename)
    rps_file = rps.RPS()
    rps_file.set_binary_data(rps_data)

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

        # Parse the sha size
        if sha_size == 256:
            signature_type = rps_consts.RPS_SIGNATURE_TYPE_SHA256
        elif sha_size == 384:
            signature_type = rps_consts.RPS_SIGNATURE_TYPE_SHA384
        elif sha_size == 512:
            signature_type = rps_consts.RPS_SIGNATURE_TYPE_SHA512
        else:
            _parser.error("Invalid SHA size. Available: 256, 384 and 512 bits.")

    is_m4_image, is_encrypted, _, is_signed, is_psram_image = rps_file.header.get_control_flags()

    if is_signed:
        _parser.error("The input RPS file is already signed. Cannot sign it again.")

    if is_encrypted:
        _parser.error("The input RPS file is already encrypted. Cannot encrypt it again.")

    if len(rps_data) % 4 != 0:
        # Regardless of security features, the RPS file must be word-aligned
        rps_data += bytes(4 - len(rps_data) % 4)

    if (apply_mic or apply_encryption) and not len(rps_data) % 16 == 0:
        print(f"Warning: The RPS file size is not a multiple of 16 bytes, which is required for encryption and MIC calculation. Padding with zeroes.")
        rps_data += bytes(16 - len(rps_data) % 16)

    rps_file.set_binary_data(rps_data)
    rps_file.header.set_image_size(len(rps_data) - rps_consts.RPS_HEADER_SIZE)

    rps_file.header.set_control_flags(is_m4_image, apply_encryption, apply_mic, apply_signature, is_psram_image)

    if apply_signature:
        rps_file.header.set_image_size(rps_file.header.image_size + rps_consts.RPS_SIGNATURE_SIZE)
        rps_file.header.set_signature_type(signature_type)

        if is_psram_image:
            last_boot_descriptor_index = rps_file.boot_descriptor.get_last_entry_index()
            if last_boot_descriptor_index < 0:
                _parser.error("No boot descriptor found in the RPS file.")

            destination_address = rps_file.boot_descriptor.boot_descriptor_entries[last_boot_descriptor_index].destination_address
            if (destination_address & rps_consts.RPS_PSRAM_ADDRESS_BASE) == rps_consts.RPS_PSRAM_ADDRESS_BASE:
                # We need to update the control_length field in the last boot descriptor entry, so that the signature is copied to the correct location
                rps_file.boot_descriptor.boot_descriptor_entries[last_boot_descriptor_index].length += rps_consts.RPS_SIGNATURE_SIZE

    if is_m4_image:
        rps_file.application.calculate_and_set_checksum()

    # Clear any existing integrity checks
    rps_file.header.set_crc(0)
    rps_file.header.set_mic(bytes(rps_consts.RPS_MIC_SIZE))

        # Apply security features
    if apply_mic:
        print("Calculating MIC of image...")
        data : bytes = rps_file.get_binary_data()
        mic  : bytes = rps_crypto.calculate_mic(data, mic_key, iv)
        rps_file.header.set_mic(mic)
    else:
        print("Calculating CRC of image...")
        if len(rps_data) > 1024 * 1024:
            print("This might take a few seconds...")
        crc_value : int = rps_crc.crc32(rps_file.get_binary_data())
        rps_file.header.set_crc(crc_value)


    # Collect the data we're about to write to file
    data : bytearray = bytearray(rps_file.get_binary_data())

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


if __name__ == "__main__":
    main()
