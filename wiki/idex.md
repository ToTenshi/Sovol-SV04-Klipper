# IDEX / dual carriage

- **Status:** `printer.dual_carriage.carriage_0` / `carriage_1` with `PRIMARY`, `INACTIVE`, `COPY`, `MIRROR`.
  **There is no `printer.dual_carriage.mode`.** Older PAUSE/CLEAN_NOZZLE code used it, which was a bug
  ("Move out of range" when pausing in MIRROR). Mainline additionally has `carriages`, and
  `carriage_0/1` exist in both versions ([source notes](sources/2026-11-24_klipper-source-notes.md)).
- **COPY offset** = `0.5 * (bed_x_max - bed_x_min)` = 151 mm (`ACTIVATE_COPY_MODE`). MIRROR mirrors at 302.
  This is why the slicer print area for COPY/MIRROR is 150 mm wide.
- **START_PRINT** is called by the slicer after `SET_DUAL_CARRIAGE CARRIAGE=1 MODE=COPY|MIRROR`.
  The Jinja branches are evaluated **at render time**, before `SET_DUAL_CARRIAGE CARRIAGE=0` inside
  the macro resets the mode. `M605 S2/S3` activates the mode again afterwards.
- `EXTRUDERS=2` + carriage state selects dual/copy/mirror, `EXTRUDERS=1` selects single (`EXTRUDER=0|1`).
- **Bed mesh in COPY/MIRROR:** `START_PRINT` extends `AREA_END` X itself (copy: +151, mirror:
  302 − min X). That's why slicers must not add an offset ([slicers](slicers.md)).
- After every carriage change the following must run: `_SV04_TOOL_OFFSET` ([offsets](offsets.md)) and
  `_SV04_APPLY_SHAPER` ([input-shaper](input-shaper.md)).
