# RPS Image Creation and Conversion Tools

[![Tests](https://github.com/SiliconLabsSoftware/utils-rps/actions/workflows/unittest.yml/badge.svg)](https://github.com/SiliconLabsSoftware/utils-rps/actions/workflows/unittest.yml)

_Create and convert RPS images for Silicon Labs SiWx91x devices in a breeze!_

## Introduction

SiWx91x devices require application images to be converted into RPS images before they can be flashed to the device. The conversion from an application binary to an RPS image includes prepending a header to the application image. This header adds certain metadata to the application, including version numbers, control flags, size information, as well as other instructions to the device's bootloader.

The `rps-create` tool can be used to create RPS images from M4 application binaries, including adding security features like encryption and signing. By default, a CRC protects the RPS' integrity, however MIC protection can be used instead.

The `rps-convert` tool can be used to convert _existing_ unsigned/unencrypted (M4 or NWP) RPS images into signed/encrypted RPS images. Changing into MIC integrity protection is also available.

## Requirements

This tool was developed using Python 3.10. Required PyPI packages are:

- `intelhex`, for parsing Intel HEX-formatted (.hex) application images
- `pycryptodome`, for encryption functionality

## Installation

```console
pip install silabs-rps
```

## Usage

Help text along with descriptions of each option can be shown by providing the `-h` or `--help` flags.

### Create RPS Images

```console
rps-create <output filename> --app <filename> 
        [--map <filename>] [--address <address>] [--app-version <version>] 
        [--fw-info <firmware info>] [--sign <filename>] [--sha <size>] 
        [--encrypt <filename>] [--mic <filename>] [--iv <filename>] 
```

Available options:

- `<output filename>` (_required_)
  - Name of the output RPS image file
- `--app <filename>` (_required_)
  - Name of the application filename to convert into RPS file. Must be in .bin or .hex format
- `--map <filename>` (_optional, but recommended if your application is to be placed in PSRAM_)
  - Name of the map file (.map) from the compilation of the provided application. Used for determining flash start address
- `--address <address>` (_required if the application file provided with --app is a .bin file, optional otherwise_)
  - Application start address. Both decimal and hexadecimal (prefixed by 0x) values are interpreted
- `--app-version <version number>` (_optional_)
  - Application version number. Both decimal and hexadecimal (prefixed by 0x) values are interpreted
- `--fw-info <firmware info>` (_optional_)
  - Additional version information. Both decimal and hexadecimal (prefixed by 0x) values are interpreted
- `--sign <key filename>` (_optional_)
  - Sign the RPS image using the provided (NIST P-256) private key, and append the signature (72 bytes) to the RPS image. The key must be in .pem or .der format
- `--sha <size>` (_optional_)
  - Use SHA-\<size\> for signing the RPS image. Supported options are 256 (default), 384, and 512 bits
- `--encrypt <key filename>` (_optional_)
  - Encrypt the application image using AES ECB encryption. Key must be 32 bytes, and must be formatted as .bin or .txt (as a string of hexadecimal characters)
- `--mic <key filename>` (_optional_)
  - Use MIC (AES CBC-MAC) based integrity check instead of CRC to protect the RPS image. Key must be 32 bytes, and must be formatted as .bin or .txt (as a string of hexadecimal characters)
- `--iv <iv filename>` (_optional_)
  - Custom initialization vector (IV) for the MIC calculation. IV must be 16 bytes, and must be formatted as .bin or .txt (as a string of hexadecimal characters). If no IV is provided, the default IV will be used.

#### Usage Examples

Here follows some examples on how to use `rps-create`.

##### Create an RPS Image From a .bin Application Image Using CRC Integrity Protection

```console
rps-create my_rps.rps --app my_app.bin --address 0x08212000
```

##### Create an RPS Image From a .hex Application Image Using CRC Integrity Protection

The application start address is encoded in the file, so the `--address` option must be omitted.

```console
rps-create my_rps.rps --app my_app.hex
```

##### Create an RPS Image to be Placed in PSRAM

```console
rps-create my_rps.rps --app my_app.bin --address 0x0A012000 --map my_map.map
```

Note: The provided .map file must correspond to the provided application.

##### Create an RPS Image With MIC Integrity Protection

```console
rps-create my_rps.rps --app my_app.hex --mic my_key.txt --iv my_iv.txt
```

Note: The provided MIC key must match the `M4_OTA_KEY` stored on the device for the device to be able to verify the MIC.

##### Create an Encrypted RPS Image

```console
rps-create my_rps.rps --app my_app.hex --encrypt my_key.txt
```

Note: The provided encryption key must match the `M4_OTA_KEY` stored on the device for the device to be able decrypt the RPS image.

##### Create a Signed RPS Image, Using SHA-384 Hashing

```console
rps-create my_rps.rps --app my_app.hex --sign my_private_key.pem --sha 384
```

Note: The provided private key must match the `M4_PUBLIC_KEY` stored on the device for the device to be able to verify the signature of the RPS image.

### Convert RPS Images

```console
rps-convert <output filename> --rps <filename> 
        [--sign <filename>] [--sha <size>]
        [--encrypt <filename>] 
        [--mic <filename>] [--iv <filename>]
```

Available options:

- `<output filename>` (_required_)
  - Name of the output RPS image file
- `--rps <filename>` (_required_)
  - Name of the application filename to convert into RPS file. Must be in .bin or .hex format
- `--sign <key filename>` (_optional_)
  - Sign the RPS image using the provided (NIST P-256) private key, and append the signature (72 bytes) to the RPS image. The key must be in .pem or .der format
- `--sha <size>` (_optional_)
  - Use SHA-\<size\> for signing the RPS image. Supported options are 256 (default), 384, and 512 bits
- `--encrypt <key filename>` (_optional_)
  - Encrypt the application image using AES ECB encryption. Key must be 32 bytes, and must be formatted as .bin or .txt (as a string of hexadecimal characters)
- `--mic <key filename>` (_optional_)
  - Use MIC (AES CBC-MAC) based integrity check instead of CRC to protect the RPS image. Key must be 32 bytes, and must be formatted as .bin or .txt (as a string of hexadecimal characters)
- `--iv <iv filename>` (_optional_)
  - Custom initialization vector (IV) for the MIC calculation. IV must be 16 bytes, and must be formatted as .bin or .txt (as a string of hexadecimal characters). If no IV is provided, the default IV will be used.

#### Usage Examples

Here follows some examples on how to use `rps-convert`.

##### Sign RPS Image

```console
rps-convert my_signed_rps.rps --rps my_rps.rps --sign my_key.pem
```

##### Encrypt RPS Image

```console
rps-convert my_encrypted_rps.rps --rps my_rps.rps --encrypt my_key.bin
```

##### Enable MIC Integrity Protection in RPS Image

```console
rps-convert my_mic_rps.rps --rps my_rps.rps --mic my_key.bin --iv my_iv.bin
```
