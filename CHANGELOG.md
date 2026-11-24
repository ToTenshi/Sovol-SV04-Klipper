# Changelog

All notable changes to this project. Format based on [Keep a Changelog](https://keepachangelog.com/),
newest version first.

## [Unreleased]

### Installation
- New: `install/sv04-pi-setup.sh`, a SV04 setup on a fresh MainsailOS without KIAUH: backup, config,
  STM32/GD32, serial port, firmware build without `make menuconfig` (checks the Kconfig options),
  optional Bully85 fork for the display and KlipperScreen with its official installer, restart.
  `--update` refreshes only the macro files and keeps `printer.cfg`/`variables.cfg`.
- New: slicer installers for all systems: `install/install-slicer-profiles.sh` (Linux + macOS,
  including Flatpak) and `install/install-slicer-profiles-windows.cmd` / `.ps1` (Windows).
  They install Bambu Studio, Cura 4/5 and PrusaSlicer (bundle split into user presets) including the
  bed model. They replace `sv04-bambu-install.sh` and `sv04-cura-install.sh`.
- Installation only via a fresh MainsailOS with the original Klipper. The pre-made custom image
  and the instructions for existing systems were removed.
- The printer firmware is built on the Pi with `make menuconfig`, with settings documented in
  the README: STM32F103, 28 KiB bootloader, 8 MHz, USART1 PA10/PA9, 115200 baud.
- The original Sovol display is optional: switch to the Bully85 Klipper fork via `git` and use
  `config/SV04-with-display`.

### Added
- Input shaping without a sensor: preset `input_shaper.cfg` (X EI 40 Hz, Y EI 30 Hz), set per
  carriage at runtime (start, T0/T1, COPY/MIRROR). `INPUT_SHAPER_SET`, `INPUT_SHAPER_STATUS`.
- Optional ADXL345 measurement per carriage with `SHAPER_CALIBRATE_SV04` (stored in
  `variables.cfg`), buttons in `SV04_MENU`. `SAVE_CONFIG` is blocked while measured shaper values
  are pending, because they would stop original Klipper from starting with dual_carriage.
- `sv04_tools.cfg` with `SV04_MENU` (button menu for Mainsail ≥ 2.9 / Fluidd ≥ 1.27),
  `Z_OFFSET_CALIBRATE`, `CALIBRATE_T1_Z`, `SAVE_Z_OFFSET`, `Z_TILT_HOME`, `BED_LEVEL_SCREWS`,
  `PID_TUNE_BED`, `PID_TUNE_HOTEND`, `LOAD_FILAMENT`, `UNLOAD_FILAMENT`.
- Z offset of the right nozzle (`dual_z_offset` in `variables.cfg`), set with `SET_T1_OFFSET X= Y= Z=`.
- Prompt for SAVE_CONFIG at the end of a print when changed values are pending.
- Bambu Studio profiles (5 printers, 4 qualities, 4 filaments) with generator and Linux installer.
- `CHANGELOG.md`, `docs/Kalibrierung-Calibration.md`.
- `wiki/`: knowledge base following the LLM Wiki pattern (raw sources in `wiki/sources/`, topic pages,
  index, log, lint rules). `LLM-WIKI.md` now only points there.
- `tools/check_klipper_config.py`: static check of both config folders (parser, Jinja, variables, `{-` trap, consistency).
- `.gitattributes`: CRLF for `.cmd`/`.ps1`, LF for `.sh`.

### Changed
- `max_accel` 1000 → 1500 mm/s² (fork: `max_accel_to_decel` 500 → 750). Cura 600 → 1500 mm/s².
  Bambu Studio: accelerations to 1500 and speeds raised slightly (inner walls 80, infill 100, travel 200 mm/s).
- `adxl345.cfg` no longer needs the `gcode_shell_command` extension or the fixed `/home/pi` path.
  The invalid option `shaper_freq_dc` was removed. `ADXL_X`/`ADXL_Y` remain as aliases.
- COPY/MIRROR: `START_PRINT` extends the bed mesh area to the second copy itself.
  Cura, PrusaSlicer and Bambu Studio limit the print area to 150 mm.
- T1 offsets are applied relatively on tool changes, so babysteps are kept.
  All G-code offsets are reset at the start of a print.
- `min_extrude_temp` changed from 1 to 170 °C.
- Original Klipper: `minimum_cruise_ratio: 0.5` instead of `max_accel_to_decel`. Added stub
  macros for `DGUS_PRINT_START`/`DGUS_PRINT_END`.
- `XY_offset_dual` is now an alias of `SET_T1_OFFSET`.
- PrusaSlicer bundle: removed 14 presets that were only compatible with Creality/Prusa printers.
  The bed model is set consistently.
- The Cura guide now uses the user folder (survives Cura updates).

### Fixed
- PAUSE and CLEAN_NOZZLE used the non-existent `printer.dual_carriage.mode`. Pausing in MIRROR
  mode could fail with "Move out of range".
- An X/Y offset of T1 was carried over into the next print.
- Prints in dual mode starting with T1 did not use the T1 offset.
- `[bed_screws]`: names of screw 2 and 4 were swapped.
- `SAVE_AT_END` set a variable that was never read (removed).

### Removed
- `config/old config`.
- `macro/shell_commands/adxl_*.sh` (no longer needed).
- `sv04-bambu-install.sh`, `sv04-cura-install.sh` (replaced by `install/`).

## [1.0.1] - 2023-09-26
- Fan bug fixed.

## [1.0.0] - 2023-09-24
- New config structure: `SV04-with-display` (Bully85 fork with display) and
  `Sv04-works-with origin-klipper`.
- Copy/Mirror fixes, new slicer start codes.

## [0.2.1] - 2023-04-20
- Support for the stock DGUS display, homing override (T0 before Z homing), new printer firmware.

## [0.1.1] - 2023-03-11
- First release: printer.cfg, IDEX macros, variables.cfg, KlipperScreen config.
