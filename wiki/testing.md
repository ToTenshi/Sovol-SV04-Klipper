# Testing (without a printer)

- **Live on the printer (read-only):** `python3 tools/printer_check.py`. It reads through the Moonraker
  API (`/printer/info`, `/printer/objects/query`, `/printer/gcode/help`, `/server/files/config/…`) and
  checks state, firmware/host version, ignored SAVE_CONFIG values, z_offset loaded vs. file,
  `dual_z_offset` plausibility, macro names/presence, installed macros vs. repo, and runs the simulator
  on the **installed** config. API key/host in `tools/printer.local.env` (`HOST=`, `KEY=`, git-ignored,
  **never commit**). `*.local` names may resolve to IPv6 first, so the tool resolves IPv4 itself.
  Exit 1 on FAIL. Run it after every update and when something looks wrong.
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
- **Z offset:** `python3 tools/simulate_z_offset.py [config folder]` models Klipper's `gcode_move` exactly
  (see source notes) and a "true" printer (probe 1.80, T1 0.12 mm longer). It checks the **real nozzle
  height** after calibration, babysteps, saving, restart and tool changes (also when the slicer sends no
  Z). Scenarios A–H, `exit 1` on any error. Against an old config folder it shows the old bugs (e.g.
  `git archive HEAD config`).
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
