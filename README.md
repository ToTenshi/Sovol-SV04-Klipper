Please use the newest release for download: [Releases](https://github.com/Bully85/Sovol-SV04-Klipper/releases)

# Sovol-SV04-Klipper
This repository contains all the configuration files the Sovol SV04 needs to run Klipper,
including the IDEX modes Copy and Mirror, slicer profiles, macros, pictures and descriptions.

![KlipperSV04](docs/img/sv04klipper.png)

# Spenden/Donations

[![Donate with PayPal](https://raw.githubusercontent.com/stefan-niedermann/paypal-donate-button/master/paypal-donate-button.png)](https://www.paypal.com/donate/?hosted_button_id=L85ULXXQKALP6)

# _Für die deutsche Anleitung wählt bitte [READMEdeutsch.md](READMEdeutsch.md)_

Discord: https://discord.gg/22VQXyuq

# News

All changes are listed in the [CHANGELOG](CHANGELOG.md).

- **Mainsail inside Bambu Studio:** the Bambu profiles are pre-connected to `sv04.local`. The **Device**
  tab shows Mainsail, and *Print plate* uploads and starts the job. Other address: `--host` when installing.
- **Better leveling:** more accurate probing, bed mesh up to the bed edges, mesh fade, `BED_SCREWS_CHECK`,
  `PROBE_CHECK` (how repeatable is the BLTouch?).
  `--update` now also updates `printer.cfg` (port, chip and SAVE_CONFIG values are kept).
- **Change the Z offset during the print:** `Z_OFFSET_MENU` (dialog with ±0.01/±0.05 and Save),
  `Z_OFFSET_DOWN` / `Z_OFFSET_UP`.
- **Z offset fixed:** a measured value is used by the next print even before SAVE_CONFIG. The Mainsail
  Z offset panel (babystep + save) and `SAVE_Z_OFFSET` do the same thing. Z is re-homed after the Z tilt.
- **Renamed macros (important when updating):** `SOVOL_MENU` (was SV04_MENU), `CALIBRATE_Z_T1`,
  `SET_OFFSET_T1`. The old names couldn't be called by Klipper (digits in the middle of the name).

- **Installation only via a fresh MainsailOS.** The pre-made custom image is no longer supported.
  See [Installation](#installation). You don't need KIAUH: the new script `install/sv04-pi-setup.sh`
  sets up config, chip, serial port and firmware on the Pi.
- **Slicer installers for Windows, macOS and Linux:** `install/install-slicer-profiles-windows.cmd` or
  `install/install-slicer-profiles.sh` (Bambu Studio, Cura, PrusaSlicer).
- **New macros:** `SOVOL_MENU`, guided Z offset for both nozzles, `SAVE_Z_OFFSET`,
  `LOAD_FILAMENT` … ([Calibration & macros](docs/Kalibrierung-Calibration.md)).
  When updating, also copy `sv04_tools.cfg` and **keep your own `variables.cfg`**, because it holds your T1 offsets.
- **Input shaping without a sensor:** a preset is active by default and allows 1500 instead of 1000 mm/s².
  With an ADXL345, measure per carriage with `SHAPER_CALIBRATE_SV04` ([details](docs/Kalibrierung-Calibration.md#input-shaper)).
  When updating, also copy `input_shaper.cfg`. The `macro/shell_commands` folder is no longer needed.
- **New:** profiles for [Bambu Studio](<Bambu Studio Profile/README.md>).
- Start code for the slicers: [Cura](<Cura Profile/Startcode.md>), [PrusaSlicer](<Prusaslicer Profile/Startcode.md>)

# Introduction

The STM32 and GD32 versions of the printer need slightly different configs.
Both are included in `printer.cfg`, and you only need to uncomment the right block
(section *Z Stepper Settings*). You can check your chip by opening the electronics box, or by
running `Z_TILT_ADJUST`: with the wrong block, you get an error message.

# Features

- Copy mode (different temperatures possible, no separate first layer settings for the right extruder)
- Mirror mode (different temperatures possible, no separate first layer settings for the right extruder)
- Dual mode
- Single mode (left or right nozzle)
- Bed mesh only over the print area (also covers the second copy in Copy/Mirror)
- Input shaping: preset without a sensor (default) or measured per carriage with an ADXL345
- Guided Z offset calibration for both nozzles, filament load/unload, menu for Mainsail/Fluidd ([details](docs/Kalibrierung-Calibration.md))
- Original Sovol display (only with the [Bully85 Klipper fork](#optional-original-sovol-display))
- And much more

# Slicer profiles

Install all profiles at once (Bambu Studio, Cura 4/5, PrusaSlicer). Close the slicers first:

| System | How |
|--------|-----|
| Windows | Double-click `install/install-slicer-profiles-windows.cmd` |
| macOS / Linux | In a terminal in the repo folder: `./install/install-slicer-profiles.sh` |

The script finds the installed slicers (on Linux also Flatpak) and copies the printer, process and
filament profiles plus the 3D bed model. Bambu Studio and PrusaSlicer upload directly to the printer
(`sv04.local`, or another address with `--host 192.168.1.50` / Windows `-PrinterHost 192.168.1.50`).
Bambu Studio shows Mainsail in its **Device** tab. Details and manual installation:
[Bambu Studio](<Bambu Studio Profile/README.md>), [PrusaSlicer](<Prusaslicer Profile/README.md>),
[Cura](<Cura Profile/cura readme.md>).

In all profiles, COPY and MIRROR are limited to a 150 mm wide print area (left half of the bed).

# Requirements

- Raspberry Pi 3 or newer with Wi-Fi
    - Pi Zero won't work
    - Pi 2 may work, but is not recommended
- MicroSD card for the Raspberry Pi (at least 16 GB)
- SD card to flash the SV04 (max. 8 GB, FAT32 with 4096-byte clusters)
- [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
- SSH access (Windows Terminal/PowerShell have it built in, alternatively [PuTTY](https://putty.org/))
- Optional: original 7" touch screen (KlipperScreen) and a camera

# Installation

Installation is done **only on a fresh MainsailOS**. You don't need KIAUH. MainsailOS (official,
via the Raspberry Pi Imager) already contains Klipper, Moonraker and Mainsail. Everything
SV04-specific is then done by **one script** on the Pi.

## 1. Install MainsailOS

1. Start the Raspberry Pi Imager and choose your Raspberry Pi model.
2. Operating system: *Other specific-purpose OS → 3D printing → Mainsail OS*.
3. In the settings (*Edit settings*), set the hostname (e.g. `sv04`), user name, password and
   Wi-Fi, and enable SSH in the *Services* tab.
4. Write the card, put it into the Pi and boot. After a few minutes Mainsail opens at
   `http://sv04.local` (or via the Pi's IP from your router).

## 2. Set up the SV04 with the script (recommended)

**First update MainsailOS:** In Mainsail under *Machine → Update Manager*, click *Update all*.
The image often ships an older Klipper, and the firmware must be built from the current version
(the script checks this).

Connect the printer to the Pi via USB and switch it on. Then connect [via SSH](#using-ssh) and run:

```sh
git clone -b sv04-bambu-calibration https://github.com/ToTenshi/Sovol-SV04-Klipper.git ~/Sovol-SV04-Klipper
~/Sovol-SV04-Klipper/install/sv04-pi-setup.sh
```

The script asks a few questions (with the recommended answer as default) and then:

- backs up `~/printer_data/config` and copies the SV04 configuration (original Klipper, or the
  Bully85 fork for the original Sovol display),
- enables the matching Z stepper block for your chip (STM32 or GD32) and enters the serial port,
- builds the printer firmware with the right settings (no `make menuconfig`) and puts it into
  the Mainsail config folder as `firmware.bin`,
- optionally installs KlipperScreen with its official installer,
- arranges the macros in Mainsail as tidy groups (see below),
- restarts Klipper.

## 3. Flash the firmware

In Mainsail under *Machine*, download `firmware.bin` and copy it onto the SD card for the printer.
With the **original display unplugged**, insert the card and switch the printer on. Flashing takes
about 10 seconds. Then delete `firmware.bin` from the Mainsail config folder again.

## 4. Calibrate

Run `SOVOL_MENU` and work through the steps in order. See [Calibration & macros](docs/Kalibrierung-Calibration.md).

## Tidy macros in Mainsail

The script (or `python3 ~/Sovol-SV04-Klipper/install/mainsail_macro_groups.py` on the Pi) creates five
macro panels on the dashboard and switches Mainsail to expert mode. Then only these panels are shown,
not every internal macro:

| Panel | Macros | Visible |
|-------|--------|---------|
| 1 SV04 | `SOVOL_MENU`, `LOAD_FILAMENT`, `UNLOAD_FILAMENT` | standby, paused |
| 2 During print | `Z_OFFSET_MENU`, `Z_OFFSET_DOWN/UP` (babystep), `SAVE_Z_OFFSET`, `M600` (printing only) | always |
| 3 Calibration | Z tilt, bed screws, Z offset T0/T1, PID, input shaper | standby |
| 4 IDEX | `T0`, `T1`, Copy/Mirror mode, `CLEAN_NOZZLE` | standby |
| 5 Settings | `SET_OFFSET_T1`, `INPUT_SHAPER_SET`, `PREHEAT60/80` | standby |

Reload Mainsail afterwards (F5). Your own groups are kept. You can move, rename or change the panels
under *Settings → Macros*. `--remove` removes the SV04 groups again.

## Manual setup (without the script)

<details>
<summary>Build the firmware and upload the configuration by hand</summary>

### Build the firmware

Via SSH: `cd ~/klipper && make menuconfig` and choose:

| Option | Value |
|--------|-------|
| Micro-controller Architecture | STMicroelectronics STM32 |
| Processor model | STM32F103 |
| Bootloader offset | 28KiB bootloader |
| Clock Reference | 8 MHz crystal |
| Communication interface | Serial (on USART1 PA10/PA9) |
| Baud rate for serial port | 115200 |

These values also work for the GD32 version. Save with `Q` → `Y`, then
`make clean && make && cp out/klipper.bin ~/printer_data/config/firmware.bin`.

### Upload the configuration

1. In Mainsail under *Machine*, upload all files from `config/Sv04-works-with origin-klipper`.
2. Check the serial port via SSH with `ls /dev/serial/by-id/` and enter it in `printer.cfg` under `[mcu] serial:`.
3. In `printer.cfg`, enable the matching *Z Stepper* block for your chip (STM32 or GD32).
4. Click *Save & Restart*.

</details>

## Optional: ADXL345 for input shaping

Without a sensor, a preset is active. To measure your printer, connect an ADXL345 to the Pi,
set up the Pi as a second MCU, and enable `[include adxl345.cfg]` in `printer.cfg`.
See [Calibration & macros](docs/Kalibrierung-Calibration.md#input-shaper).

## Optional: original Sovol display

The original Sovol display (DGUS/T5UID1) only works with the Klipper fork
[Bully85/klipper](https://github.com/Bully85/klipper). If you answer `display` in the script, it
switches Klipper to the fork, uses `config/SV04-with-display` and builds the firmware with display
support. Manually:

```sh
cd ~/klipper
git remote set-url origin https://github.com/Bully85/klipper
git fetch origin
git checkout -B master origin/master
sudo systemctl restart klipper
```

In `make menuconfig`, also enable *Enable extra low-level configuration options*, then
*Enable DGUS T5UID1 screen* → *USART3 (on PB11/PB10)*. Alternatively, flash the ready-made
`Firmware bin/firmware.bin`.

Fix the "invalid" message in Mainsail:

```sh
sudo nano ~/printer_data/systemd/moonraker.env
```
![moonraker.env1](docs/img/moonraker.env1.JPG)

Append `-g` to the end of the `MOONRAKER_ARGS` line:
![moonraker.env2](docs/img/moonraker.env2.JPG)

Save, reboot, then click *invalid* in Mainsail and run a *soft repair*.

## Optional: touch screen (KlipperScreen)

The script asks for it and uses the official installer. Manually:
`git clone https://github.com/KlipperScreen/KlipperScreen.git && ./KlipperScreen/scripts/KlipperScreen-install.sh`.
Then upload `KlipperScreen.conf` from the config folder.

# Updating

```sh
git -C ~/Sovol-SV04-Klipper pull
~/Sovol-SV04-Klipper/install/sv04-pi-setup.sh --update
```

`--update` refreshes the macro files. If the firmware on the printer doesn't match Klipper on the Pi
(Klipper then warns "MCU 'mcu' has deprecated code … Recompiling and flashing is recommended"), it
offers to build the matching `firmware.bin`. Flash it as in step 3. For `printer.cfg` it shows the changes and asks first. Your
serial port, chip, includes and the `#*# SAVE_CONFIG` block (Z offset, PID) are kept. `variables.cfg`
is not touched, and a backup is made beforehand. What changed is listed in the
[CHANGELOG](CHANGELOG.md). If you update without the script, don't overwrite these two files.

# Using SSH

- Open Windows Terminal or PowerShell (on Linux/macOS: Terminal).
- Connect with `ssh username@hostname` (as set in the Raspberry Pi Imager) and enter your password.
- Exit with Ctrl+D.

# For developers and AI assistants

The [wiki](wiki/index.md) describes the structure, conventions, pitfalls and test methods of this repository.
