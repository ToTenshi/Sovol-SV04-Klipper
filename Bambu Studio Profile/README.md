# Bambu Studio Profile – Sovol SV04 (Klipper)

_English below._

Getestet mit Bambu Studio 2.7 (Linux/Flatpak). Die Profile sind eigenständige
Benutzer-Presets. Du musst also keinen Fremdhersteller (z. B. Voron) in Bambu
Studio aktivieren.

## Inhalt

| Ordner     | Presets |
|------------|---------|
| `machine`  | `Sovol SV04 Klipper Single T0` (links), `Single T1` (rechts), `Dual`, `Copy`, `Mirror` |
| `process`  | `0.12mm Fine`, `0.16mm Optimal`, `0.20mm Standard`, `0.28mm Draft` (`@SV04`) |
| `filament` | `Generic PLA / PETG / ABS / TPU @SV04` |
| `bed`      | 3D-Modell des Druckbetts |

Der Start-G-Code ruft `START_PRINT` aus `Start_End_Macro.cfg` auf. Die Klipper-Configs
aus dem Ordner `config/` müssen also aktuell sein.

## Installation

**Automatisch (empfohlen):** Bambu Studio schließen, dann:

- Windows: Doppelklick auf `install/install-slicer-profiles-windows.cmd`
- macOS / Linux: im Repo-Ordner `./install/install-slicer-profiles.sh bambu`

Das Skript kopiert die Presets nach `user/default` und in jeden angemeldeten
Benutzerordner (unter Linux auch Flatpak). Außerdem trägt es das 3D-Bettmodell ein.

**Manuell:** In Bambu Studio *Datei → Importieren → Konfigurationen
importieren…* öffnen und alle `.json`-Dateien aus `machine`, `process` und `filament`
auswählen. Alternativ kopierst du die Dateien direkt in die passenden Ordner:

- Windows: `%APPDATA%\BambuStudio\user\default\{machine,process,filament}`
- macOS: `~/Library/Application Support/BambuStudio/user/default/{machine,process,filament}`

Wenn du in Bambu Studio angemeldet bist, nimm statt `default` den Ordner mit deiner Benutzer-ID.

## Verbindung zu Mainsail/Moonraker

Die SV04-Profile sind schon fertig verbunden: Host-Typ **OctoPrint** (Moonraker emuliert die
OctoPrint-API, in MainsailOS ab Werk aktiv), Adresse `sv04.local`, kein API-Key.

- **Mainsail in Bambu Studio:** Der Reiter **Gerät** (Device) zeigt Mainsail direkt in Bambu Studio
  an (Einstellung *Device UI* = `http://sv04.local`). Du kannst dort also den Druck überwachen,
  Babysteps setzen und Makros starten, ohne den Browser zu öffnen.
- **Drucken:** *Platte drucken* lädt den G-Code hoch und startet ihn, *Senden* lädt nur hoch.
- **Andere Adresse** (anderer Hostname oder IP): beim Installieren `--host 192.168.1.50` mitgeben
  (Windows: `-PrinterHost 192.168.1.50`) oder in Bambu Studio neben dem Druckerprofil auf das
  WLAN-Symbol klicken und *Hostname* und *Device UI* ändern.

## Modi

| Modus | Druckbereich | Hinweis |
|-------|--------------|---------|
| Single T0 / T1 | 300 × 300 × 400 mm | nur linker bzw. rechter Kopf |
| Dual | 300 × 300 × 400 mm | Filament 1 = T0 (links), Filament 2 = T1 (rechts) |
| Copy | **150** × 300 mm | Der rechte Kopf druckt dieselbe Teil-Kopie 151 mm weiter rechts |
| Mirror | **150** × 300 mm | Der rechte Kopf druckt gespiegelt |

- **Copy/Mirror:** Der Druckbereich ist auf die linke Betthälfte begrenzt, damit die Köpfe
  nicht kollidieren. Das Bed Mesh misst automatisch beide Kopien (erledigt `START_PRINT`).
- **Dual:** Der Werkzeugwechsel ruft die Klipper-Makros `T0`/`T1` auf (Parken und XY-Offset).
  Der Prime Tower ist standardmäßig aus. Wenn der wartende Kopf tropft, aktivierst du ihn in
  den Prozesseinstellungen (*Andere → Prime Tower*). Bambu Studio hat keine
  Standby-Temperatur, deshalb bleiben beide Düsen auf Drucktemperatur.
- Die Betttemperatur gilt für jeden Plattentyp gleich. Welchen Plattentyp du wählst, ist also egal.

## Profile anpassen / neu erzeugen

Die JSON-Dateien werden von `tools/build_profiles.py` aus den Voron-Profilen erzeugt, die
Bambu Studio mitliefert. Die SV04-Werte stehen übersichtlich oben im Skript.

```sh
python3 tools/build_profiles.py /var/lib/flatpak/app/com.bambulab.BambuStudio/current/active/files/share/BambuStudio/profiles
```

---

# English

Tested with Bambu Studio 2.7. The presets are standalone user presets, so no
third-party vendor has to be enabled.

- **Automatic:** close Bambu Studio, then double-click `install/install-slicer-profiles-windows.cmd`
  (Windows) or run `./install/install-slicer-profiles.sh bambu` (macOS/Linux).
- **Manual:** *File → Import → Import Configs…* and select all `.json` files from
  `machine`, `process` and `filament`.
- **Mainsail inside Bambu Studio:** the presets are already connected (host type OctoPrint, which
  Moonraker emulates, address `sv04.local`, no API key). The **Device** tab shows Mainsail (*Device UI*),
  and *Print plate* uploads and starts the job. For another address, use `--host 192.168.1.50` when
  installing, or change it with the Wi-Fi icon next to the printer.
- **Copy/Mirror** limit the print area to 150 × 300 mm (left half). The bed mesh covers both copies.
- **Dual:** filament 1 = T0 (left), filament 2 = T1 (right). The prime tower is off by default.
- The presets need the current `Start_End_Macro.cfg` (`START_PRINT`) from `config/`.
