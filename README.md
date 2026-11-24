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

- **Installation only via a fresh MainsailOS.** The pre-made custom image is no longer supported.
  See [Installation](#installation).
- **New macros:** `SV04_MENU`, guided Z offset for both nozzles, `SAVE_Z_OFFSET`,
  `LOAD_FILAMENT` … ([Calibration & macros](docs/Kalibrierung-Calibration.md)).
  When updating, also copy `sv04_tools.cfg` and **keep your own `variables.cfg`**, because it holds your T1 offsets.
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
- Input shaping
- Guided Z offset calibration for both nozzles, filament load/unload, menu for Mainsail/Fluidd ([details](docs/Kalibrierung-Calibration.md))
- Original Sovol display (only with the [Bully85 Klipper fork](#optional-original-sovol-display))
- And much more

# Slicer profiles

- [Bambu Studio](<Bambu Studio Profile/README.md>) (Linux installer: `./sv04-bambu-install.sh`)
- [PrusaSlicer](<Prusaslicer Profile/README.md>)
- [Cura](<Cura Profile/cura readme.md>) (Linux installer for Cura 5.x: `./sv04-cura-install.sh`)

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

Installation is done **only on a fresh MainsailOS**. MainsailOS ships the current original Klipper,
so the config folder for original Klipper is used:
`config/Sv04-works-with origin-klipper`.

## 1. Install MainsailOS

1. Start the Raspberry Pi Imager and choose your Raspberry Pi model.
2. Operating system: *Other specific-purpose OS → 3D printing → Mainsail OS*.
3. In the settings (*Edit settings*), set the hostname (e.g. `sv04`), user name, password and
   Wi-Fi, and enable SSH in the *Services* tab.
4. Write the card, put it into the Pi and boot. After a few minutes Mainsail opens at
   `http://sv04.local` (or via the Pi's IP from your router).

## 2. Build and flash the printer firmware

The firmware must match the Klipper version on the Pi, so it is built on the Pi itself.
Connect [via SSH](#using-ssh) and run:

```sh
cd ~/klipper
make menuconfig
```

Choose these settings:

| Option | Value |
|--------|-------|
| Micro-controller Architecture | STMicroelectronics STM32 |
| Processor model | STM32F103 |
| Bootloader offset | 28KiB bootloader |
| Clock Reference | 8 MHz crystal |
| Communication interface | Serial (on USART1 PA10/PA9) |
| Baud rate for serial port | 115200 |

These values also work for the GD32 version. Save with `Q` → `Y`, then build the firmware and
copy it into the config folder, so you can download it in Mainsail:

```sh
make clean && make
cp out/klipper.bin ~/printer_data/config/firmware.bin
```

In Mainsail, go to *Machine*, download `firmware.bin` and copy it onto the SD card for the printer.
With the **original display unplugged**, insert the card and switch the printer on. Flashing
takes about 10 seconds. Then delete `firmware.bin` from the Mainsail config folder again.

## 3. Upload the configuration

1. In Mainsail under *Machine*, upload all files from `config/Sv04-works-with origin-klipper`.
   Create the subfolder `macro/shell_commands` and upload the two `adxl_*.sh` files there.
2. Connect the printer to the Pi via USB and check the serial port via SSH:
   `ls /dev/serial/by-id/`. If the name differs from `printer.cfg` (`[mcu] serial:`), change it there.
3. In `printer.cfg`, enable the matching *Z Stepper* block for your chip (STM32 or GD32).
4. Click *Save & Restart*. Klipper should now show *Ready*.

## 4. Calibrate

Run `SV04_MENU` and work through the steps in order. See [Calibration & macros](docs/Kalibrierung-Calibration.md).

## Optional: original Sovol display

The original Sovol display (DGUS/T5UID1) only works with the Klipper fork
[Bully85/klipper](https://github.com/Bully85/klipper). If you need it, switch Klipper on the fresh
MainsailOS to the fork via SSH:

```sh
cd ~/klipper
git remote set-url origin https://github.com/Bully85/klipper
git fetch origin
git checkout -B master origin/master
sudo systemctl restart klipper
```

Then do this instead of the steps above:

- Build the firmware as in [step 2](#2-build-and-flash-the-printer-firmware). The fork offers
  the T5UID1 option in `make menuconfig`. Alternatively, flash the ready-made `Firmware bin/firmware.bin`.
- Upload `config/SV04-with-display` instead of `Sv04-works-with origin-klipper`.
- Fix the "invalid" message in Mainsail:

```sh
sudo nano ~/printer_data/systemd/moonraker.env
```
![moonraker.env1](docs/img/moonraker.env1.JPG)

Append `-g` to the end of the `MOONRAKER_ARGS` line:
![moonraker.env2](docs/img/moonraker.env2.JPG)

Save, reboot, then click *invalid* in Mainsail and run a *soft repair*.

## Optional: touch screen (KlipperScreen)

Install KlipperScreen with [KIAUH](https://github.com/dw-0/kiauh). Then upload `KlipperScreen.conf`
from the config folder.

# Updating

Upload the changed files from the config folder. Don't overwrite `variables.cfg`, and don't
overwrite the `#*# SAVE_CONFIG` block at the end of your `printer.cfg`, because these hold your
calibration values. What changed is listed in the [CHANGELOG](CHANGELOG.md).

# Using SSH

- Open Windows Terminal or PowerShell (on Linux/macOS: Terminal).
- Connect with `ssh username@hostname` (as set in the Raspberry Pi Imager) and enter your password.
- Exit with Ctrl+D.

# For developers and AI assistants

[LLM-WIKI.md](LLM-WIKI.md) describes the structure, conventions, pitfalls and test methods of this repository.
