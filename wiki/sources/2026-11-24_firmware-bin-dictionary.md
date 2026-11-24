# Data dictionary of `Firmware bin/firmware.bin`

**Method:** search the binary for a zlib stream (`0x78 0x01/0x5e/0x9c/0xda`), decompress it and read it
as JSON. The reset vector (second word of the vector table) shows the start address.

**Result (2026-11-24):**

- `version`: `v0.11.0-261-gffa46e48` (Bully85 fork)
- `build_versions`: `gcc: (15:8-2019-q3-1+b1) 8.3.1 20190703 … binutils: 2.35.2`
- `MCU`: `stm32f103xe`, `CLOCK_FREQ`: 72000000
- `SERIAL_BAUD`: 115200, `RESERVE_PINS_serial`: `PA10,PA9`
- `RESERVE_PINS_t5uid1`: `PB11,PB10`
- Vector table: SP `0x20002800`, reset `0x08007185` → app at `0x08007000` = **28 KiB bootloader**
