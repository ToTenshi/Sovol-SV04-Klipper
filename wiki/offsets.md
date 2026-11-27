# Offsets (Z/XY) and calibration wizards

- **T0 Z:** `[bltouch] z_offset` (SAVE_CONFIG block). **T1:** `dual_x/y/z_offset` in `variables.cfg`,
  relative to T0, set with `SET_OFFSET_T1 X= Y= Z=` (`XY_offset_dual` is an alias).
- **Model since 2026-11-28:** G-code Z offset = `sync_z` + `baby0` (+ `dual_z_offset` + `baby1` while T1
  is active). `baby0` = babystep made while T0/COPY/MIRROR prints, the reference correction for **both**
  nozzles. `baby1` = babystep made while T1 prints, **only T1**. `_SOVOL_TOOL_OFFSET TOOL=n` computes the
  live babystep of the active tool from `homing_origin.z`, stores it and sets the absolute offset of the
  new tool. Saving: T0 → probe z_offset (`_SOVOL_SAVE_BABYSTEP_T0`, temporarily removes the T1 part,
  then `sync_z += b0`). T1 → `dual_z_offset += b1` (`_SOVOL_SAVE_BABYSTEP_T1`, no movement). Why
  hierarchical: a probe error affects both nozzles equally, a T1 error only T1. Strictly separate
  babysteps would have counted a probe error twice (simulator scenario F).
- **Tool change (`_SOVOL_TOOLCHANGE`):** remembers `gcode_position`, lifts by `z_hop`, parks, switches,
  `RESTORE_GCODE_STATE` (without MOVE), new tool offsets, then `G1 X Y Z+hop` and `G1 Z` back to the same
  G-code position. Klipper facts ([source notes](sources/2026-11-24_klipper-source-notes.md)): `G1`
  without Z keeps the kinematic Z, and `SET_GCODE_OFFSET` without `MOVE` only takes effect on the next Z
  move. The old macros (`RESTORE … MOVE=1` back to the *lifted* position, lowering only when not
  printing) left the new tool 2 mm higher and without its offset if the slicer didn't send Z (old config
  simulated: T1 +1.88 mm, T0 after switching back +4 mm).
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
- **Babystep during the print:** `Z_OFFSET_UP/DOWN STEP=` → `_SOVOL_BABYSTEP` (`SET_GCODE_OFFSET Z_ADJUST
  MOVE=1` like Mainsail, limit |total| ≤ 1 mm, the total is shown without `applied_z`). `MENU=1` reopens
  `Z_OFFSET_MENU` (nested macro, so the new value is shown).
- `Z_OFFSET_CALIBRATE`: heats, homes, Z tilt, `PROBE_CALIBRATE` in the bed centre (probe 25 mm behind
  the nozzle → nozzle at Y 125.5). After ACCEPT, a dialog with SAVE_CONFIG appears.
- `CALIBRATE_Z_T1` refuses while a T0 z_offset is pending, because the kinematic zero still uses the
  old value. After `MANUAL_PROBE`, `printer.toolhead.position.z` (kinematic, without G-code
  offset) is the T1 offset relative to T0. Above 0.3 mm a warning appears (COPY/MIRROR can't compensate).
- **Waiting for ACCEPT/ABORT:** `_SOVOL_WAIT_MANUAL_PROBE DONE=<macro>` polls
  `printer.manual_probe.is_active` via `delayed_gcode`. ACCEPT and ABORT can't be told apart, so the
  result dialog offers *Discard*.
- At the end of a print, `_SOVOL_END_PRINT_PROMPT` offers SAVE_CONFIG when values are pending.
