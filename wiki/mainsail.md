# Mainsail

## Macro groups (expert mode)

- Mainsail stores its settings in the **Moonraker database**, namespace `mainsail`. Macro settings live
  under `macros`: `mode` (`simple`|`expert`), `hiddenMacros`, `macrogroups.<id>`
  ([source notes](sources/2026-11-25_mainsail-source-notes.md)).
- Group: `name`, `color` (`primary|secondary|success|warning|error|custom`), `showInStandby/Printing/Pause`,
  `macros[]` with `pos`, `name`, `color` (`group` = group colour), `showIn…`.
- Groups are sorted **alphabetically by name**, hence the number prefixes "1 SV04" … "5 Settings".
- In expert mode, every group becomes a dashboard panel `macrogroup_<id>`. Missing panels are
  added to column 1 automatically.
- Macro names match case-insensitively. Macros that don't exist are hidden (so
  `SHAPER_CALIBRATE_SV04` can stay in the group even without `adxl345.cfg`).
- **Never shown as macros:** names with a leading `_` and macros with `rename_existing` (PAUSE, RESUME,
  CANCEL_PRINT, SAVE_CONFIG, BED_MESH_CALIBRATE). Mainsail has its own buttons for those.
- **Mainsail only stores keys once they change.** In a fresh install, `macros` is **missing** from the
  namespace (only `initVersion` and theme defaults exist). So read the whole namespace
  (`GET …?namespace=mainsail`), never `key=macros` (404 even though Mainsail is set up). Real bug in the
  first test on 2026-11-25.
- `install/mainsail_macro_groups.py` writes via `POST /server/database/item` with fixed ids `sv04-1-main`
  … `sv04-5-settings` (re-run = update), keeps groups with other ids, `--remove` deletes via
  `DELETE /server/database/item`. Mainsail must have been opened once (otherwise the namespace is missing,
  404), and it must be reloaded afterwards (F5).

## Z offset panel

From `src/components/mixins/zoffset.ts` / `ToolheadControls/ZoffsetControl.vue`: babystep =
`SET_GCODE_OFFSET Z_ADJUST=±x MOVE=1`, reset = `SET_GCODE_OFFSET Z=0`, save = `Z_OFFSET_APPLY_PROBE`
(shown when `stepper_z endstop_pin` is `probe:z_virtual_endstop` and the command exists, and the
offset ≠ 0), then a dialog with `SAVE_CONFIG`. Displayed value = `homing_origin[2]` (includes the T1 share).

## Prompts

See [klipper-jinja-pitfalls](klipper-jinja-pitfalls.md#) (`action:prompt_*`, Mainsail ≥ 2.9).
