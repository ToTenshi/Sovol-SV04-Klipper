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
- Tidy macros in Mainsail: `install/mainsail_macro_groups.py` creates 5 macro panels (SV04, During print,
  Calibration, IDEX, Settings) with visibility per printer state, switches to expert mode, keeps your
  own groups, `--remove`. Included in `sv04-pi-setup.sh` (step 6, `--macros yes|no`).
- Input shaping without a sensor: preset `input_shaper.cfg` (X EI 40 Hz, Y EI 30 Hz), set per
  carriage at runtime (start, T0/T1, COPY/MIRROR). `INPUT_SHAPER_SET`, `INPUT_SHAPER_STATUS`.
- Optional ADXL345 measurement per carriage with `SHAPER_CALIBRATE_SV04` (stored in
  `variables.cfg`), buttons in `SOVOL_MENU`. `SAVE_CONFIG` is blocked while measured shaper values
  are pending, because they would stop original Klipper from starting with dual_carriage.
- `sv04_tools.cfg` with `SOVOL_MENU` (button menu for Mainsail ≥ 2.9 / Fluidd ≥ 1.27),
  `Z_OFFSET_CALIBRATE`, `CALIBRATE_Z_T1`, `SAVE_Z_OFFSET`, `Z_TILT_HOME`, `BED_LEVEL_SCREWS`,
  `PID_TUNE_BED`, `PID_TUNE_HOTEND`, `LOAD_FILAMENT`, `UNLOAD_FILAMENT`.
- Z offset of the right nozzle (`dual_z_offset` in `variables.cfg`), set with `SET_OFFSET_T1 X= Y= Z=`.
- Prompt for SAVE_CONFIG at the end of a print when changed values are pending.
- Bambu Studio profiles (5 printers, 4 qualities, 4 filaments) with generator and Linux installer.
- `CHANGELOG.md`, `docs/Kalibrierung-Calibration.md`.
- `wiki/`: knowledge base following the LLM Wiki pattern (raw sources in `wiki/sources/`, topic pages,
  index, log, lint rules). `LLM-WIKI.md` now only points there.
- `tools/simulate_z_offset.py`: simulates the Z offset paths (calibration, Mainsail panel, SAVE_Z_OFFSET,
  T1, restart) with Klipper's command parser. Every path must reach the same value.
- `tools/check_klipper_config.py`: static check of both config folders (parser, Jinja, variables, `{-` trap, consistency).
- `.gitattributes`: CRLF for `.cmd`/`.ps1`, LF for `.sh`.

### Changed
- `max_accel` 1000 → 1500 mm/s² (deceleration limit now Klipper's default = half). Cura 600 → 1500 mm/s².
  Bambu Studio: accelerations to 1500 and speeds raised slightly (inner walls 80, infill 100, travel 200 mm/s).
- `adxl345.cfg` no longer needs the `gcode_shell_command` extension or the fixed `/home/pi` path.
  The invalid option `shaper_freq_dc` was removed. `ADXL_X`/`ADXL_Y` remain as aliases.
- COPY/MIRROR: `START_PRINT` extends the bed mesh area to the second copy itself.
  Cura, PrusaSlicer and Bambu Studio limit the print area to 150 mm.
- T1 offsets are applied relatively on tool changes, so babysteps are kept.
  All G-code offsets are reset at the start of a print.
- `min_extrude_temp` changed from 1 to 170 °C.
- Original Klipper: added stub
  macros for `DGUS_PRINT_START`/`DGUS_PRINT_END`.
- `XY_offset_dual` is now an alias of `SET_OFFSET_T1`.
- PrusaSlicer bundle: removed 14 presets that were only compatible with Creality/Prusa printers.
  The bed model is set consistently.
- The Cura guide now uses the user folder (survives Cura updates).

### Fixed
- **First layer too high after Z calibration:** a measured z_offset only takes effect after
  SAVE_CONFIG/restart, and SAVE_CONFIG was broken by the naming bug. Now `START_PRINT`
  (`_SOVOL_SYNC_Z_OFFSET`) uses a pending z_offset right away. `START_PRINT` also re-homes Z after
  `Z_TILT_ADJUST` (like the calibration), so measuring and printing share the same zero point.
- **Z offset: Mainsail panel and macros lead to the same result.** `Z_OFFSET_APPLY_PROBE` (Mainsail's
  save button) is wrapped and leaves out the T1 tool offset. `SAVE_Z_OFFSET` uses it. Babysteps are no
  longer deleted at print start (they stay until saved or Klipper restarts, as in standard Klipper).
  END_PRINT offers to save an active babystep. `CALIBRATE_Z_T1` refuses while the T0 value is unsaved.
- **Renamed macros because they couldn't be called at all:** Klipper cuts command names after digits in
  the middle (`SV04_MENU` → `SV04`). New names: `SOVOL_MENU`, `CALIBRATE_Z_T1`, `SET_OFFSET_T1`, internal
  helpers `_SOVOL_…`. Before this, SAVE_CONFIG ("Unknown command _SV04"), the menu, T1 offsets and input
  shaper at print start / tool change didn't work. `tools/check_klipper_config.py` now checks this.
- `mainsail_macro_groups.py` did nothing on a fresh Mainsail ("open Mainsail once"), because Mainsail
  only stores the key `macros` once a setting changes. It now reads the whole namespace.
- "Option 'minimum_cruise_ratio' is not valid" on older Klipper (e.g. an old MainsailOS image): the
  option is no longer set in either variant. Klipper's default (half of `max_accel`) matches the previous
  value. `max_accel_to_decel` was removed in mainline in 08/2025, so no single spelling works on old and
  new Klipper.
- `sv04-pi-setup.sh` with variant `original` on a Pi that already runs the Bully85 fork: it used to only
  warn and copy the original config onto the fork (→ "minimum_cruise_ratio is not valid"). Now it
  switches Klipper back to original Klipper and installs the Python requirements (also when switching to the fork).
- `sv04-pi-setup.sh` stops if Klipper (original variant) is older than 2024-03-14 and asks you to update
  it in Mainsail first, so the firmware is built from the current version.
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
