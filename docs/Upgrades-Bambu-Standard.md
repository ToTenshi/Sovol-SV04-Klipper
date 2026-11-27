# Upgrades: SV04 auf „Bambu-Lab-Niveau“ / Upgrades towards Bambu Lab level

_English summary below._

Diese Übersicht zeigt, wie der SV04 näher an den Komfort und die Qualität eines Bambu-Lab-Druckers
kommt. Grundregeln:

- **Die Basis muss passen:** 24-V-System mit 500-W-Netzteil, Bett 300 × 300 mm
  (Federstahlplatte 310 × 320 mm), IDEX mit zwei Titan-ähnlichen Direktextrudern (3:1), Hotend bis
  260 °C, STM32F103-Board mit 7 Treibern im Step/Dir-Modus (keine TMC-UART-Leitung). Quellen unten.
- **Bambu-Kompatibilität ehrlich bewertet:** Die meisten Bambu-Teile sind proprietär und passen
  nur in Bambu-Drucker. Wo ein Teil **zwischen SV04 und einem Bambu-Drucker tauschbar** ist, steht
  das in der Spalte „Bambu-kompatibel“. So kann man zum Beispiel denselben Ersatzteilvorrat nutzen.
- **Was keine Hardware braucht, ist schon erledigt** (Teil A). Danach folgen die Umbauten nach
  Aufwand sortiert.

Legende: ✅ funktioniert / im Repo vorbereitet · 🔧 Halter selbst drucken bzw. Umbau (machbar, siehe
„Eigene Halter drucken“) · ❌ passt nicht

## A. Bereits umgesetzt (nur Software, dieses Repo)

| Bambu-Funktion | Umsetzung beim SV04 | Vorteil |
|----------------|---------------------|---------|
| Ein-Klick-Kalibrierung | `SOVOL_MENU`: Z-Tilt, Bettschrauben, Z-Offset T0/T1, PID, Sondentest | geführte Kalibrierung per Dialog, kein Konsolenwissen nötig |
| Vibrationskompensation | Input-Shaper-Preset ohne Sensor, optional Messung mit ADXL345 | 1500 statt 1000 mm/s², weniger Ringing |
| Adaptives Bed Mesh | Mesh nur über die Druckfläche, auch für Copy/Mirror | schnellerer Druckstart, bessere erste Schicht |
| Slicer-Integration | Bambu-Studio-Profile, Mainsail im Reiter „Gerät“, Hochladen per Klick | gleicher Arbeitsablauf wie mit einem Bambu-Drucker |
| Filamentprofile | Generic PLA/PETG/ABS/TPU @SV04 | Bambu-Filamente mit passenden Temperaturen nutzbar |
| Filamentwechsel | `LOAD_FILAMENT`, `UNLOAD_FILAMENT`, `M600` | Laden und Entladen per Knopfdruck |

## B. Hardware-Upgrades

| # | Upgrade | Bambu-Pendant | Teile | Bambu-kompatibel | Passt zur SV04-Basis? | Aufwand | Vorteile |
|---|---------|---------------|-------|------------------|-----------------------|---------|----------|
| 1 | **Kamera + Fehlererkennung** | X1-Kamera, Spaghetti-Erkennung | USB-Webcam oder Pi-Kamera, Software Obico (Klipper-Plugin) | – | ✅ crowsnest ist in MainsailOS bereits installiert | gering | Druck aus der Ferne beobachten, Zeitraffer, Abbruch bei „Spaghetti“ |
| 2 | **PEI-Federstahlplatte, doppelseitig (glatt + texturiert)** | Bambu Textured PEI Plate | PEI-Platte **310 × 320 mm** für den SV04 | ❌ Bambu-Platten (257 × 257 mm) sind zu klein, gleiche Oberfläche aber in SV04-Größe erhältlich | ✅ Magnetbasis vorhanden | gering | gleiche Haftung wie beim Bambu, Teile springen beim Biegen ab |
| 3 | **Gehärtete Düsen** | X1C/P1 gehärtete Stahldüse | gehärtete Düsen im **Format der SV04-Düse** (Gewinde und Länge an der Originaldüse prüfen) | ❌ Bambu-Düsen passen nur ins Bambu-Hotend | ✅ | gering | CF/GF-Filamente (PLA-CF, PA-CF) ohne Verschleiß |
| 4 | **ADXL345 über USB** statt SPI-Verkabelung | eingebauter Beschleunigungssensor | z. B. RP2040-ADXL345-Modul mit USB | – | ✅ `adxl345.cfg` vorhanden (aktuell für SPI am Pi, für USB `[mcu adxl]` + `cs_pin` anpassen) | gering | Input Shaper je Schlitten messen statt Preset → höhere Beschleunigung bei gleicher Qualität |
| 5 | **Bambu-X1/P1-Hotend** mit eigenem Halter | Bambu-Hotend (Schnellwechsel) | Bambu Hotend X1/P1 (Düse + Heizung 24 V/48 W + Thermistor NTC 100K) | ✅ **Düsen, Heizung und Thermistor tauschbar mit Bambu X1/P1**. Nicht mit den Schnellwechsel-Hotends von A1 und H2/P2S, die laut Bambu nicht zu X1/P1 passen | 🔧 kein fertiger SV04-Halter bekannt. Es gibt Vorlagen für SV08, Neptune 4 und Ender 3. 24 V/48 W passt elektrisch, Stecker müssen umgecrimpt werden | hoch | bis 300 °C, deutlich höherer Durchfluss als das Original (≈260 °C), Düsenwechsel in Sekunden, gemeinsamer Ersatzteilvorrat mit Bambu |
| 6 | **Bi-Metall-Heatbreak** (kleine Alternative zu 5) | – | Bi-Metall-Heatbreaks für SV04/SV01 Pro | – | ✅ Sovol bietet sie für den SV04 an | gering | höhere Temperaturen, weniger Verstopfungen bei PETG/ABS |
| 7 | **Wirbelstrom-Sonde** (BTT Eddy) statt BLTouch | Lidar/Kraftsensor für Bett-Scan | BTT Eddy (USB) | – | 🔧 Halter am T0-Schlitten nötig, Klipper unterstützt sie (nur Original-Klipper) | mittel | Bed Mesh in Sekunden statt Minuten, kein mechanischer Stift. Z-Offset weiter einmal per Papiertest |
| 8 | **Wägezelle** für automatischen Z-Offset | A1 / P2S (Kraftsensor misst den Düsenkontakt) | Wägezelle(n) + ADC (HX711/HX717/ADS1220), ggf. Zusatz-MCU (RP2040) | – | 🔧 aufwendiger Umbau, eine Zelle pro Schlitten oder Bett-Wägezellen. Klipper hat `[load_cell_probe]` seit 2025 (nur Original-Klipper) | hoch | **Z-Offset für T0 und T1 vollautomatisch**, kein Papiertest mehr ([Details](../wiki/hardware-ideas.md)) |
| 9 | **Dual-Gear-Extruder** (Orbiter/Sherpa Mini) | Bambu-Extruder (Doppelantrieb) | Orbiter 2.0 oder Sherpa Mini, je Schlitten | ❌ Bambu-Extrudereinheit passt nicht | 🔧 kein fertiger SV04-Halter gefunden, eigener Halter nötig. `rotation_distance` anpassen | hoch | gleichmäßigerer Vorschub, bessere TPU-Verarbeitung, leichterer Druckkopf |
| 10 | **Neues Mainboard mit TMC2209 (UART)** | leise Treiber, Sensorüberwachung | z. B. 32-Bit-Board mit ≥ 7 Treibern (für IDEX: X, X2, Y, Z, Z1, E0, E1) | – | 🔧 Board-Tausch + neue `printer.cfg` (Pins), 24 V passt | hoch | leiser, Stromstärke per Software, Sensorless-Homing für X/Y möglich, Basis für LEDs, Wägezelle usw. |
| 11 | **Einhausung** + Abluft/Kammersensor | P1S/X1C geschlossen | Einhausung für ≈ 600 × 700 mm Grundfläche (Bettschlitten braucht Platz in Y), Temperatursensor, Lüfter | – | ✅ Klipper: `[temperature_sensor]`, `[fan_generic]` | mittel | ABS/ASA ohne Warping, leiser, weniger Staub |
| 12 | **LED-Beleuchtung** | Kammerlicht | 24-V-LED-Streifen + MOSFET-Modul an einem freien Pin oder am Pi (GPIO) | – | ✅ `[output_pin]`/`[led]` | gering | bessere Kamerabilder, Licht per Mainsail schaltbar |
| 13 | **AMS** (Mehrfarben-Wechsler) | Bambu AMS / AMS lite | – | ❌ nur für Bambu-Drucker | ❌ | – | Alternative beim SV04: Dual-Modus mit zwei Köpfen (kein Spülturm-Abfall) |

**Was zwischen SV04 und Bambu-Drucker tauschbar wird:** Mit Upgrade 5 teilen sich beide Drucker
Düsen, Heizpatrone und Thermistor, aber nur mit einem **Bambu X1/P1**. Die Hotends von **P2S/H2**
(Schnellwechsel mit Verriegelung) und A1 sind ein anderes System. Bambu führt X1/P1 dafür als „Not
Supported“. Ein P2S teilt also keine Hotend-Teile mit dem SV04. Filamente, Bambu-Studio-Profile und 4-mm-PTFE-Schläuche lassen sich ohnehin gemeinsam
nutzen. Druckplatten, Düsen des Original-Hotends, Extruder und AMS sind nicht kompatibel.

## Empfohlene Reihenfolge

1. **Kamera (1) und PEI-Platte (2):** wenig Aufwand, sofort spürbarer Komfort.
2. **ADXL über USB (4):** gemessene Input-Shaper-Werte statt Preset.
3. **Gehärtete Düsen (3) oder Bi-Metall-Heatbreak (6)**, je nach Filament.
4. **Größere Umbauten** (5, 7, 8, 9, 10) am besten **gemeinsam planen**. Ein neues Mainboard (10)
   bringt die freien Anschlüsse, die Wägezelle (8), Eddy (7) oder LEDs (12) brauchen. Ein neuer
   Druckkopf-Halter kann Bambu-Hotend (5), Extruder (9) und Sonde in einem Teil aufnehmen.
   Alle setzen das **Original-Klipper** voraus.

## Eigene Halter drucken

Die 🔧-Upgrades scheitern nicht an fehlenden Teilen. Halter, Lüfterkanäle und Gehäuse lassen sich
selbst konstruieren und drucken. Worauf es am SV04 ankommt:

- **Material nach Temperatur wählen:** Alles in Hotend-Nähe (Hotend-Halter, Lüfterkanal) aus
  **ASA/ABS**, besser **PC** oder **PA-CF**. PLA und PETG werden dort weich. Halter weiter weg
  (Sonde, Kabelhalter, Elektronikgehäuse) gehen in PETG.
- **Gewindeeinsätze statt Schrauben ins Plastik:** Gewindeeinsätze aus Messing (M3) halten dauerhaft
  und lassen sich mehrfach lösen. Wände um die Einsätze mit mindestens 4 Perimetern drucken.
- **Maße am Original abnehmen:** Bohrbild am Schlitten, Abstand Düsenspitze zu Schlitten und Höhe
  der Sonde. Der BLTouch muss im eingefahrenen Zustand **2–4 mm über der Düsenspitze** liegen.
  Liegt die neue Düse tiefer oder höher, ändert sich der Z-Offset (danach `Z_OFFSET_CALIBRATE`).
- **IDEX-Kollision:** Beide Köpfe müssen in Mirror/Copy in der Bettmitte aneinander vorbeikommen.
  Neue Teile also **nicht breiter** als die originalen Köpfe in X bauen, Lüfter nach vorne oder
  hinten statt zur Seite. Die Parkpositionen links (X −62) und rechts (X 360) dürfen keinen Rahmenteil
  berühren.
- **Sondenversatz eintragen:** Sitzt die Sonde an anderer Stelle, ändern sich `x_offset/y_offset` in
  `[bltouch]`. Damit ändern sich auch `mesh_min/mesh_max` sowie die Koordinaten für Z-Tilt und
  Bettschrauben (alles in `printer.cfg`, siehe [Wiki Leveling](../wiki/leveling.md)).
- **Gewicht klein halten:** Jede zusätzliche Masse am Kopf senkt die Resonanzfrequenz. Danach den Input
  Shaper neu messen oder das Preset anpassen.
- **CAD-Vorlagen nutzen:** Die Bambu-Hotend-Halter für SV08, Neptune 4 und Ender 3 (Quellen unten)
  enthalten die Bambu-Hotend-Geometrie und eignen sich als Ausgangspunkt für einen SV04-Halter.

## Vor jedem Umbau prüfen

- **Kollision der Köpfe:** Beim IDEX müssen beide Köpfe in der Mitte aneinander vorbeipassen. Breitere
  Halter oder Lüfterkanäle verkleinern den Druckbereich oder stoßen zusammen. Ein bekannter
  SV01-Pro-Umbau passt aus genau diesem Grund nicht auf den SV04.
- **Gewicht:** Schwerere Druckköpfe senken die Resonanzfrequenz. Danach Input Shaper neu messen.
- **Firmware/Config:** Neue Thermistoren brauchen den passenden `sensor_type`, neue Heizungen ein
  `PID_TUNE_HOTEND`, ein neues Hotend einen neuen Z-Offset (`Z_OFFSET_CALIBRATE`, `CALIBRATE_Z_T1`).

---

# English summary

Software features (calibration wizards, input shaper preset, adaptive mesh, Bambu Studio
integration with Mainsail in the Device tab, filament macros) are already part of this repo.
Hardware upgrades, from easy to involved:

| # | Upgrade | Shared with Bambu? | Fits the SV04 base? | Benefit |
|---|---------|--------------------|---------------------|---------|
| 1 | Camera + Obico failure detection | – | ✅ crowsnest is in MainsailOS | remote monitoring, timelapse, spaghetti detection |
| 2 | Double-sided PEI spring steel sheet 310 × 320 mm | ❌ Bambu plates are 257 mm | ✅ | Bambu-like adhesion and release |
| 3 | Hardened nozzles (SV04 format) | ❌ | ✅ | CF/GF filaments |
| 4 | USB ADXL345 (RP2040) | – | ✅ adapt `adxl345.cfg` | measured input shaper per carriage |
| 5 | Bambu X1/P1 hotend with a custom mount | ✅ nozzles, heater, thermistor with X1/P1 only (P2S/H2 and A1 quick-swap hotends are a different system) | 🔧 no SV04 mount yet, 24 V/48 W fits | up to 300 °C, high flow, fast nozzle swaps, shared spares |
| 6 | Bi-metal heatbreak | – | ✅ sold for SV04 | higher temperatures, fewer clogs |
| 7 | BTT Eddy probe | – | 🔧 mount needed, original Klipper | mesh in seconds |
| 8 | Load cell (automatic Z offset) | – | 🔧 major retrofit, `[load_cell_probe]` | automatic Z offset for both nozzles |
| 9 | Dual-gear extruder (Orbiter/Sherpa Mini) | ❌ | 🔧 mount needed | smoother extrusion, TPU, lighter head |
| 10 | New mainboard with TMC2209 UART (≥ 7 drivers) | – | 🔧 new `printer.cfg` | quieter, current control, free pins for upgrades |
| 11 | Enclosure + chamber sensor/exhaust | – | ✅ | ABS/ASA, less noise |
| 12 | LED lighting | – | ✅ | better camera image |
| 13 | AMS | ❌ Bambu only | ❌ | use dual mode instead |

Printing your own mounts makes the 🔧 upgrades feasible: use ASA/ABS/PC/PA-CF near the hotend
(PETG further away), brass heat-set inserts, keep the parts no wider in X than the stock heads
(IDEX collision in mirror/copy), keep the BLTouch 2–4 mm above the nozzle tip, and update the probe
offset and mesh/Z-tilt coordinates in `printer.cfg` if the probe moves.

Check head collisions (IDEX), extra weight (re-measure the input shaper) and Klipper settings
(thermistor type, PID, Z offset) after every change.

## Quellen / Sources

- SV04-Daten: [SimplyPrint](https://simplyprint.io/compatibility/sovol-sv04),
  [3D Print Beginner](https://3dprintbeginner.com/sovol-sv04-review-large-format-idex-3d-printer/),
  [3DSourced](https://www.3dsourced.com/3d-printer-reviews/sovol-sv04/)
- SV04-Hotend: [Sovol-Forum, Hotend tauschen](https://forum.sovol3d.com/t/replacing-sovol-sv04-hot-end/5133),
  [Bi-Metall-Heatbreak für SV04](https://www.amazon.com/Sovol-Bi-Metal-HeatBreak-Upgraded-Titanium/dp/B0BJDPS741),
  [Volcano-Umbau SV01 Pro (Kollision beim SV04)](https://www.printables.com/model/223015-sovol-sv01-pro-all-metal-heatbreak-volcano-dual-50)
- Bambu-Hotend an Fremddruckern: [SV08-Adapter](https://www.printables.com/model/1027739-bambu-hotend-adaptor-for-sovol-sv08-opimised-for-s),
  [Neptune-4-Kit](https://www.printables.com/model/758185-bambu-lab-hotend-kit-for-elegoo-neptune-4),
  [Ender-3-Halter](https://www.printables.com/model/1049936-siforo-v2-ender-3-bambu-hotend-mount),
  [Bambu Heizung & Thermistor P1](https://us.store.bambulab.com/products/ceramic-heater-thermistor-p1p),
  [Bambu High Flow Hotend H2/P2S (X1/P1 „Not Supported“)](https://us.store.bambulab.com/products/bambu-high-flow-hotend-h2-p2s)
- Bambu-Druckplatten (257 × 257 mm): [Kompatibilität](https://replacementhq.co.uk/3d-printing/parts/bambu-textured-pei-plate/)
- Dual-Gear-Extruder: [Vergleich BMG/Orbiter/Sherpa](https://blog.uavmodel.com/dual-gear-extruder-upgrade-bmg-clone-vs-orbiter-vs-sherpa-mini-torque-weight-and-print-quality-2026-guide/)
