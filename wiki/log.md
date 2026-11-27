# Wiki log

Newest entries first. One line per change: date – what – affected pages.

- 2026-11-28 – Live analysis via Moonraker (tools/printer_check.py): z_offset 1.307 in the file but 0.0 loaded, because merge_printer_cfg brought back `z_offset: 0` active (Klipper ignores autosave duplicates); dual_z_offset −1.15 measured against T0=0. Fixed: merge strip_duplicates, CALIBRATE_Z_T1 guard, END prompt without bed_mesh – testing, installation, klipper-jinja-pitfalls
- 2026-11-28 – Real test "dual print lost its Z offset": tool change stayed lifted / T1 offset only active on the next Z move; babystep on T1 changed T0. New `_SOVOL_TOOLCHANGE`, hierarchical babystep model, simulator with exact gcode_move semantics (old config: T1 +1.88 mm) – offsets, testing, sources
- 2026-11-26 – Upgrade guide docs/Upgrades-Bambu-Standard.md (web research on SV04 hardware and Bambu compatibility) – hardware-ideas
- 2026-11-26 – PROBE_CHECK (BLTouch repeatability); hardware ideas page (load cell as an upgrade, sensorless Z ruled out) – leveling, hardware-ideas
- 2026-11-26 – Real test: MCU v0.11 (fork firmware) vs host v0.14 → "deprecated code / STEPPER_STEP_BOTH_EDGE". The Pi script now compares the versions and offers the firmware – installation
- 2026-11-26 – Mainsail in Bambu Studio (print_host/print_host_webui), PrusaSlicer upload address, installer --host – slicers, installation
- 2026-11-26 – Leveling review: probe 5 mm/s + samples_tolerance, mesh to the edges + fade, BED_MESH passthrough, PREHEAT, BED_SCREWS_CHECK, printer.cfg merge on --update – leveling, installation
- 2026-11-26 – Z offset during the print: Z_OFFSET_MENU / Z_OFFSET_UP / Z_OFFSET_DOWN, simulator scenario G – offsets, testing
- 2026-11-26 – Real test "Z offset too high": pending z_offset was never active (SAVE_CONFIG broken, no restart), no G28 Z after Z tilt, babystep deleted at print start. Fixed: `_SOVOL_SYNC_Z_OFFSET`, `Z_OFFSET_APPLY_PROBE` wrapper, babystep kept, simulator – offsets, mainsail, klipper-jinja-pitfalls, testing
- 2026-11-25 – Real test: `Unknown command:"_SV04"` → digits in the middle of names break Klipper's parser. All `SV04_…`/`_SV04_…` → `SOVOL_…`, `CALIBRATE_T1_Z` → `CALIBRATE_Z_T1`, `SET_T1_OFFSET` → `SET_OFFSET_T1`; checker extended – klipper-jinja-pitfalls, testing, all pages
- 2026-11-25 – Macro groups had no effect in the real test (key `macros` missing in a fresh Mainsail) → read the whole namespace – mainsail
- 2026-11-25 – Mainsail macro groups (from the Mainsail source) – mainsail, installation
- 2026-11-25 – Real test: the Pi ran the Bully85 fork (Update Manager: klipper v0.12.0-0-g1c8f683a = fork head 2024-01-26, "up to date" because the fork has no new commits). Script now switches back to mainline for `original` – installation
- 2026-11-25 – First real test: old MainsailOS image → `minimum_cruise_ratio` invalid. Option removed, version check in the Pi script – klipper-jinja-pitfalls, installation, repo-structure
- 2026-11-25 – Restructured as LLM Wiki (sources/ + topic pages + index); added installation (Pi script, slicer installers for Windows/macOS/Linux) – all pages
- 2026-11-25 – Input shaper without a sensor (preset) and with ADXL345 – input-shaper, printer-hardware, slicers
- 2026-11-24 – Install only via MainsailOS, firmware settings from firmware.bin – installation, printer-hardware
- 2026-11-24 – Z offset model T0/T1, SOVOL_MENU, IDEX fixes, Bambu Studio profiles – offsets, idex, slicers, testing
