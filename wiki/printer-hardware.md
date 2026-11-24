# Printer hardware

- **MCU:** STM32F103xE (also a GD32 variant), 72 MHz, 8 MHz crystal, 28 KiB bootloader (app at
  0x08007000). Communication via USART1 PA10/PA9 at **115200** baud through a CH340 USB serial adapter
  (`/dev/serial/by-id/usb-1a86_USB_Serial-…`). DGUS display on USART3 PB11/PB10.
  Source: [firmware.bin dictionary](sources/2026-11-24_firmware-bin-dictionary.md).
- **Firmware options** (Kconfig, checked in the source of both Klipper versions):
  `CONFIG_MACH_STM32F103`, `CONFIG_STM32_FLASH_START_7000`, `CONFIG_STM32_CLOCK_REF_8M`,
  `CONFIG_STM32_SERIAL_USART1`, `CONFIG_SERIAL_BAUD=115200`. Display, fork only:
  `CONFIG_T5UID1_SERIAL`, `CONFIG_STM32_T5UID1_SERIAL_USART3_PB11_PB10` (needs `CONFIG_LOW_LEVEL_OPTIONS`).
  Source: [Klipper source](sources/2026-11-24_klipper-source-notes.md).
- **STM32 vs. GD32:** only the Z stepper pins differ (two blocks in `printer.cfg`, between the banners
  `Use this if yor Chip is STM32` / `… Giga Device GD32`). `sv04-pi-setup.sh --chip gd32` switches them.
- **Bed** 302 × 302, Z 400. X: carriage 0 `position_min -65` (endstop -65), `dual_carriage` endstop/max 360.
- **Probe:** BLTouch `y_offset: 25`. Homing via `[homing_override]`, always with T0, centre 150.5/150.5.
- **Limits:** `max_velocity 300`, `max_accel 1500` (only with [input shaping](input-shaper.md), previously 1000).
- **Fans:** part cooling `fan_generic fanX1` (T0) / `fanX2` (T1). `M106`/`M107` are macros (`M106 P1` → fanX2).
- `min_extrude_temp: 170` (was 1). `idle_timeout` 7200 s (M600 pauses must not cool down).
