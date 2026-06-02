/***************************************************************************//**
 * GCC/CMake Linker script for Silicon Labs devices
 *******************************************************************************
 * # License
 * <b>Copyright 2020 Silicon Laboratories Inc. www.silabs.com</b>
 *******************************************************************************
 *
 * SPDX-License-Identifier: Zlib
 *
 * The licensor of this software is Silicon Laboratories Inc.
 *
 * This software is provided 'as-is', without any express or implied
 * warranty. In no event will the authors be held liable for any damages
 * arising from the use of this software.
 *
 * Permission is granted to anyone to use this software for any purpose,
 * including commercial applications, and to alter it and redistribute it
 * freely, subject to the following restrictions:
 *
 * 1. The origin of this software must not be misrepresented; you must not
 *    claim that you wrote the original software. If you use this software
 *    in a product, an acknowledgment in the product documentation would be
 *    appreciated but is not required.
 * 2. Altered source versions must be plainly marked as such, and must not be
 *    misrepresented as being the original software.
 * 3. This notice may not be removed or altered from any source distribution.
 *
 ******************************************************************************/


 MEMORY
 {
   ?!?!?!?!?  (rx)  : ORIGIN = 0x8202000, LENGTH = 0x1fe000
   DUMMY (!ax) : ORIGIN = 0xffe02000, LENGTH = 0x1fe000

   ram   (rwx) : ORIGIN = 0x400, LENGTH = 0x2f800
   psram (rwx) : ORIGIN = 0xa001000, LENGTH = 0x7ff000
 }
 MEMORY
 {
   udma0   (rwx)  : ORIGIN = 0x2fc00, LENGTH = 0x400
   udma1   (rwx)  : ORIGIN = 0x24061c00, LENGTH = 0x400
 }
/*******************************************************************************
 * Program headers: explicit PT_LOAD with correct p_flags so the linker does not
 * apply wrong access flags when a single flash region holds both executable and
 * read-only data. ELF p_flags: 4=read, 5=read+execute, 6=read+write.
 *
 * When ram_execution is set, output section text_ram (VMA in RAM, LMA in flash)
 * follows the usual ramfunc pattern: startup copies (or uses tables) before .data init.
 ******************************************************************************/
PHDRS
{
  vectors PT_LOAD FLAGS(4);      /* Flash: vector table (separate segment so ram_code LMA doesn't overlap) */
  readonly PT_LOAD FLAGS(4);     /* Flash: .rodata */
  text PT_LOAD FLAGS(5);         /* Flash: executable code, unwind tables */
  tables PT_LOAD FLAGS(4);       /* Flash: .copy.table / .zero.table */
  ram_code PT_LOAD FLAGS(5);     /* RAM: executable code copied from flash (ram_execution) */
  ram_classified PT_LOAD FLAGS(6); /* PSRAM: classified text+data (VMA in PSRAM, copied to RAM at startup) */
  ram_data PT_LOAD FLAGS(6);     /* RAM: .data (init values only) AT>rom */
}
_last_psram_location = ORIGIN(psram);
_last_ram_location = ORIGIN(ram);

ENTRY(Reset_Handler)
 
SECTIONS
{
 .vectors :
 {
  KEEP(*(.isr_vector))
  . = ALIGN(32);
  _last_psram_location = .;
 } > psram :vectors
 /*-----------------------------------------------------------------------
  * PSRAM+LLVM: text_ram init data is placed at a PSRAM VMA so that the
  * resulting PT_LOAD segment stays within the PSRAM address range.
  * Commander's create_rps uses the ELF address span to build the RPS
  * image; a PT_LOAD at the low RAM VMA (0x400) would push the span
  * above 100 MB and fail.  The startup copy_functions_to_ram() routine
  * copies from __lma_ramfuncs_start__ (PSRAM) to __ramfuncs_start__
  * (RAM) using linker symbols, so the init data is still available in
  * RAM at runtime.
  *---------------------------------------------------------------------*/
 text_ram _last_psram_location : {
  . = ALIGN(4);
  *(text_application_ram)
  *(text_core_*timecritical*)
  *(text_sleeptimer_*timecritical*)
  *(text_cmsis_udma_*timecritical*)
  *(text_psram_core_*timecritical*)
  *(text_rsilib_chip_*timecritical*)
  *(text_rsilib_dcache_*timecritical*)
  *(text_rsilib_egpio_*timecritical*)
  *(text_rsilib_qspi_*timecritical*)
  *(text_rsilib_sysrtc_*timecritical*)
  *(text_si91x_tickless_*timecritical*)
  *(text_sl_clock_manager_*timecritical*)
  *(text_sl_power_manager_*timecritical*)
  *(text_sleeptimer_si91x_*timecritical*)
  *(text_systemlevel_pll_*timecritical*)
  *(text_si91x_wireless_*timecritical*)
  *(text_sli_hal_si91x_*timecritical*)
  *(text_sli_routing_utility_*timecritical*)
  *(text_sli_si91x_wifi_cmd_engine_*timecritical*)
  *(text_freertos_kernel_*timecritical*)
  */sl_si91x_psram.*(.data*)
  */sl_si91x_psram_handle.*(.data*)
  */rsi_deepsleep_soc.*(.data*)
  */rsi_egpio.*(.data*)
  */rsi_qspi.*(.data*)
  */sli_si91x_clock_manager.*(.data*)
  */sl_si91x_power_manager.*(.data*)
  */rsi_pll.*(.data*)
  *(.common_ipmu_ram*)
  . = ALIGN(512);
  KEEP(*(.ramVector))
  . = ALIGN(4);
  _last_psram_location = .;
 } > psram :ram_code

 __lma_ramfuncs_start__ = ADDR(text_ram);
 __lma_ramfuncs_end__ = ADDR(text_ram) + SIZEOF(text_ram);
 __ramfuncs_start__ = _last_ram_location;
 __ramfuncs_end__ = _last_ram_location + SIZEOF(text_ram);
 _last_ram_location = __ramfuncs_end__;
 __text_core_ram_start__ = __ramfuncs_start__;
 __text_core_ram_end__ = __ramfuncs_end__;
 __text_sleeptimer_ram_start__ = __ramfuncs_start__;
 __text_sleeptimer_ram_end__ = __ramfuncs_end__;
 __text_cmsis_udma_ram_start__ = __ramfuncs_start__;
 __text_cmsis_udma_ram_end__ = __ramfuncs_end__;
 __text_psram_core_ram_start__ = __ramfuncs_start__;
 __text_psram_core_ram_end__ = __ramfuncs_end__;
 __text_rsilib_chip_ram_start__ = __ramfuncs_start__;
 __text_rsilib_chip_ram_end__ = __ramfuncs_end__;
 __text_rsilib_dcache_ram_start__ = __ramfuncs_start__;
 __text_rsilib_dcache_ram_end__ = __ramfuncs_end__;
 __text_rsilib_egpio_ram_start__ = __ramfuncs_start__;
 __text_rsilib_egpio_ram_end__ = __ramfuncs_end__;
 __text_rsilib_qspi_ram_start__ = __ramfuncs_start__;
 __text_rsilib_qspi_ram_end__ = __ramfuncs_end__;
 __text_rsilib_sysrtc_ram_start__ = __ramfuncs_start__;
 __text_rsilib_sysrtc_ram_end__ = __ramfuncs_end__;
 __text_si91x_tickless_ram_start__ = __ramfuncs_start__;
 __text_si91x_tickless_ram_end__ = __ramfuncs_end__;
 __text_sl_clock_manager_ram_start__ = __ramfuncs_start__;
 __text_sl_clock_manager_ram_end__ = __ramfuncs_end__;
 __text_sl_power_manager_ram_start__ = __ramfuncs_start__;
 __text_sl_power_manager_ram_end__ = __ramfuncs_end__;
 __text_sleeptimer_si91x_ram_start__ = __ramfuncs_start__;
 __text_sleeptimer_si91x_ram_end__ = __ramfuncs_end__;
 __text_systemlevel_pll_ram_start__ = __ramfuncs_start__;
 __text_systemlevel_pll_ram_end__ = __ramfuncs_end__;
 __text_si91x_wireless_ram_start__ = __ramfuncs_start__;
 __text_si91x_wireless_ram_end__ = __ramfuncs_end__;
 __text_sli_hal_si91x_ram_start__ = __ramfuncs_start__;
 __text_sli_hal_si91x_ram_end__ = __ramfuncs_end__;
 __text_sli_routing_utility_ram_start__ = __ramfuncs_start__;
 __text_sli_routing_utility_ram_end__ = __ramfuncs_end__;
 __text_sli_si91x_wifi_cmd_engine_ram_start__ = __ramfuncs_start__;
 __text_sli_si91x_wifi_cmd_engine_ram_end__ = __ramfuncs_end__;

 .rodata : ALIGN(32)
 {
  *(.rodata*)
  *(.rodata.*)
  _last_psram_location = .;
 } > psram :readonly

 .text :
 {
  KEEP(*(.reset_handler))
  *(SORT_BY_ALIGNMENT(.text*))
  KEEP(*(.init))
  KEEP(*(.fini)) 

  /* .ctors */
  */crtbegin.*(.ctors)
  */crtbegin?.*(.ctors)
  *(EXCLUDE_FILE(*/crtend?.* */crtend.*) .ctors)
  *(SORT(.ctors.*))
  *(.ctors)
  
  /* .dtors */
  */crtbegin.*(.dtors)
  */crtbegin?.*(.dtors)
  *(EXCLUDE_FILE(*/crtend?.* */crtend.*) .dtors)
  *(SORT(.dtors.*))
  *(.dtors)
  
  KEEP(*(.eh_frame*))
  _last_psram_location = .;
 } > psram :text 
 
 .common_tcm_code :
 {
  *(.common_tcm_code*)
  _last_psram_location = .;
 } > psram :text

 .ARM.extab : 
 {
  *(.ARM.extab* .gnu.linkonce.armextab.*)
  _last_psram_location = .;
 } > psram :text
 
 __exidx_start = .;
 .ARM.exidx :
 {
  *(.ARM.exidx* .gnu.linkonce.armexidx.*)
  _last_psram_location = .;
 } > psram :text 
 __exidx_end = .;
 .copy.table :
 {
  __copy_table_start__ = .;
  __copy_table_end__ = .;
 } > psram :tables

 .zero.table :
 {
  __zero_table_start__ = .;
  __zero_table_end__ = .;
 } > psram :tables

 __etext = .; 
 

 

  .classified_text _last_psram_location :
  {
      . = ALIGN(4);
      *(text_*)
      . = ALIGN(4);
      _last_psram_location = .;
  } > psram :ram_classified

  _classified_text_ = ADDR(.classified_text);
  _classified_text_section_start_ = _last_ram_location;
  _classified_text_section_end_ = _last_ram_location + SIZEOF(.classified_text);
  _last_ram_location = _classified_text_section_end_;

  .classified_data _last_psram_location :
  {
      . = ALIGN(4);
      *(data_*)
      . = ALIGN(4);
      _last_psram_location = .;
  } > psram :ram_classified

  _classified_data_ = ADDR(.classified_data);
  _classified_data_section_start_ = _last_ram_location;
  _classified_data_section_end_ = _last_ram_location + SIZEOF(.classified_data);
  _last_ram_location = _classified_data_section_end_;
 .data : ALIGN(8)
 
 {
  __data_start__ = .;
  
  /* _sdata is used in startup code */
  _sdata = __data_start__;
  *(.data*)
  /* ipmu calibration data */
  *(.common_ipmu_ram*)
    
  . = ALIGN(4);
  /* preinit data */
  PROVIDE_HIDDEN (__preinit_array_start = .);
  KEEP(*(.preinit_array))
  PROVIDE_HIDDEN (__preinit_array_end = .);
  
  . = ALIGN(4);
  /* init data */
  
  PROVIDE_HIDDEN (__init_array_start = .);
  KEEP(*(SORT(.init_array.*)))
  KEEP(*(.init_array))
  PROVIDE_HIDDEN (__init_array_end = .);
  
  . = ALIGN(4);
  /* finit data */
  PROVIDE_HIDDEN (__fini_array_start = .);
  KEEP(*(SORT(.fini_array.*)))
  KEEP(*(.fini_array))
  PROVIDE_HIDDEN (__fini_array_end = .);
  
  KEEP(*(.jcr*))
  . = ALIGN(4);
  /* All data end */
  __data_end__ = .;
  
  /* _edata is used in startup code */
  _edata = __data_end__;
  _last_psram_location = .;
 } > psram :ram_data
 _sidata = LOADADDR(.data);

 .classified_bss _last_psram_location (NOLOAD) :
 {
  _classified_bss_section_start_ = .;
  
  . = ALIGN(4);
  *(bss_to_psram*)
  
  _classified_bss_section_end_ = .;
  _last_psram_location = .;
 } > psram :NONE

 .bss _last_ram_location (NOLOAD) :
 {
  . = ALIGN(8);
  __bss_start__ = .;
  *(.bss*)
  *(COMMON)
  . = ALIGN(4);
  __bss_end__ = .;
  _last_ram_location = .;   
 } > ram :NONE
  
 .stack _last_ram_location (NOLOAD):
 {
  __StackLimit = .;
  KEEP(*(.stack*))
  . = ALIGN(4);
  __StackTop = .;
  PROVIDE(__stack = __StackTop); 
  _last_ram_location = .;
 } > ram :NONE
 /* RAM overflow detection (only valid when stack is in RAM) */
 __current_ram_used = . - ORIGIN(ram);
 __ram_total = LENGTH(ram);
 __ram_remaining = __ram_total - __current_ram_used;
 
 ASSERT((. <= (ORIGIN(ram) + LENGTH(ram))), "RAM OVERFLOW: RAM usage exceeds available memory region")
 ASSERT((__ram_remaining >= 1024), "WARNING: Less than 1KB RAM left for heap - application may run out of dynamic memory")
 ASSERT((__StackLimit >= __bss_end__), "CRITICAL: Stack overlaps with BSS section - increase RAM or reduce static allocation")

 __ram_start__ = ORIGIN(ram);
 __ram_end__   = ORIGIN(ram) + LENGTH(ram);

   .heap _last_ram_location (NOLOAD):
   {
  . = ALIGN(8);
  __HeapBase = .;
  __end__ = .;
  end = __end__;
  _end = __end__;
  KEEP(*(.heap*)) 
  . = ORIGIN(ram) + LENGTH(ram);
    
  __HeapLimit = .;
   } > ram :NONE
 __heap_size = __HeapLimit - __HeapBase;

 /* Final heap validation */
 ASSERT((__heap_size >= 0), "CRITICAL: Heap region is invalid (negative size) - stack and heap are overlapping")
 .udma_addr0 (NOLOAD) :
 {
  *(.udma_addr0*)
 } > udma0 :NONE

 .udma_addr1 (NOLOAD) :
 {
  *(.udma_addr1*)
 } > udma1 :NONE 
  /* nvm3 enable*/  /* Flash Present*/  /* littlefs_enable */  /* Flash Present */

 .debug_misc 0 : { *(.debug_*); *(.zdebug_*); }
}
 
