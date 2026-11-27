# Hardware ideas (upgrades)

Ideas that need hardware changes. Look at them when you are working on the printer anyway.
The user-facing overview with all upgrades, Bambu compatibility and benefits is in
[docs/Upgrades-Bambu-Standard.md](../docs/Upgrades-Bambu-Standard.md).

**Bambu compatibility (researched 2026-11-26):** Bambu plates are 257 mm (SV04 needs 310 × 320).
Nozzles/extruders/AMS are proprietary. Only the **X1/P1 hotend** can be fitted to other printers with
an adapter (SV08/Neptune 4/Ender 3 templates, 24 V/48 W, NTC 100K, no SV04 mount yet). The
**H2/P2S** and A1 hotends are a different quick-swap system (Bambu: X1/P1 "Not Supported").
Hardware base: [printer-hardware](printer-hardware.md).
The user can print their own mounts/housings (2026-11-26), so "no ready-made SV04 mount" is not a
blocker. Design rules are in the upgrade guide ("Eigene Halter drucken").

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
