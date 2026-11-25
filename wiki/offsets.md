# Offsets (Z/XY) and calibration wizards

- **T0 Z:** `[bltouch] z_offset` (SAVE_CONFIG block). **T1:** `dual_x/y/z_offset` in `variables.cfg`,
  relative to T0, set with `SET_OFFSET_T1 X= Y= Z=` (`XY_offset_dual` is an alias).
- `_SOVOL_TOOL_OFFSET TOOL=n` sets X/Y absolutely and Z **relatively** (`Z_ADJUST`), and remembers
  `applied_z`. So babysteps survive tool changes, even when T0/T1 are not called in pairs.
- `_SOVOL_TOOL_OFFSET_RESET` at `START_PRINT`/`END_PRINT` only removes the **T1 share** (X/Y absolute,
  Z via `-applied_z`). **The babystep stays** until saved or Klipper restarts, as in standard Klipper.
  Until 2026-11-26 it was set to 0, which threw away a babystep that was stored with
  Z_OFFSET_APPLY_PROBE but not yet active.
- **Pending z_offset:** `PROBE_CALIBRATE`/`Z_OFFSET_APPLY_PROBE` only write it to `configfile`. Klipper
  uses it **only after SAVE_CONFIG** (restart). `_SOVOL_SYNC_Z_OFFSET` (START_PRINT) sets the
  babystep to `loaded - pending`. With Z_OFFSET_APPLY_PROBE that is exactly the existing babystep
  (no change). With PROBE_CALIBRATE it is the difference to the measured value. Every path ends at the
  same nozzle height (`tools/simulate_z_offset.py`).
- `Z_OFFSET_APPLY_PROBE` is a macro (rename_existing `Z_OFFSET_APPLY_PROBE_BASE`) that leaves out
  `applied_z`. That makes Mainsail's save button (sends exactly this command,
  [mainsail](mainsail.md)) and `SAVE_Z_OFFSET` equivalent.
- `START_PRINT` homes Z again after `Z_TILT_ADJUST` (`G28 Z`), the same as `Z_TILT_HOME`/the calibration.
- Edge case: Mainsail's *Reset* (`SET_GCODE_OFFSET Z=0`) **while T1 is active** also deletes the T1 share.
  The next T0 then subtracts it again (−dz until the next print start). Rare, not fixed.
- `Z_OFFSET_CALIBRATE`: heats, homes, Z tilt, `PROBE_CALIBRATE` in the bed centre (probe 25 mm behind
  the nozzle → nozzle at Y 125.5). After ACCEPT, a dialog with SAVE_CONFIG appears.
- `CALIBRATE_Z_T1` refuses while a T0 z_offset is pending, because the kinematic zero still uses the
  old value. After `MANUAL_PROBE`, `printer.toolhead.position.z` (kinematic, without G-code
  offset) is the T1 offset relative to T0. Above 0.3 mm a warning appears (COPY/MIRROR can't compensate).
- **Waiting for ACCEPT/ABORT:** `_SOVOL_WAIT_MANUAL_PROBE DONE=<macro>` polls
  `printer.manual_probe.is_active` via `delayed_gcode`. ACCEPT and ABORT can't be told apart, so the
  result dialog offers *Discard*.
- At the end of a print, `_SOVOL_END_PRINT_PROMPT` offers SAVE_CONFIG when values are pending.
