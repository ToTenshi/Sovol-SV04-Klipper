# Findings from the Klipper source

Read via `gh api repos/<repo>/contents/<file>` on 2026-11-24/25. Fork = `Bully85/klipper` (master,
latest commit 2024-01-26), mainline = `Klipper3d/klipper` (master at that time).

- **Fork `klippy/toolhead.py`:** only knows `max_accel_to_decel` (lines 221/564/603), no `minimum_cruise_ratio`.
- **Fork `klippy/kinematics/idex_modes.py` get_status():** `{'carriage_%d' % i: dc.mode}`, no `mode`.
  **Mainline:** additionally `carriages`, plus `carriage_0/1` when there are 2 carriages.
- **Fork `extras/manual_probe.py`:** object loaded by default (klippy.py: list with `"manual_probe"`).
  Status `is_active`, `z_position`, …; `finalize` resets the status.
- **Fork `extras/probe.py` cmd_Z_OFFSET_APPLY_PROBE:** `new = self.z_offset - homing_origin.z`, `configfile.set`.
- **Fork `configfile.py`:** status `save_config_pending`, `save_config_pending_items`.
- **Fork `gcode_macro.py`:** `SET_GCODE_VARIABLE` uses `ast.literal_eval`.
- **Mainline `extras/input_shaper.py` connect():** with `dual_carriage` and enabled values in
  `[input_shaper]` → `config_error` "Input shaper parameters cannot be configured via [input_shaper]
  section with dual_carriage(s) enabled". Reacts to the `dual_carriage:update_kinematics` event.
- **Fork `extras/input_shaper.py`:** no dual_carriage check, only x/y.
- **Mainline `extras/resonance_tester.py` cmd_SHAPER_CALIBRATE:** `apply_params` (live
  SET_INPUT_SHAPER) **and** `save_params` → `configfile.set('input_shaper', 'shaper_type_<axis>'/'shaper_freq_<axis>')`.
- **Kconfig (`src/stm32/Kconfig`, both):** `MACH_STM32F103`, `STM32_FLASH_START_7000`, `STM32_CLOCK_REF_8M`,
  `STM32_SERIAL_USART1`, `SERIAL_BAUD` exist.
- **Fork `src/stm32/t5uid1/Kconfig`:** `T5UID1_SERIAL` ("Enable DGUS T5UID1 screen"), choice
  "Screen serial interface" (only with `LOW_LEVEL_OPTIONS`), option `STM32_T5UID1_SERIAL_USART3_PB11_PB10`.
- **`KlipperScreen/scripts/KlipperScreen-install.sh`:** interactive (`read -p`: backend X11/Wayland,
  NetworkManager, service), does not add an update_manager entry.
- **`klippy/gcode.py` (both versions):** `args_r = re.compile('([A-Z_]+|[A-Z*])')` (fork: `[A-Z*/]`),
  `cmd = parts[1] + parts[2].strip()`. So a name like `SV04_MENU` becomes the command `SV04`.
  Real error on 2026-11-25: `Unknown command:"_SV04"` on SAVE_CONFIG (macro `_SV04_SAVE_CONFIG_BASE`).
- **`klippy/extras/gcode_move.py` (mainline, read 2026-11-28):** `cmd_G1` only sets `last_position`
  for the given axes (`v + base_position`), missing axes keep the kinematic position.
  `cmd_SET_GCODE_OFFSET` only changes `base_position`/`homing_position`, it only moves the toolhead with
  `MOVE=1`. `cmd_RESTORE_GCODE_STATE` restores modes/`base_position`/`homing_position` and only
  `last_position` (back to the saved position) with `MOVE=1`.
