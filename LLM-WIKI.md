# LLM-WIKI – Sovol SV04 Klipper

Knowledge base for AI assistants and developers. It describes what is not obvious from the code:
structure, rules, pitfalls and how changes are tested. Keep this file up to date with every change.

## Maintenance rules

- Record every change in `CHANGELOG.md` under `[Unreleased]` (Added/Changed/Fixed/Removed).
- Keep the `README.md` (English) and `READMEdeutsch.md` (German) content identical, and extend them
  with every user-visible change (news section, features, installation).
- Update this wiki when structure, rules or known pitfalls change.
- Installation is documented **only** for a fresh MainsailOS. Don't recommend a custom image again.
- Users must never lose `variables.cfg` or the `#*# SAVE_CONFIG` block. Point this out in update notes.

## Repository structure

| Path | Contents |
|------|----------|
| `config/Sv04-works-with origin-klipper/` | **Default.** Config for original Klipper (MainsailOS) |
| `config/SV04-with-display/` | Config for the fork `Bully85/klipper` with the original DGUS display (`t5uid1.cfg`) |
| `Bambu Studio Profile/` | Bambu Studio user presets, `tools/build_profiles.py` generates them |
| `Cura Profile/` | Cura definitions/extruders, `MeshPrintSize.py` (replaces `%MINX%` etc.) |
| `Prusaslicer Profile/` | PrusaSlicer config bundle + bed model |
| `Firmware bin/firmware.bin` | Firmware built from the fork (v0.11.0-261), only for the display variant |
| `docs/Kalibrierung-Calibration.md` | User guide for macros and calibration (DE+EN) |
| `sv04-*-install.sh` | Linux installers for Bambu Studio and Cura (native + Flatpak) |

**The two config folders are identical except for `printer.cfg` and `t5uid1.cfg`.** Edit shared files
(`IDEX_mode.cfg`, `Start_End_Macro.cfg`, `macros.cfg`, `sv04_tools.cfg`, `misc.cfg`, …) in
`SV04-with-display` and copy them to the other folder. Check with:
`diff -r config/SV04-with-display "config/Sv04-works-with origin-klipper"`
Expected differences only: the `t5uid1` include and DGUS stubs, and `max_accel_to_decel` vs.
`minimum_cruise_ratio`.

## Printer facts

- MCU: STM32F103xE (also GD32 variant), 72 MHz, 28 KiB bootloader (app at 0x08007000),
  serial USART1 PA10/PA9 at **115200** baud, CH340 USB serial adapter. DGUS display on USART3 PB11/PB10.
  Source: data dictionary in `firmware.bin`.
- STM32 vs. GD32: only the Z stepper pins differ (two blocks in `printer.cfg`).
- Bed 302 × 302, Z 400. X: carriage 0 `position_min -65` (endstop -65), `dual_carriage` endstop/max 360.
- BLTouch `y_offset: 25`, homing via `[homing_override]` (always T0, centre 150.5/150.5).
- Firmware limits: `max_velocity 300`, `max_accel 1000`.
- Part cooling fans are `fan_generic fanX1` (T0) / `fanX2` (T1), and `M106`/`M107` are macros.

## IDEX / dual carriage

- Status: `printer.dual_carriage.carriage_0` / `carriage_1` with `PRIMARY`, `INACTIVE`, `COPY`, `MIRROR`.
  **There is no `printer.dual_carriage.mode`.** Older code used it, which was a bug.
  Mainline additionally has `carriages`. `carriage_0/1` exist in the fork and in mainline.
- COPY offset = `0.5 * (bed_x_max - bed_x_min)` = 151 mm (`ACTIVATE_COPY_MODE`). MIRROR mirrors at 302.
  This is why the slicer print area for COPY/MIRROR is 150 mm wide.
- `START_PRINT` is called by the slicer after `SET_DUAL_CARRIAGE CARRIAGE=1 MODE=COPY|MIRROR`.
  The Jinja branches are evaluated **at render time**, before `SET_DUAL_CARRIAGE CARRIAGE=0`
  inside the macro resets the mode. `M605 S2/S3` activates the mode again afterwards.
- `EXTRUDERS=2` + carriage state selects dual/copy/mirror, `EXTRUDERS=1` selects single (`EXTRUDER=0|1`).

## Offset model (Z/XY)

- T0 Z: `[bltouch] z_offset` (SAVE_CONFIG). T1: `dual_x/y/z_offset` in `variables.cfg`.
- `_SV04_TOOL_OFFSET TOOL=n` sets X/Y absolutely and Z **relatively** (`Z_ADJUST`), and remembers
  `applied_z`. So babysteps survive tool changes, even when T0/T1 are not called in pairs.
- `_SV04_TOOL_OFFSET_RESET` at `START_PRINT`/`END_PRINT` clears everything.
- `SAVE_Z_OFFSET` removes `applied_z` for a moment, so `Z_OFFSET_APPLY_PROBE` only stores the babystep.
- `CALIBRATE_T1_Z`: after `MANUAL_PROBE`, `printer.toolhead.position.z` (kinematic, without
  G-code offset) is the T1 offset relative to T0.
- Waiting for ACCEPT/ABORT: `_SV04_WAIT_MANUAL_PROBE DONE=<macro>` polls `printer.manual_probe.is_active`
  with `delayed_gcode`. ACCEPT and ABORT can't be told apart, so the result dialog offers Discard.

## Klipper/Jinja pitfalls

- **`{-x}` is not minus.** With Klipper's delimiters `{ }`, `{-` is Jinja whitespace control.
  Write `{0.0 - x}`.
- The whole template of a macro is rendered **before** execution. Values that a command in the
  same macro changes must be read in a nested macro.
- `SET_GCODE_VARIABLE VALUE` is `ast.literal_eval`. Pass strings as `VALUE="'text'"`.
- Parameters are split with `shlex`, so no unbalanced `"` in messages. Avoid umlauts in G-code strings.
- Mainsail prompts: `RESPOND TYPE=command MSG="action:prompt_begin …"`, `prompt_button Label|GCODE|color`,
  `prompt_footer_button`, `prompt_show`, `prompt_end`. Macros started from buttons begin with `prompt_end`.
- The fork (January 2024) knows **no** `minimum_cruise_ratio`, keep `max_accel_to_decel` there.
- `SAVE_CONFIG` comments out values in the main `printer.cfg` that are overridden by the autosave block.

## Slicer conventions

- Start G-code always begins with `M190 S0` / `M109 S0`. This keeps the slicer from heating on its own,
  because `START_PRINT` handles heating, homing, Z tilt and the mesh.
- Mesh area: Cura `%MINX%…` (via `MeshPrintSize.py`), PrusaSlicer/Bambu
  `{first_layer_print_min[0]}` etc. Don't add offsets in the slicer, `START_PRINT` extends COPY/MIRROR itself.
- Bambu Studio: standalone user presets (`"inherits": ""`, `"from": "User"`), generated from the
  Voron profiles that ship with Bambu Studio. Placeholders: `nozzle_temperature_initial_layer[n]`
  (index beyond the end falls back to `[0]`), `bed_temperature_initial_layer_single`, `initial_extruder`.
  Dual: `change_filament_gcode = T[next_extruder]`.

## Testing (without a printer)

- Static: parse the configs with `configparser` (`inline_comment_prefixes=(';','#')`, `strict=False`)
  and compile all `gcode` templates with `jinja2.Environment('{%','%}','{','}')`.
- Simulation: render macros recursively against a mock `printer` object and follow
  `SET_GCODE_OFFSET`, `SAVE/RESTORE_GCODE_STATE`, `SET_DUAL_CARRIAGE`, `SET_GCODE_VARIABLE`.
  This found the `{-` bug.
- Bambu Studio CLI (Flatpak):
  `flatpak run --command=bambu-studio com.bambulab.BambuStudio --slice 0 --load-settings "machine.json;process.json" --load-filaments "f.json" model.stl`.
  For the CLI, test copies need `inherits` set to a system preset (e.g. `Voron 2.4 300 0.4 nozzle`).
  Otherwise it reports "process not compatible". Slicing with 2 filaments fails in the CLI even with
  stock Voron presets ("Levitating objects"), so test the dual tool change in the GUI.
- PrusaSlicer bundle: compare section by section with `git show HEAD:<file>` (the diff is noisy).

## Known open points

- Dual tool change with Bambu Studio has not been tested on real hardware/GUI.
- The Discord invite link may expire, and only the maintainer can create a permanent one.
- `idle_timeout` is 7200 s (long, because M600 pauses must not cool down).
