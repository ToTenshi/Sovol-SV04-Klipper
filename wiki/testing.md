# Testing (without a printer)

- **Static:** `python3 tools/check_klipper_config.py` parses both config folders the way Klipper does
  (`configparser`, `inline_comment_prefixes=(';','#')`, `strict=False`), compiles every `gcode`
  template with `jinja2.Environment('{%','%}','{','}')`, checks `variable_*` with `ast.literal_eval`,
  and compares the two folders.
- **Macro simulation:** render macros recursively against a mock `printer` object and follow
  `SET_GCODE_OFFSET`, `SAVE/RESTORE_GCODE_STATE`, `SET_DUAL_CARRIAGE`, `SET_GCODE_VARIABLE`,
  `SAVE_VARIABLE`. This found the `{-` bug ([pitfalls](klipper-jinja-pitfalls.md)).
  The simulator is not in the repo yet ([open-points](open-points.md)). **Gap:** it didn't model Klipper's
  command parser and missed the "digits in the middle of a name" bug. `check_klipper_config.py`
  now covers that.
- **Z offset:** `python3 tools/simulate_z_offset.py [config folder]` runs scenarios A–F (calibration
  without saving, Mainsail panel, SAVE_Z_OFFSET, babystep on T1, unsaved babystep, T1 calibration with
  a pending T0 value). Every "effective z_offset" line must show 1.800 (except the start value in D),
  and there must be no `UNKNOWN COMMAND`.
- **Klipper batch mode** (real parser) wasn't possible here: building the host MCU firmware from a
  cloned Klipper repo was blocked in the work environment.
- **Bambu Studio CLI** (Flatpak):
  `flatpak run --command=bambu-studio com.bambulab.BambuStudio --slice 0 --load-settings "machine.json;process.json" --load-filaments "f.json" model.stl`.
  For the CLI, test copies need `inherits` set to a system preset (`Voron 2.4 300 0.4 nozzle`),
  otherwise "process not compatible". Two filaments fail in the CLI even with stock Voron presets
  ("Levitating objects") ([source](sources/2026-11-24_bambu-cli-tests.md)).
- **Installers:** run them with a fake `HOME` (and `SV04_OS=Darwin` for macOS, a `pgrep` stub that
  returns 1). Compare the PrusaSlicer split line by line with the bundle. For the Pi script, use a
  fake Klipper repo with a stub Makefile plus `SV04_*` variables.
- **PrusaSlicer bundle:** compare section by section with `git show HEAD:<file>` (the diff is noisy).
- **PowerShell:** no `pwsh` on the dev machine, so the Windows installer is untested.
