# Bambu Studio CLI tests

Bambu Studio 2.7.1.62 (Flatpak), 20 mm cube, `--arrange 1 --orient 0 --slice 0`.

- User presets with `"inherits": ""` → CLI error -17 "process not compatible with printer". With
  `inherits` set to `Voron 2.4 300 0.4 nozzle` / `0.20mm Standard @Voron` in test copies, it works.
- 5 printers × 4 processes + all 4 filaments: exit 0. The G-code contains only Klipper-compatible commands
  (`EXCLUDE_OBJECT_*`, `M73`, `M204`, `M106`, `G17`/`G3` lift at the end).
- `M190 S0`/`M109 S0` stop Bambu from inserting its own heat-up commands.
- `{nozzle_temperature_initial_layer[1]}` with one filament → value of `[0]`.
- `{first_layer_print_max[0] + 151}` is computed (later dropped again, `START_PRINT` does it).
- Two filaments (`--load-filament-ids "1,2"` or a 3MF with extruder 2) → "Levitating objects cannot be
  printed without supports". Same with stock Voron presets, so it is a CLI limit.
- Accelerations after the input shaper change: `M204 S1500/750/1000/500`, plus `S250` = Bambu's
  `travel_short_distance_acceleration`. Cube 1147 s → 1076 s.
