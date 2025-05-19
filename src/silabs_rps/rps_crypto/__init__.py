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

RPS Crypto functions.

This file provides functions for calculating the MIC, encrypting data, and signing data.

This instance uses the pycryptodome package; you may provide the cryptography package of your choice
and reimplement any of these functions, as long as the function signatures remain the same.

"""
from Crypto.Cipher import AES
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256, SHA384, SHA512
from Crypto.Signature import DSS

from .. import rps_consts

INITIALIZATION_VECTOR = bytes("4" * 16, "utf-8")

def calculate_mic(data: bytes, key: bytes, iv: bytes | None = None) -> bytes:
    """
    Calculate the MIC (AES CBC-MAC) of the given data using the given key.
    NOTE: The data MUST be aligned to 16 bytes.
    NOTE: The IV must be 16 bytes.
    Returns the MIC as a bytes object.
    """
    if iv is None:
        iv = INITIALIZATION_VECTOR

    cipher = AES.new(key, AES.MODE_CBC, IV=iv)

    mic = cipher.encrypt(data)[-rps_consts.RPS_MIC_SIZE:]

    return mic


def encrypt(data: bytes, key: bytes) -> bytes:
    """
    Encrypt the given data using the given key.
    NOTE: The data MUST be aligned to 16 bytes.
    NOTE: The key must be 32 bytes.
    Returns the encrypted data as a bytes object.
    """
    cipher = AES.new(key, AES.MODE_ECB)

    encrypted_data = cipher.encrypt(data)

    return encrypted_data


def sign(data: bytes, key: bytes, sha_size : int = 256) -> bytes:
    """
    Sign the given data using the given key and the SHA size. Key can be either a PEM string or a DER-formatted bytearray.
    NOTE: Signature is padded to 72 bytes before returning.
    Returns the signature as a bytes object.
    """
    private_key = ECC.import_key(key)

    if sha_size == 256:
        hash_algorithm = SHA256
    elif sha_size == 384:
        hash_algorithm = SHA384
    elif sha_size == 512:
        hash_algorithm = SHA512
    else:
        raise ValueError("Invalid SHA size.")

    hash_obj = hash_algorithm.new(data)

    # Use deterministic-rfc6979 to ensure the same signature is generated every time
    signer = DSS.new(private_key, 'deterministic-rfc6979', encoding='der')

    signature = signer.sign(hash_obj)

    if len(signature) < rps_consts.RPS_SIGNATURE_SIZE:
        # Pad the signature with zeroes
        signature += b"\x00" * (rps_consts.RPS_SIGNATURE_SIZE - len(signature))

    return signature
