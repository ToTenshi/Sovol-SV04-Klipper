# Installation

## Why MainsailOS without KIAUH

The official route, recommended by Mainsail, is the MainsailOS image from the Raspberry Pi Imager.
It already contains Klipper, Moonraker and Mainsail. KIAUH is only needed for extras like
KlipperScreen, which has its own official installer
([research](sources/2026-11-25_web-research.md)). Docker setups (e.g. prind) don't help on the Pi.
That's why everything SV04-specific is handled by `install/sv04-pi-setup.sh`.

## `install/sv04-pi-setup.sh` (on the Pi)

Flow: variant (original/display) → **version check** (original: Klipper commit < 2024-03-14 → stop
with "update in Mainsail first", because old MainsailOS images ship an old Klipper and the firmware
must be built from the current one) → Klipper switch if needed (`switch_klipper`: `git remote set-url` + `checkout -B master
origin/master` + `pip install -r scripts/klippy-requirements.txt`). `display` → fork, `original` on a
fork → back to Klipper3d. Detection via `origin` contains "bully85" → `tar` backup of `~/printer_data/config` → copy config → chip/port → firmware →
optional KlipperScreen → restart.

- **Copy rules:** `variables.cfg` is never overwritten if it exists. `printer.cfg` is kept if it already
  contains `[dual_carriage]` (SV04 config). The MainsailOS default `printer.cfg` is replaced.
  Everything else is overwritten. `--update` copies only the macro files.
- **GD32:** awk comments out the STM32 block and uncomments the GD32 block (between the banners up to `#####…`).
- **Port:** exactly one device in `/dev/serial/by-id` → it is used. Several → `1a86` is preferred and the script asks.
- **Firmware:** writes `.config` (see [printer-hardware](printer-hardware.md)), `make olddefconfig`,
  **checks** that every option was accepted (otherwise it aborts), builds and copies to
  `~/printer_data/config/firmware.bin` (download via Mainsail).
- **KlipperScreen:** clone + `scripts/KlipperScreen-install.sh` (interactive), plus an
  `[update_manager KlipperScreen]` entry in `moonraker.conf`.
- **Mainsail macros:** `install/mainsail_macro_groups.py` ([mainsail](mainsail.md)), asked as step 6,
  always run with `--update`.
- **Restart:** via the Moonraker API (`/printer/restart`, after a fork switch
  `/machine/services/restart?service=klipper`), fallback `sudo systemctl`.
- Test variables: `SV04_KLIPPER_DIR`, `SV04_CONFIG_DIR`, `SV04_SERIAL_DIR`, `SV04_MOONRAKER_URL`.

## Slicer installers

| Slicer | Linux | macOS | Windows |
|--------|-------|-------|---------|
| Bambu Studio | `~/.config/BambuStudio`, Flatpak `~/.var/app/com.bambulab.BambuStudio/config/BambuStudio` | `~/Library/Application Support/BambuStudio` | `%APPDATA%\BambuStudio` |
| Cura | `~/.local/share/cura/<ver>`, Flatpak `~/.var/app/com.ultimaker.cura/data/cura/<ver>` | `~/Library/Application Support/cura/<ver>` | `%APPDATA%\cura\<ver>` |
| PrusaSlicer | `~/.config/PrusaSlicer`, Flatpak `~/.var/app/com.prusa3d.PrusaSlicer/config/PrusaSlicer` | `~/Library/Application Support/PrusaSlicer` | `%APPDATA%\PrusaSlicer` |

- Bambu: presets into `user/default` **and** every `user/<account-ID>` (logged in → cloud sync).
- `install-slicer-profiles.sh` is bash-3.2 compatible (macOS) and uses only `sed`/`awk`/`grep`
  (no Python). `SV04_OS=Darwin` simulates macOS for tests.
- `install-slicer-profiles.ps1` is pure ASCII (Windows PowerShell 5.1 reads files without a BOM as ANSI)
  and writes UTF-8 **without** a BOM. `.gitattributes` enforces CRLF for `.ps1`/`.cmd`.
