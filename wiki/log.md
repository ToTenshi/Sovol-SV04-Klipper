# Wiki log

Newest entries first. One line per change: date – what – affected pages.

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
