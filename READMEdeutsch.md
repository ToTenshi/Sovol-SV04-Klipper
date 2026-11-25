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

- **Mainsail in Bambu Studio:** Die Bambu-Profile sind mit `sv04.local` vorverbunden. Der Reiter
  **Gerät** zeigt Mainsail, *Platte drucken* lädt hoch und startet den Druck. Andere Adresse: `--host` beim Installieren.
- **Besseres Leveling:** genauere Messung, Bed Mesh bis an den Bettrand, Mesh-Fade, `BED_SCREWS_CHECK`.
  `--update` aktualisiert jetzt auch die `printer.cfg` (Port, Chip und SAVE_CONFIG-Werte bleiben).
- **Z-Offset während des Drucks ändern:** `Z_OFFSET_MENU` (Dialog mit ±0.01/±0.05 und Speichern),
  `Z_OFFSET_DOWN` / `Z_OFFSET_UP`.
- **Z-Offset korrigiert:** Ein gemessener Wert gilt schon beim nächsten Druck, auch vor SAVE_CONFIG.
  Das Mainsail-Panel „Z-Offset“ (Babystep + Speichern) und `SAVE_Z_OFFSET` machen dasselbe. Nach
  dem Z-Tilt wird Z neu gehomt.
- **Makros umbenannt (wichtig beim Update):** `SOVOL_MENU` (vorher SV04_MENU), `CALIBRATE_Z_T1`,
  `SET_OFFSET_T1`. Die alten Namen konnte Klipper nicht aufrufen (Ziffern mitten im Namen).

- **Installation nur noch über ein frisches MainsailOS.** Das fertige Custom-Image wird nicht mehr
  unterstützt. Siehe [Installation](#installation). KIAUH braucht ihr nicht: Das neue Skript
  `install/sv04-pi-setup.sh` richtet Config, Chip, Port und Firmware auf dem Pi ein.
- **Slicer-Installer für Windows, macOS und Linux:** `install/install-slicer-profiles-windows.cmd` bzw.
  `install/install-slicer-profiles.sh` (Bambu Studio, Cura, PrusaSlicer).
- **Neue Makros:** `SOVOL_MENU`, geführter Z-Offset für beide Düsen, `SAVE_Z_OFFSET`,
  `LOAD_FILAMENT` … ([Kalibrierung & Makros](docs/Kalibrierung-Calibration.md)).
  Beim Update auch `sv04_tools.cfg` kopieren und die **eigene `variables.cfg` behalten**, darin stehen eure T1-Offsets.
- **Input Shaping ohne Sensor:** Ein Preset ist standardmäßig aktiv und erlaubt 1500 statt 1000 mm/s².
  Mit einem ADXL345 messt ihr pro Schlitten mit `SHAPER_CALIBRATE_SV04` ([Details](docs/Kalibrierung-Calibration.md#input-shaper)).
  Beim Update auch `input_shaper.cfg` kopieren. Der Ordner `macro/shell_commands` wird nicht mehr gebraucht.
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
- Input Shaper: Preset ohne Sensor (Standard) oder pro Schlitten mit einem ADXL345 gemessen
- Geführte Z-Offset-Kalibrierung für beide Düsen, Filament laden/entladen, Menü für Mainsail/Fluidd ([Details](docs/Kalibrierung-Calibration.md))
- Original-Sovol-Display (nur mit dem [Bully85-Klipper-Fork](#optional-original-sovol-display))
- uvm.


# Slicer-Profile

Alle Profile auf einmal installieren (Bambu Studio, Cura 4/5, PrusaSlicer). Schließt vorher die Slicer:

| System | So geht's |
|--------|-----------|
| Windows | Doppelklick auf `install/install-slicer-profiles-windows.cmd` |
| macOS / Linux | Im Terminal im Repo-Ordner: `./install/install-slicer-profiles.sh` |

Das Skript findet die installierten Slicer (unter Linux auch Flatpak). Es kopiert die Drucker-,
Prozess- und Filamentprofile sowie das 3D-Bettmodell. Bambu Studio und PrusaSlicer laden direkt
auf den Drucker hoch (`sv04.local`, andere Adresse mit `--host 192.168.1.50` bzw. unter Windows
`-PrinterHost 192.168.1.50`). Bambu Studio zeigt Mainsail im Reiter **Gerät**. Details und manuelle Installation:
[Bambu Studio](<Bambu Studio Profile/README.md>), [PrusaSlicer](<Prusaslicer Profile/README.md>),
[Cura](<Cura Profile/cura readme.md>).

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

Installiert wird **nur noch auf einem frischen MainsailOS**, KIAUH braucht ihr nicht. MainsailOS
(offiziell, über den Raspberry Pi Imager) bringt Klipper, Moonraker und Mainsail schon mit. Alles
SV04-Spezifische erledigt danach **ein Skript** auf dem Pi.

## 1. MainsailOS installieren

1. Raspberry Pi Imager starten und euer Raspberry-Pi-Modell wählen.
2. Betriebssystem: *Other specific-purpose OS → 3D printing → Mainsail OS*.
3. In den Einstellungen (*Einstellungen bearbeiten*) Hostname (z. B. `sv04`), Benutzername,
   Passwort und WLAN eintragen und im Reiter *Dienste* SSH aktivieren.
4. Karte schreiben, in den Pi stecken und starten. Nach ein paar Minuten erreicht ihr Mainsail
   unter `http://sv04.local` (oder über die IP des Pi aus eurem Router).

## 2. SV04 per Skript einrichten (empfohlen)

**Zuerst MainsailOS aktualisieren:** In Mainsail unter *Maschine → Update Manager* auf
*Alles aktualisieren* klicken. Das Image bringt oft ein älteres Klipper mit, und die Firmware muss
aus der aktuellen Version gebaut werden (das Skript prüft das).

Verbindet den Drucker per USB mit dem Pi und schaltet ihn ein. Dann meldet euch
[per SSH](#benutzung-von-ssh) an und führt aus:

```sh
git clone -b sv04-bambu-calibration https://github.com/ToTenshi/Sovol-SV04-Klipper.git ~/Sovol-SV04-Klipper
~/Sovol-SV04-Klipper/install/sv04-pi-setup.sh
```

Das Skript stellt ein paar Fragen (die empfohlene Antwort ist vorausgewählt) und dann:

- sichert `~/printer_data/config` und kopiert die SV04-Konfiguration (Original-Klipper, oder den
  Bully85-Fork für das Original-Sovol-Display),
- aktiviert den passenden Z-Stepper-Block für euren Chip (STM32 oder GD32) und trägt den seriellen Port ein,
- baut die Drucker-Firmware mit den richtigen Einstellungen (ohne `make menuconfig`) und legt sie
  als `firmware.bin` in den Mainsail-Config-Ordner,
- installiert auf Wunsch KlipperScreen mit dessen offiziellem Installer,
- ordnet die Makros in Mainsail übersichtlich in Gruppen (siehe unten),
- startet Klipper neu.

## 3. Firmware flashen

Ladet in Mainsail unter *Maschine* die `firmware.bin` herunter und kopiert sie auf die SD-Karte für
den Drucker. Steckt bei **ausgestecktem Original-Display** die Karte ein und schaltet den Drucker
ein. Das Flashen dauert etwa 10 Sekunden. Danach löscht ihr die `firmware.bin` wieder aus dem
Mainsail-Config-Ordner.

## 4. Kalibrieren

Führt `SOVOL_MENU` aus und arbeitet die Schritte der Reihe nach ab. Siehe [Kalibrierung & Makros](docs/Kalibrierung-Calibration.md).

## Aufgeräumte Makros in Mainsail

Das Skript (oder `python3 ~/Sovol-SV04-Klipper/install/mainsail_macro_groups.py` auf dem Pi) legt fünf
Makro-Panels auf dem Dashboard an und stellt Mainsail auf den Experten-Modus. Dann seht ihr nur
noch diese Panels statt aller internen Makros:

| Panel | Makros | Sichtbar |
|-------|--------|----------|
| 1 SV04 | `SOVOL_MENU`, `LOAD_FILAMENT`, `UNLOAD_FILAMENT` | Bereit, Pause |
| 2 During print | `Z_OFFSET_MENU`, `Z_OFFSET_DOWN/UP` (Babystep), `SAVE_Z_OFFSET`, `M600` (nur beim Drucken) | immer |
| 3 Calibration | Z-Tilt, Bettschrauben, Z-Offset T0/T1, PID, Input Shaper | Bereit |
| 4 IDEX | `T0`, `T1`, Copy-/Mirror-Modus, `CLEAN_NOZZLE` | Bereit |
| 5 Settings | `SET_OFFSET_T1`, `INPUT_SHAPER_SET`, `PREHEAT60/80` | Bereit |

Danach Mainsail neu laden (F5). Eigene Gruppen bleiben erhalten. Unter *Einstellungen → Makros*
könnt ihr die Panels verschieben, umbenennen oder ändern. `--remove` entfernt die SV04-Gruppen wieder.

## Manuelle Einrichtung (ohne Skript)

<details>
<summary>Firmware bauen und Konfiguration von Hand hochladen</summary>

### Firmware bauen

Per SSH: `cd ~/klipper && make menuconfig` und diese Werte wählen:

| Option | Wert |
|--------|------|
| Micro-controller Architecture | STMicroelectronics STM32 |
| Processor model | STM32F103 |
| Bootloader offset | 28KiB bootloader |
| Clock Reference | 8 MHz crystal |
| Communication interface | Serial (on USART1 PA10/PA9) |
| Baud rate for serial port | 115200 |

Diese Werte gelten auch für die GD32-Version. Speichert mit `Q` → `Y`, dann
`make clean && make && cp out/klipper.bin ~/printer_data/config/firmware.bin`.

### Konfiguration hochladen

1. Ladet in Mainsail unter *Maschine* alle Dateien aus `config/Sv04-works-with origin-klipper` hoch.
2. Prüft per SSH mit `ls /dev/serial/by-id/` den seriellen Port und tragt ihn in der `printer.cfg` unter `[mcu] serial:` ein.
3. Aktiviert in der `printer.cfg` den passenden *Z Stepper*-Block für euren Chip (STM32 oder GD32).
4. Klickt auf *Speichern & Neustarten*.

</details>

## Optional: ADXL345 für Input Shaping

Ohne Sensor ist ein Preset aktiv. Wer seinen Drucker vermessen will, schließt einen ADXL345 an
den Pi an, richtet den Pi als zweite MCU ein und aktiviert in der `printer.cfg` die Zeile
`[include adxl345.cfg]`. Siehe [Kalibrierung & Makros](docs/Kalibrierung-Calibration.md#input-shaper).

## Optional: Original-Sovol-Display

Das originale Sovol-Display (DGUS/T5UID1) funktioniert nur mit dem Klipper-Fork
[Bully85/klipper](https://github.com/Bully85/klipper). Antwortet ihr im Skript mit `display`, stellt
es Klipper auf den Fork um, nutzt `config/SV04-with-display` und baut die Firmware mit
Display-Unterstützung. Von Hand:

```sh
cd ~/klipper
git remote set-url origin https://github.com/Bully85/klipper
git fetch origin
git checkout -B master origin/master
sudo systemctl restart klipper
```

In `make menuconfig` zusätzlich *Enable extra low-level configuration options* aktivieren, dann
*Enable DGUS T5UID1 screen* → *USART3 (on PB11/PB10)*. Alternativ flasht ihr die fertige
`Firmware bin/firmware.bin`.

Die Meldung „ungültig“ in Mainsail behebt ihr so:

```sh
sudo nano ~/printer_data/systemd/moonraker.env
```
![moonraker.env1](docs/img/moonraker.env1.JPG)

Fügt `-g` am Ende der Zeile `MOONRAKER_ARGS` an:
![moonraker.env2](docs/img/moonraker.env2.JPG)

Speichert, startet neu, klickt in Mainsail auf *ungültig* und führt einen *Soft Repair* durch.

## Optional: Touchscreen (KlipperScreen)

Das Skript fragt danach und nutzt den offiziellen Installer. Von Hand:
`git clone https://github.com/KlipperScreen/KlipperScreen.git && ./KlipperScreen/scripts/KlipperScreen-install.sh`.
Danach ladet ihr die `KlipperScreen.conf` aus dem Config-Ordner hoch.


# Update

```sh
git -C ~/Sovol-SV04-Klipper pull
~/Sovol-SV04-Klipper/install/sv04-pi-setup.sh --update
```

`--update` erneuert die Makro-Dateien. Passt die Firmware auf dem Drucker nicht zum Klipper auf dem
Pi (Klipper warnt dann mit „MCU 'mcu' has deprecated code … Recompiling and flashing is recommended“),
bietet es an, die passende `firmware.bin` zu bauen. Die flasht ihr wie in Schritt 3. Bei der
`printer.cfg` zeigt es die Änderungen und fragt nach. Euer serieller Port, Chip, die Includes und der Block `#*# SAVE_CONFIG` (Z-Offset, PID) bleiben
erhalten. Die `variables.cfg` wird nicht angefasst, vorher wird eine Sicherung angelegt. Was sich geändert hat,
steht im [CHANGELOG](CHANGELOG.md). Wer ohne Skript aktualisiert, überschreibt diese beiden Dateien nicht.


# Benutzung von SSH

- Öffnet das Windows-Terminal oder die PowerShell (unter Linux/macOS: Terminal).
- Verbindet euch mit `ssh benutzername@hostname` (wie im Raspberry Pi Imager eingestellt) und gebt das Passwort ein.
- Beenden mit Ctrl+D.


# Für Entwickler und KI-Assistenten

Das [Wiki](wiki/index.md) beschreibt Aufbau, Konventionen, Fallstricke und Testmethoden dieses Repos.
