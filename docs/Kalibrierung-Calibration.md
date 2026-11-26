# Kalibrierung & Makros / Calibration & macros

_English below._

Alle Makros stehen in `sv04_tools.cfg` und sind in beiden Config-Ordnern enthalten.
Die bequemste Bedienung ist das Menü **`SOVOL_MENU`**. Mainsail (ab v2.9) und Fluidd (ab v1.27)
zeigen es als Dialog mit Buttons an. Tipp: In Mainsail unter *Einstellungen → Makros* eine
Gruppe „SV04“ anlegen und `SOVOL_MENU`, `SAVE_Z_OFFSET`, `LOAD_FILAMENT` und `UNLOAD_FILAMENT`
hinzufügen. Dann liegen sie als Buttons auf dem Dashboard.

## Reihenfolge bei der Ersteinrichtung

1. **`Z_TILT_HOME`**: Homing und Ausrichten der beiden Z-Motoren.
2. **`PROBE_CHECK`** (optional): misst die Bettmitte zehnmal mit dem BLTouch und zeigt, wie stark
   die Werte streuen. Bis 0,025 mm Spannweite ist alles gut. Darüber sitzt der BLTouch oder sein
   Halter locker, oder Stift bzw. Kabel haben ein Problem. Schwankt der Z-Offset von Druck zu Druck,
   ist das der erste Test. Mit `PROBE_CHECK SAMPLES=20 BED_TEMP=60` misst es öfter und bei warmem Bett.
   **`BED_SCREWS_CHECK`** (einmalig): fährt die Sonde nacheinander über die vier Bettschrauben.
   Steht sie nicht über einer Schraube, stimmen die Positionen in `[screws_tilt_adjust]` nicht.
   Dann die **Düse** auf die Schraubenmitte fahren, X/Y notieren und eintragen (Y minus 25 mm,
   weil die Sonde 25 mm hinter der Düse sitzt).
   **`BED_LEVEL_SCREWS`**: Misst die vier Bettschrauben mit dem BLTouch. Mainsail zeigt danach
   an, wie weit jede Schraube gedreht werden muss (z. B. „CW 00:15“ = eine Viertelumdrehung im
   Uhrzeigersinn). So oft wiederholen, bis alle Werte nahe 00:00 liegen.
3. **`Z_OFFSET_CALIBRATE`**: Z-Offset der linken Düse (T0), siehe unten.
4. **`CALIBRATE_Z_T1`**: Höhenunterschied der rechten Düse (T1), siehe unten.
5. **XY-Offset von T1**: Kalibrierwürfel aus `Calibration for x_y offset/` drucken und den Wert
   mit `SET_OFFSET_T1 X=… Y=…` speichern. Der alte Befehl `XY_offset_dual` funktioniert weiterhin.
6. Optional **`PID_TUNE_BED`** und **`PID_TUNE_HOTEND TOOL=0`** bzw. **`TOOL=1`**.
7. Optional **Input Shaper** messen (mit Sensor oder Testdruck), siehe unten. Ohne Messung ist ein Preset aktiv.

Nach Schritt 3 und 6 erscheint ein Dialog mit **SAVE_CONFIG**. Damit werden die Werte in
`printer.cfg` gespeichert und Klipper startet neu.

## Z-Offset

| Was | Wo gespeichert | Einstellen |
|-----|----------------|------------|
| Z-Offset T0 | `printer.cfg` (`[bltouch] z_offset`, SAVE_CONFIG-Block) | `Z_OFFSET_CALIBRATE` oder Babystep + `SAVE_Z_OFFSET` |
| Z-Offset T1 (relativ zu T0) | `variables.cfg` (`dual_z_offset`) | `CALIBRATE_Z_T1` oder `SET_OFFSET_T1 Z=…` |
| Babystep | bis zum Speichern oder Neustart von Klipper | Mainsail-Buttons „Z-Offset“ (±0.01 / ±0.05) |

**`Z_OFFSET_CALIBRATE`** heizt Bett (60 °C) und Düse (150 °C) auf, homt, richtet Z aus und misst
die Bettmitte mit dem BLTouch. Danach öffnet Mainsail automatisch den Dialog *Manual Probe*:
Ein Blatt Papier unter die Düse legen und mit den Buttons absenken, bis das Papier leicht
schleift. Dann **ACCEPT** drücken und im folgenden Dialog **SAVE_CONFIG** wählen. Andere
Temperaturen gehen mit `Z_OFFSET_CALIBRATE BED_TEMP=80 NOZZLE_TEMP=160`.

**`CALIBRATE_Z_T1`** funktioniert genauso mit der rechten Düse. Danach erscheint ein Dialog mit dem
gemessenen Wert und den Buttons **Save** und **Discard**. Bei mehr als 0,3 mm erscheint ein Hinweis:
Im COPY/MIRROR-Modus kann der Höhenunterschied nicht per Software ausgeglichen werden, dann
sollte der Hotend mechanisch nachjustiert werden.

**Feinjustieren während des Drucks.** Beide Wege führen zum selben Ergebnis:

- **Dialog:** **`Z_OFFSET_MENU`** (Panel „2 During print“ oder in `SOVOL_MENU`) öffnet einen Dialog mit
  −0.05 / −0.01 / +0.01 / +0.05, dem aktuellen Wert und einem Speichern-Button. Einzelne Schritte
  gehen auch mit `Z_OFFSET_DOWN STEP=0.01` / `Z_OFFSET_UP STEP=0.01`. Minus bedeutet näher ans Bett.
  Insgesamt sind höchstens ±1 mm möglich.
- **Mainsail-Standard:** Mit den Babystep-Buttons im Panel „Z-Offset“ nachstellen, bis die erste
  Schicht passt, dann den **Speichern-Button** im Panel drücken und im Dialog **SAVE_CONFIG** wählen.
- **Makro:** Babystep wie oben, dann **`SAVE_Z_OFFSET`** (Panel „2 During print“).

Beide rechnen einen aktiven T1-Offset heraus, das Speichern ist also auch mit T1 korrekt.
SAVE_CONFIG startet Klipper neu und geht deshalb nicht mitten im Druck. Am Druckende erscheint
automatisch der Dialog. Ist noch ein ungespeicherter Babystep aktiv, fragt der Dialog, ob er
gespeichert werden soll.

**Was gilt, solange nichts gespeichert ist?**

- Ein gemessener, aber noch nicht gespeicherter Z-Offset (aus `Z_OFFSET_CALIBRATE` oder dem
  Speichern-Button) wird beim **nächsten Druck trotzdem schon verwendet**. `START_PRINT` setzt dafür
  automatisch den passenden Babystep. Nach SAVE_CONFIG gilt derselbe Wert dauerhaft.
- Ein Babystep bleibt bis zum Speichern oder bis zum Neustart von Klipper aktiv, auch über mehrere
  Drucke. So verhält sich auch Klipper/Mainsail ohne SV04-Makros. Der Button *Zurücksetzen* im
  Mainsail-Panel löscht ihn.
- `CALIBRATE_Z_T1` misst relativ zu T0. Ist der neue T0-Wert noch nicht gespeichert, verlangt es
  zuerst SAVE_CONFIG.
- Bei jedem Werkzeugwechsel wird nur der T1-Anteil verrechnet. Ein Babystep gilt für beide Düsen.
- `START_PRINT` homt Z nach dem Z-Tilt erneut, so wie die Kalibrierung. Der Nullpunkt ist beim
  Messen und beim Drucken derselbe.

## Input Shaper

Input Shaping unterdrückt Schwingungen (Ringing/Ghosting) und erlaubt dadurch höhere Beschleunigungen.

**Ohne Sensor (Standard):** Ein vorsichtiges Preset ist automatisch aktiv: X EI 40 Hz (beide
Schlitten), Y EI 30 Hz (Bett). Damit ist `max_accel` von 1000 auf **1500 mm/s²** angehoben.
EI verzeiht eine geschätzte Frequenz deutlich besser als MZV. Die Glättung liegt bei 1500 mm/s²
auf Y bei etwa 0,13 mm. Wer feinste Details braucht, setzt `max_accel` in der `printer.cfg`
wieder auf 1000–1200. Die Slicer-Profile (Cura, Bambu Studio) sind auf 1500 mm/s² angepasst,
PrusaSlicer nutzt direkt Klippers `max_accel`.

**Eigene Werte ohne Sensor:** Den Ringing-Tower aus der
[Klipper-Doku](https://www.klipper3d.org/Resonance_Compensation.html) drucken, die Frequenzen
ermitteln und so speichern:

```
INPUT_SHAPER_SET AXIS=X TOOL=0 TYPE=mzv FREQ=45.0
INPUT_SHAPER_SET AXIS=X TOOL=1 TYPE=mzv FREQ=43.0
INPUT_SHAPER_SET AXIS=Y TYPE=mzv FREQ=32.0
```

`FREQ=0` setzt eine Achse zurück aufs Preset. `INPUT_SHAPER_STATUS` zeigt, was gerade gilt.

**Mit Sensor (ADXL345):**

1. Den ADXL345 an die SPI-Pins des Raspberry Pi anschließen und den Pi als zweite MCU einrichten
   ([Anleitung](https://www.klipper3d.org/RPi_microcontroller.html),
   [Verkabelung](https://www.klipper3d.org/Measuring_Resonances.html)). Einmalig per SSH
   `~/klippy-env/bin/pip install numpy` ausführen.
2. In der `printer.cfg` die Zeile `[include adxl345.cfg]` aktivieren und *Speichern & Neustarten*.
3. Messen, jeweils mit dem Sensor an der passenden Stelle (in `SOVOL_MENU` gibt es dafür Buttons):
   - `SHAPER_CALIBRATE_SV04 AXIS=X TOOL=0`: Sensor am linken Druckkopf
   - `SHAPER_CALIBRATE_SV04 AXIS=X TOOL=1`: Sensor am rechten Druckkopf
   - `SHAPER_CALIBRATE_SV04 AXIS=Y`: Sensor auf dem Bett
4. Die Werte werden in `variables.cfg` gespeichert und sofort benutzt. Danach Klipper einmal
   neu starten (Button **RESTART** im Dialog).

Warum nicht über SAVE_CONFIG: Original-Klipper startet mit `[dual_carriage]` nicht, wenn
Shaper-Werte in `[input_shaper]` stehen. Deshalb setzt die Config die Werte pro Schlitten zur
Laufzeit, beim Start, bei jedem Werkzeugwechsel und in Copy/Mirror. Solange eine Messung auf
SAVE_CONFIG wartet, blockiert `SAVE_CONFIG` mit einem Hinweis. Ein RESTART löst das auf.

## Filament

- `LOAD_FILAMENT TOOL=0` bzw. `TOOL=1`: heizt auf (Standard 220 °C, in der Pause die
  Drucktemperatur), zieht 50 mm ein und spült 20 mm.
- `UNLOAD_FILAMENT TOOL=0` bzw. `TOOL=1`: formt die Spitze und zieht das Filament 75 mm zurück.
- Optional `TEMP=240` und `LENGTH=…` (höchstens 95 mm). Ohne `TOOL` gilt die aktive Düse.
- Filamentwechsel während des Drucks: `M600` (pausieren, parken, entladen), dann
  `LOAD_FILAMENT` und `RESUME`. Im COPY/MIRROR-Modus laden und entladen beide Düsen gemeinsam.

## Weitere Änderungen

- `min_extrude_temp` ist jetzt 170 °C statt 1 °C. So kann nicht mehr versehentlich kalt
  extrudiert werden.
- COPY/MIRROR: `START_PRINT` erweitert den Bed-Mesh-Bereich automatisch auf die zweite Kopie.
  Das funktioniert mit jedem Slicer. Die Slicer-Profile begrenzen den Druckbereich auf 150 mm.
- PAUSE im MIRROR/COPY-Modus parkt jetzt korrekt. Vorher konnte das zu „Move out of range“ führen.
- Beim Update `variables.cfg` **nicht** überschreiben, sonst gehen die gespeicherten T1-Offsets
  verloren. Falls `dual_z_offset` fehlt, gilt automatisch 0.

---

# English

All macros live in `sv04_tools.cfg`. Run **`SOVOL_MENU`** for a button menu (Mainsail ≥ 2.9,
Fluidd ≥ 1.27).

First-time order: `Z_TILT_HOME` → `BED_LEVEL_SCREWS` → `Z_OFFSET_CALIBRATE` →
`CALIBRATE_Z_T1` → XY offset (`SET_OFFSET_T1 X=… Y=…`) → optional `PID_TUNE_BED` and
`PID_TUNE_HOTEND TOOL=0|1`.

- **`Z_OFFSET_CALIBRATE`**: heats, homes, levels and opens Mainsail's *Manual Probe* dialog.
  Do the paper test, press **ACCEPT**, then **SAVE_CONFIG**.
- **`CALIBRATE_Z_T1`**: the same paper test with T1. The result is stored as `dual_z_offset` in
  `variables.cfg` and applied on every tool change and in single T1 mode.
- **Change the Z offset during the print:** `Z_OFFSET_MENU` (dialog with ±0.01/±0.05 and Save) or
  `Z_OFFSET_DOWN` / `Z_OFFSET_UP STEP=…` (minus = closer to the bed, at most ±1 mm). Mainsail's own
  babystep buttons do the same.
- **`SAVE_Z_OFFSET`** and **Mainsail's Z offset save button** do the same thing: they store the
  babystep in the probe z_offset, without the T1 tool offset. SAVE_CONFIG is offered when the print
  finishes. A measured but unsaved z_offset is already used by the next print (`START_PRINT` sets
  the matching babystep). Babysteps stay active until they are saved or Klipper restarts.
- **`LOAD_FILAMENT` / `UNLOAD_FILAMENT`** `TOOL=0|1 TEMP=… LENGTH=…`
- **Input shaper:** a preset (X EI 40 Hz, Y EI 30 Hz) is active without a sensor, so `max_accel` is 1500.
  Own values: `INPUT_SHAPER_SET AXIS=X TOOL=0|1` or `AXIS=Y TYPE=… FREQ=…` (ringing tower).
  With an ADXL345: `[include adxl345.cfg]`, then `SHAPER_CALIBRATE_SV04 AXIS=X TOOL=0|1` / `AXIS=Y`.
  Values are stored in `variables.cfg` (never in `[input_shaper]`, which breaks original Klipper with
  dual_carriage). Restart once after measuring. `INPUT_SHAPER_STATUS` shows the active values.
- `min_extrude_temp` is now 170 °C. COPY/MIRROR bed meshes cover both copies, and PAUSE parks
  correctly in COPY/MIRROR.
- Don't overwrite `variables.cfg` when updating, because it holds your T1 offsets.
