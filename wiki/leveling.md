# Leveling

Order: `Z_TILT_HOME` (gantry) → `BED_LEVEL_SCREWS` (bed plane, screws) → Z offset ([offsets](offsets.md)).
Every print: `START_PRINT` = G28 → Z_TILT_ADJUST → **G28 Z** → adaptive `BED_MESH_CALIBRATE`.

## Probe (`[bltouch]`)

- `y_offset: 25` (probe behind the nozzle), `x_offset: 0`.
- `speed: 5` (BLTouch recommendation, was 10), `lift_speed: 10`, `samples: 2`,
  `samples_tolerance: 0.025` + `samples_tolerance_retries: 3`: measurements that disagree are repeated
  instead of being averaged silently. Directly improves the repeatability of homing/Z offset.

## Z tilt (`[z_tilt]`)

- `points` are **nozzle** coordinates (50/150.5 and 280/150.5 → probe at Y 175.5).
- `z_positions` 10,150 / 290,150 are estimates of the lead screw positions. Wrong values only cost
  retries (`retries: 10`, `retry_tolerance: 0.02`).
- After `Z_TILT_ADJUST`, Z must be homed again, because the reference point moves (START_PRINT, PREHEAT and
  Z_TILT_HOME do that).

## Bed mesh (`[bed_mesh]`)

- `mesh_min/mesh_max` are **probe** coordinates. The mesh applies to the nozzle position, so slicer
  AREA values (nozzle) and mesh limits can be compared directly.
- Front: probe Y 30 = nozzle Y 5, back: probe Y 290 = nozzle Y 265 (bed 302). Was 45/270, so parts
  at the front/back edge were outside the mesh (Klipper uses the edge value there).
- `fade_start: 1`, `fade_end: 10`: the correction fades out over the first 10 mm.
- `BED_MESH_CALIBRATE` macro (macros.cfg): with `AREA_START/AREA_END` from the slicer → adaptive mesh
  (area + 5 mm, probe count scaled, at least 3). All other parameters are passed through
  (`rejectattr(0, "in", [...])|map("join","=")`), e.g. `PROFILE=` from Mainsail's heightmap page.
- No `zero_reference_position`: mesh values are relative to the Z zero from homing (bed centre).

## Bed screws

- `[bed_screws]` (BED_SCREWS_ADJUST, paper test): **nozzle** over the screw, 25/35, 295/35, 295/295, 25/295.
- `[screws_tilt_adjust]` (BED_LEVEL_SCREWS, probe): **nozzle position at which the probe is over the screw**,
  31/0, 270/0, 270/240, 31/240. **These don't match** (bed_screws translated would be 25/10,
  295/10, 295/270, 25/270). Check with `BED_SCREWS_CHECK` ([open-points](open-points.md)).
- `screw_thread: CW-M4`.

## PREHEAT

`PREHEAT BED= NOZZLE=`: bed + both nozzles, G28, Z_TILT_ADJUST, G28 Z. It no longer creates stored
mesh profiles (the old `PREHEATANDMESH`/`LOAD_MESH_TEMP` left a pending SAVE_CONFIG behind,
and START_PRINT measures the mesh every time anyway). `LOAD_MESH_TEMP`/`ADD_BED_MESH` still exist,
but are not part of the normal workflow.
