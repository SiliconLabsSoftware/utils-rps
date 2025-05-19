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

RPS_HEADER_MAGIC                 = 0x900D900D
RPS_HEADER_SIZE                  =         64
RPS_FULL_HEADER_SIZE             =       4096

RPS_BOOT_DESCRIPTOR_MAGIC        = 0x5AA5
RPS_BOOT_DESCRIPTOR_SIZE         =     64
RPS_BOOT_DESCRIPTOR_PADDING_SIZE = RPS_FULL_HEADER_SIZE - RPS_BOOT_DESCRIPTOR_SIZE - RPS_HEADER_SIZE

RPS_NUM_BOOT_DESCRIPTOR_ENTRIES  = 7
RPS_BOOT_DESCRIPTOR_ENTRY_SIZE   = 8

RPS_M4_FLASH_ADDRESS_BASE        = 0x08000000
RPS_PSRAM_ADDRESS_BASE           = 0x0A000000

RPS_APP_VALIDATION_MAGIC         = 0x10AD10AD

RPS_SIGNATURE_SIZE               = 72
RPS_SIGNATURE_TYPE_NONE          = 0
RPS_SIGNATURE_TYPE_SHA256        = 1
RPS_SIGNATURE_TYPE_SHA384        = 2
RPS_SIGNATURE_TYPE_SHA512        = 3

RPS_MIC_SIZE                     = 16
