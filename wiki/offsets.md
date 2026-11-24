# Offsets (Z/XY) and calibration wizards

- **T0 Z:** `[bltouch] z_offset` (SAVE_CONFIG block). **T1:** `dual_x/y/z_offset` in `variables.cfg`,
  relative to T0, set with `SET_T1_OFFSET X= Y= Z=` (`XY_offset_dual` is an alias).
- `_SV04_TOOL_OFFSET TOOL=n` sets X/Y absolutely and Z **relatively** (`Z_ADJUST`), and remembers
  `applied_z`. So babysteps survive tool changes, even when T0/T1 are not called in pairs.
- `_SV04_TOOL_OFFSET_RESET` at `START_PRINT`/`END_PRINT` clears everything, so no stale offsets carry over.
- `SAVE_Z_OFFSET` removes `applied_z` for a moment, so `Z_OFFSET_APPLY_PROBE` only stores the babystep
  (correct even while T1 is active). Mainsail's own save button would include the T1 share.
- `Z_OFFSET_CALIBRATE`: heats, homes, Z tilt, `PROBE_CALIBRATE` in the bed centre (probe 25 mm behind
  the nozzle → nozzle at Y 125.5). After ACCEPT, a dialog with SAVE_CONFIG appears.
- `CALIBRATE_T1_Z`: after `MANUAL_PROBE`, `printer.toolhead.position.z` (kinematic, without G-code
  offset) is the T1 offset relative to T0. Above 0.3 mm a warning appears (COPY/MIRROR can't compensate).
- **Waiting for ACCEPT/ABORT:** `_SV04_WAIT_MANUAL_PROBE DONE=<macro>` polls
  `printer.manual_probe.is_active` via `delayed_gcode`. ACCEPT and ABORT can't be told apart, so the
  result dialog offers *Discard*.
- At the end of a print, `_SV04_END_PRINT_PROMPT` offers SAVE_CONFIG when values are pending.
