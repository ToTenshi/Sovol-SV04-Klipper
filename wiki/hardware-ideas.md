# Hardware ideas (upgrades)

Ideas that need hardware changes. Look at them when you are working on the printer anyway.

## Load cell for automatic Z offset ⭐ (user wish, 2026-11-26)

- **Goal:** set the Z offset automatically, without a paper test. A load cell measures the force when the
  nozzle touches the bed, so it measures exactly where the bed is, with the nozzle itself.
  Prusa MK4/XL and Bambu Lab do it this way.
- **Klipper:** mainline has `[load_cell]` / `[load_cell_probe]` (since 2025). The original
  Klipper variant of this repo is required, the Bully85 fork (January 2024) doesn't have it.
- **SV04 specifics:** two print heads, so one load cell per carriage, or one in the bed (bed load cells
  measure both nozzles). Requires an ADC module (e.g. HX711/HX717 or ADS1220) and a free MCU input, or a
  separate small MCU board (RP2040), plus mechanical integration.
- **Payoff:** Z offset T0 and T1 automatic and exact. The probe offset and the paper test would no longer be needed.
- **Status:** idea, nothing done yet. Before starting: check which load cell kits exist for
  IDEX/bed mounting and check the current Klipper docs (`Load_Cell.md`).

## Eddy current sensor (e.g. BTT Eddy)

- Replaces the BLTouch, measures the bed without contact and very fast (bed mesh in seconds).
- The Z offset still has to be set once (paper test), and it needs temperature compensation.

## Why not "sensorless" Z (motor resistance/StallGuard)

- The SV04 drivers run in step/dir mode (no `[tmc…]` section in the config), so there is no load
  feedback to Klipper.
- Even with TMC UART drivers, it would be too imprecise and too risky on Z (two lead screws with 8 mm
  pitch, high reduction). The nozzle would already be pressing on the bed. Klipper advises against
  sensorless homing on Z. Needed: ±0.01 mm.
