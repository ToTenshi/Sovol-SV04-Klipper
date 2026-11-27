# Klipper/Jinja pitfalls

- **No digits in the MIDDLE of a command/macro name.** Klipper's parser (`args_r = ([A-Z_]+|[A-Z*])`
  in `klippy/gcode.py`) splits a line into letter and number blocks and takes block 1 + block 2 as
  the command. `SV04_MENU` → `SV04`, `SET_T1_OFFSET` → `SET_T1`. Klipper registers such macros, but
  they can never be called ("Unknown command"). Digits only at the **end** (`PREHEAT60`,
  `CALIBRATE_Z_T1`). This affected all `SV04_…` macros until 2026-11-25 (SAVE_CONFIG was dead).
  `tools/check_klipper_config.py` now checks names and calls.

- **`{-x}` is not minus.** With Klipper's delimiters `{ }`, `{-` is Jinja whitespace control.
  Write `{0.0 - x}`. Found by the macro simulation ([testing](testing.md)).
- The whole template of a macro is rendered **before** execution. Values that a command in the same
  macro changes must be read in a nested macro (e.g. `_SOVOL_TOOL_OFFSET` after `SAVE_VARIABLE`).
- `SET_GCODE_VARIABLE VALUE` and `SAVE_VARIABLE VALUE` are `ast.literal_eval`. Pass strings as `VALUE="'text'"`.
- Parameters are split with `shlex`, so no unbalanced `"` in messages. Avoid umlauts in G-code strings.
- Unknown G-code commands only produce the message `Unknown command`, the print continues.
- **Mainsail prompts** (Mainsail ≥ 2.9, Fluidd ≥ 1.27): `RESPOND TYPE=command MSG="action:prompt_begin …"`,
  `prompt_text`, `prompt_button Label|GCODE|color`, `prompt_button_group_start/_end`,
  `prompt_footer_button`, `prompt_show`, `prompt_end`. Macros started from buttons begin with `prompt_end`.
- **Fork vs. mainline:** the fork (January 2024, v0.11.0-261) knows **no** `minimum_cruise_ratio` and
  doesn't check input shaper + dual_carriage.
- **`minimum_cruise_ratio` / `max_accel_to_decel`:** mainline introduced `minimum_cruise_ratio` on
  2024-03-14 and **removed** `max_accel_to_decel` on 2025-08-11. No spelling works on every version,
  so **set neither**. The default is half of `max_accel` everywhere. Real error on an old MainsailOS
  image: "Option 'minimum_cruise_ratio' is not valid in section 'printer'".
- **Values from `configfile.set` (PROBE_CALIBRATE, Z_OFFSET_APPLY_PROBE, SHAPER_CALIBRATE, PID) are
  not active before SAVE_CONFIG + restart**, they are only "pending" (`save_config_pending_items`).
- **SAVE_CONFIG values are ignored if the same option is active above the block.** On load, Klipper
  comments out such autosave values (`configfile.py` `_strip_duplicates`, line ~302). That is why
  SAVE_CONFIG comments out the values above. Anyone who writes printer.cfg themselves (merge, templates)
  must also comment them out. Real bug 2026-11-28: template `z_offset: 0` active → saved 1.307 ignored.
- Jinja tests like `match` don't exist (Ansible only). Runtime errors are not caught by
  `env.from_string`, only by rendering (simulator).
- `SAVE_CONFIG` comments out values in the main `printer.cfg` that are overridden by the autosave block.
  `Z_OFFSET_APPLY_PROBE` computes from the loaded `z_offset`, not from a pending one.
- `manual_probe` always exists as an object (default load), `printer.manual_probe.is_active` is always readable.
- `RESTART` reloads only the config. After changing the Klipper **code** (e.g. switching to the fork),
  the service must restart (`POST /machine/services/restart?service=klipper`).
