Bitte immer das neueste Release herunterladen: [Releases](https://github.com/Bully85/Sovol-SV04-Klipper/releases)

# Sovol-SV04-Klipper
Dieses Repository enthält alle Konfigurationsdateien, mit denen der Sovol SV04 unter Klipper läuft.
Dazu gehören die IDEX-Modi Copy und Mirror, Slicer-Profile, Makros, Bilder und Beschreibungen.

![KlipperSV04](docs/img/sv04klipper.png)


# Spenden

[![Donate with PayPal](https://raw.githubusercontent.com/stefan-niedermann/paypal-donate-button/master/paypal-donate-button.png)](https://www.paypal.com/donate/?hosted_button_id=L85ULXXQKALP6)

Discord: https://discord.gg/22VQXyuq


# Neuigkeiten

Alle Änderungen stehen im [CHANGELOG](CHANGELOG.md).

- **Installation nur noch über ein frisches MainsailOS.** Das fertige Custom-Image wird nicht mehr
  unterstützt. Siehe [Installation](#installation).
- **Neue Makros:** `SV04_MENU`, geführter Z-Offset für beide Düsen, `SAVE_Z_OFFSET`,
  `LOAD_FILAMENT` … ([Kalibrierung & Makros](docs/Kalibrierung-Calibration.md)).
  Beim Update auch `sv04_tools.cfg` kopieren und die **eigene `variables.cfg` behalten**, darin stehen eure T1-Offsets.
- **Neu:** Profile für [Bambu Studio](<Bambu Studio Profile/README.md>).
- Startcode für die Slicer: [Cura](<Cura Profile/Startcode.md>), [PrusaSlicer](<Prusaslicer Profile/Startcode.md>)


# Einleitung

Für die STM32- und die GD32-Version des Druckers braucht ihr leicht unterschiedliche Configs.
Beide stehen in der `printer.cfg`, ihr müsst nur den passenden Block aktivieren
(Abschnitt *Z Stepper Settings*). Welchen Chip ihr habt, seht ihr im Elektronikkasten. Alternativ
führt ihr `Z_TILT_ADJUST` aus: Mit dem falschen Block kommt eine Fehlermeldung.


# Was geht alles?

- Copy-Modus (verschiedene Temperaturen möglich, aber keine eigenen First-Layer-Einstellungen für den rechten Extruder)
- Mirror-Modus (verschiedene Temperaturen möglich, aber keine eigenen First-Layer-Einstellungen für den rechten Extruder)
- Dual-Modus
- Single-Modus (linke oder rechte Düse)
- Bed Mesh nur über den Druckbereich (bei Copy/Mirror inklusive der zweiten Kopie)
- Input Shaper
- Geführte Z-Offset-Kalibrierung für beide Düsen, Filament laden/entladen, Menü für Mainsail/Fluidd ([Details](docs/Kalibrierung-Calibration.md))
- Original-Sovol-Display (nur mit dem [Bully85-Klipper-Fork](#optional-original-sovol-display))
- uvm.


# Slicer-Profile

- [Bambu Studio](<Bambu Studio Profile/README.md>) (Linux-Installer: `./sv04-bambu-install.sh`)
- [PrusaSlicer](<Prusaslicer Profile/README.md>)
- [Cura](<Cura Profile/cura readme.md>) (Linux-Installer für Cura 5.x: `./sv04-cura-install.sh`)

COPY und MIRROR sind in allen Profilen auf 150 mm Breite begrenzt (linke Betthälfte).


# Benötigt

- Raspberry Pi 3 oder neuer mit WLAN
    - Pi Zero funktioniert nicht
    - Pi 2 geht eventuell, wird aber nicht empfohlen
- MicroSD-Karte für den Raspberry Pi (mindestens 16 GB)
- SD-Karte zum Flashen des SV04 (maximal 8 GB, FAT32 mit 4096-Byte-Clustern)
- [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
- SSH-Zugang (Windows-Terminal/PowerShell haben SSH eingebaut, alternativ [PuTTY](https://putty.org/))
- Optional: originaler 7"-Touchscreen (KlipperScreen) und eine Kamera


# Installation

Installiert wird **nur noch auf einem frischen MainsailOS**. MainsailOS bringt das aktuelle
Original-Klipper mit. Deshalb nutzt ihr den Config-Ordner für Original-Klipper:
`config/Sv04-works-with origin-klipper`.

## 1. MainsailOS installieren

1. Raspberry Pi Imager starten und euer Raspberry-Pi-Modell wählen.
2. Betriebssystem: *Other specific-purpose OS → 3D printing → Mainsail OS*.
3. In den Einstellungen (*Einstellungen bearbeiten*) Hostname (z. B. `sv04`), Benutzername,
   Passwort und WLAN eintragen und im Reiter *Dienste* SSH aktivieren.
4. Karte schreiben, in den Pi stecken und starten. Nach ein paar Minuten erreicht ihr Mainsail
   unter `http://sv04.local` (oder über die IP des Pi aus eurem Router).

## 2. Drucker-Firmware bauen und flashen

Die Firmware muss zur Klipper-Version auf dem Pi passen, deshalb baut ihr sie direkt auf dem Pi.
Meldet euch [per SSH](#benutzung-von-ssh) an und führt aus:

```sh
cd ~/klipper
make menuconfig
```

Wählt diese Einstellungen:

| Option | Wert |
|--------|------|
| Micro-controller Architecture | STMicroelectronics STM32 |
| Processor model | STM32F103 |
| Bootloader offset | 28KiB bootloader |
| Clock Reference | 8 MHz crystal |
| Communication interface | Serial (on USART1 PA10/PA9) |
| Baud rate for serial port | 115200 |

Diese Werte gelten auch für die GD32-Version. Speichert mit `Q` → `Y`. Dann baut ihr die Firmware
und kopiert sie in den Config-Ordner, damit ihr sie in Mainsail herunterladen könnt:

```sh
make clean && make
cp out/klipper.bin ~/printer_data/config/firmware.bin
```

Ladet in Mainsail unter *Maschine* die `firmware.bin` herunter und kopiert sie auf die SD-Karte für
den Drucker. Steckt bei **ausgestecktem Original-Display** die Karte ein und schaltet den Drucker
ein. Das Flashen dauert etwa 10 Sekunden. Danach löscht ihr die `firmware.bin` wieder aus dem
Mainsail-Config-Ordner.

## 3. Konfiguration hochladen

1. Ladet in Mainsail unter *Maschine* alle Dateien aus `config/Sv04-works-with origin-klipper` hoch.
   Legt den Unterordner `macro/shell_commands` an und ladet die beiden `adxl_*.sh` dort hinein.
2. Verbindet den Drucker per USB mit dem Pi und prüft per SSH den seriellen Port:
   `ls /dev/serial/by-id/`. Weicht der Name von der `printer.cfg` ab (`[mcu] serial:`), passt ihn dort an.
3. Aktiviert in der `printer.cfg` den passenden *Z Stepper*-Block für euren Chip (STM32 oder GD32).
4. Klickt auf *Speichern & Neustarten*. Klipper sollte jetzt *Ready* melden.

## 4. Kalibrieren

Führt `SV04_MENU` aus und arbeitet die Schritte der Reihe nach ab. Siehe [Kalibrierung & Makros](docs/Kalibrierung-Calibration.md).

## Optional: Original-Sovol-Display

Das originale Sovol-Display (DGUS/T5UID1) funktioniert nur mit dem Klipper-Fork
[Bully85/klipper](https://github.com/Bully85/klipper). Wer es braucht, stellt Klipper auf dem
frischen MainsailOS per SSH auf den Fork um:

```sh
cd ~/klipper
git remote set-url origin https://github.com/Bully85/klipper
git fetch origin
git checkout -B master origin/master
sudo systemctl restart klipper
```

Danach geht ihr statt wie oben so vor:

- Die Firmware baut ihr wie in [Schritt 2](#2-drucker-firmware-bauen-und-flashen). Der Fork bietet
  in `make menuconfig` zusätzlich die T5UID1-Option. Alternativ flasht ihr die fertige
  `Firmware bin/firmware.bin`.
- Statt `Sv04-works-with origin-klipper` ladet ihr `config/SV04-with-display` hoch.
- Die Meldung „ungültig“ in Mainsail behebt ihr so:

```sh
sudo nano ~/printer_data/systemd/moonraker.env
```
![moonraker.env1](docs/img/moonraker.env1.JPG)

Fügt `-g` am Ende der Zeile `MOONRAKER_ARGS` an:
![moonraker.env2](docs/img/moonraker.env2.JPG)

Speichert, startet neu, klickt in Mainsail auf *ungültig* und führt einen *Soft Repair* durch.

## Optional: Touchscreen (KlipperScreen)

Installiert KlipperScreen mit [KIAUH](https://github.com/dw-0/kiauh). Danach ladet ihr die
`KlipperScreen.conf` aus dem Config-Ordner hoch.


# Update

Ladet die geänderten Dateien aus dem Config-Ordner hoch. Die `variables.cfg` und den Block
`#*# SAVE_CONFIG` am Ende eurer `printer.cfg` überschreibt ihr nicht, darin stehen eure
Kalibrierwerte. Was sich geändert hat, steht im [CHANGELOG](CHANGELOG.md).


# Benutzung von SSH

- Öffnet das Windows-Terminal oder die PowerShell (unter Linux/macOS: Terminal).
- Verbindet euch mit `ssh benutzername@hostname` (wie im Raspberry Pi Imager eingestellt) und gebt das Passwort ein.
- Beenden mit Ctrl+D.


# Für Entwickler und KI-Assistenten

[LLM-WIKI.md](LLM-WIKI.md) beschreibt Aufbau, Konventionen, Fallstricke und Testmethoden dieses Repos.
