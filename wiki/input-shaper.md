# Input shaper

- **Original Klipper + `[dual_carriage]`: shaper values in `[input_shaper]` cause a config error at
  startup** (`input_shaper.py` connect()). That is why `[input_shaper]` stays empty and
  `_SV04_APPLY_SHAPER` runs `SET_INPUT_SHAPER` at runtime. The fork accepts it too
  ([source notes](sources/2026-11-24_klipper-source-notes.md)).
- `SET_INPUT_SHAPER` only affects the steppers of the currently active carriage(s), so it is called
  after every carriage change: `_SV04_SHAPER_INIT` (delayed_gcode at startup), T0/T1,
  ACTIVATE_COPY/MIRROR_MODE, START_PRINT when starting with T1. COPY/MIRROR use the T0 values (x0).
- **Values:** `shaper_type_x0/x1/y` + `shaper_freq_x0/x1/y` in `variables.cfg`. Empty or 0 means the
  preset from `_SV04_SHAPER` (X EI 40 Hz, Y EI 30 Hz) is used. Set manually with `INPUT_SHAPER_SET`
  (ringing tower), show with `INPUT_SHAPER_STATUS`.
- **Sensor:** `SHAPER_CALIBRATE` always writes to `configfile` (pending for SAVE_CONFIG).
  `_SV04_SHAPER_STORE` reads the result from `printer.configfile.save_config_pending_items['input_shaper']`.
  The `SAVE_CONFIG` macro (rename_existing `_SV04_SAVE_CONFIG_BASE`) blocks while it is pending, and
  RESTART discards it.
- **Preset limit:** EI 30 Hz (Y) gives ~0.134 mm smoothing at 1500 mm/s² (Klipper target 0.12, scv 8),
  calculated with Klipper's `_get_shaper_smoothing` formula. No published SV04 measurements were found
  ([research](sources/2026-11-25_web-research.md)).
- **Slicers:** Cura and Bambu Studio send their own accelerations (`M204`), both set to 1500.
  PrusaSlicer sends nothing (`M201` is a no-op macro), so Klipper's `max_accel` applies.
