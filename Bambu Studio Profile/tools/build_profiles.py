#!/usr/bin/env python3
"""Generate the Sovol SV04 (Klipper) user presets for Bambu Studio.

The presets are written as *standalone* user presets (``"inherits": ""``) so
they work without enabling any third-party vendor in Bambu Studio.  To get a
complete, valid key set, the generator resolves the Voron profile chain that
ships with Bambu Studio (Klipper based, 300x300 bed) and applies the SV04
specific overrides defined below.

Usage:
    python3 build_profiles.py <path-to-BambuStudio-resources/profiles>

Example (Flatpak):
    python3 build_profiles.py \
      /var/lib/flatpak/app/com.bambulab.BambuStudio/current/active/files/share/BambuStudio/profiles
"""
import json
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent
VERSION = "2.0.0.0"

# ---------------------------------------------------------------- helpers ----

META_KEYS = {"type", "name", "from", "inherits", "instantiation", "setting_id",
             "filament_id", "base_id", "compatible_printers", "compatible_prints",
             "compatible_printers_condition", "compatible_prints_condition"}


def resolve(vendor_dir: Path, kind: str, name: str) -> dict:
    """Load a preset and merge its whole 'inherits' chain (parent first)."""
    folder = vendor_dir / kind
    data = json.loads((folder / f"{name}.json").read_text())
    parent = data.get("inherits")
    merged = resolve(vendor_dir, kind, parent) if parent else {}
    merged.update(data)
    return merged


def finish(cfg: dict, kind: str, name: str, settings_id_key: str) -> dict:
    cfg = {k: v for k, v in cfg.items() if k not in META_KEYS}
    cfg.update({
        "type": kind,
        "name": name,
        "from": "User",
        "inherits": "",
        "version": VERSION,
        settings_id_key: name if kind != "filament" else [name],
    })
    return dict(sorted(cfg.items()))


def write(kind_dir: str, name: str, cfg: dict) -> None:
    path = OUT / kind_dir / f"{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cfg, indent=4, ensure_ascii=False) + "\n")
    print("wrote", path.relative_to(OUT))


# --------------------------------------------------------------- machines ----

AREA = ("AREA_START={first_layer_print_min[0]},{first_layer_print_min[1]} "
        "AREA_END={first_layer_print_max[0]},{first_layer_print_max[1]}")
# COPY/MIRROR: START_PRINT extends the mesh area to the second copy itself.

BED = "BED_TEMP={bed_temperature_initial_layer_single}"
T0 = "{nozzle_temperature_initial_layer[0]}"
T1 = "{nozzle_temperature_initial_layer[1]}"

# M190 S0 / M109 S0 stop the slicer from inserting its own heat-up commands;
# START_PRINT (Start_End_Macro.cfg) does all heating, homing and meshing.
HEAD = "M190 S0\nM109 S0\n"

MACHINES = {
    "Sovol SV04 Klipper Single T0": dict(
        width=300, filaments=1, colours=["#1E90FF"],
        start=HEAD + f"START_PRINT EXTRUDER=0 EXTRUDERS=1 EXTRUDER_TEMP={T0} EXTRUDER1_TEMP=0 {BED} {AREA}"),
    "Sovol SV04 Klipper Single T1": dict(
        width=300, filaments=1, colours=["#FF4500"],
        start=HEAD + f"START_PRINT EXTRUDER=1 EXTRUDERS=1 EXTRUDER_TEMP={T0} EXTRUDER1_TEMP=0 {BED} {AREA}"),
    "Sovol SV04 Klipper Dual": dict(
        width=300, filaments=2, colours=["#1E90FF"],
        start=HEAD + "G28 X\nSET_DUAL_CARRIAGE CARRIAGE=0 MODE=PRIMARY\n"
              f"START_PRINT EXTRUDER={{initial_extruder}} EXTRUDERS=2 EXTRUDER_TEMP={T0} EXTRUDER1_TEMP={T1} {BED} {AREA}"),
    "Sovol SV04 Klipper Copy": dict(
        width=150, filaments=1, colours=["#2E8B57"],
        start=HEAD + "G28 X\nSET_DUAL_CARRIAGE CARRIAGE=1 MODE=COPY\n"
              f"START_PRINT EXTRUDER=0 EXTRUDERS=2 EXTRUDER_TEMP={T0} EXTRUDER1_TEMP={T0} {BED} {AREA}"),
    "Sovol SV04 Klipper Mirror": dict(
        width=150, filaments=1, colours=["#9370DB"],
        start=HEAD + "G28 X\nSET_DUAL_CARRIAGE CARRIAGE=1 MODE=MIRROR\n"
              f"START_PRINT EXTRUDER=0 EXTRUDERS=2 EXTRUDER_TEMP={T0} EXTRUDER1_TEMP={T0} {BED} {AREA}"),
}
PRINTER_NAMES = list(MACHINES)


def two(v):
    """Machine limits are [normal, silent]."""
    return [str(v), str(v)]


def build_machines(vendor: Path) -> None:
    base = resolve(vendor, "machine", "Voron 2.4 300 0.4 nozzle")
    for name, m in MACHINES.items():
        cfg = dict(base)
        w = m["width"]
        cfg.update({
            "printer_model": "",
            "printer_variant": "0.4",
            "nozzle_diameter": ["0.4"],
            "nozzle_type": "brass",
            "gcode_flavor": "klipper",
            "printable_area": ["0x0", f"{w}x0", f"{w}x300", "0x300"],
            "printable_height": "400",
            "bed_exclude_area": [],
            "extruder_colour": m["colours"],
            "extruder_offset": ["0x0"],
            "single_extruder_multi_material": "1",
            "use_relative_e_distances": "1",
            # machine limits (only used for time estimation with Klipper)
            "machine_max_speed_x": two(300), "machine_max_speed_y": two(300),
            "machine_max_speed_z": two(20), "machine_max_speed_e": two(120),
            "machine_max_acceleration_x": two(1000), "machine_max_acceleration_y": two(1000),
            "machine_max_acceleration_z": two(50), "machine_max_acceleration_e": two(1500),
            "machine_max_acceleration_extruding": two(1000),
            "machine_max_acceleration_retracting": two(1000),
            "machine_max_acceleration_travel": two(1000),
            "machine_max_jerk_x": two(8), "machine_max_jerk_y": two(8),
            "machine_max_jerk_z": two(0.4), "machine_max_jerk_e": two(2.5),
            "min_layer_height": ["0.08"], "max_layer_height": ["0.32"],
            # retraction (same values as the tested PrusaSlicer profile)
            "retraction_length": ["2"], "retraction_speed": ["30"],
            "deretraction_speed": ["0"], "retraction_minimum_travel": ["2"],
            "retract_length_toolchange": ["10"] if m["filaments"] == 2 else ["2"],
            "retract_when_changing_layer": ["1"], "retract_before_wipe": ["0%"],
            "wipe": ["0"], "z_hop": ["0.4"], "retract_lift_below": ["399"],
            # g-code
            "machine_start_gcode": m["start"],
            "machine_end_gcode": "END_PRINT",
            "machine_pause_gcode": "PAUSE",
            "change_filament_gcode": "T[next_extruder]" if m["filaments"] == 2 else "M600",
            "layer_change_gcode": ";AFTER_LAYER_CHANGE\n;[layer_z]",
            "before_layer_change_gcode": ";BEFORE_LAYER_CHANGE\n;[layer_z]\nG92 E0\n",
            "default_print_profile": "0.20mm Standard @SV04",
            "default_filament_profile": ["Generic PLA @SV04"],
            "scan_first_layer": "0",
            "auxiliary_fan": "0",
            "support_chamber_temp_control": "0",
            "support_air_filtration": "0",
            "host_type": "octoprint",
        })
        write("machine", name, finish(cfg, "machine", name, "printer_settings_id"))


# -------------------------------------------------------------- processes ----

PROCESSES = {
    "0.12mm Fine @SV04":     dict(src="0.12mm Fine @Voron", layer="0.12", top="5", bottom="4"),
    "0.16mm Optimal @SV04":  dict(src="0.15mm Optimal @Voron", layer="0.16", top="5", bottom="3"),
    "0.20mm Standard @SV04": dict(src="0.20mm Standard @Voron", layer="0.2", top="4", bottom="3"),
    "0.28mm Draft @SV04":    dict(src="0.28mm Extra Draft @Voron", layer="0.28", top="3", bottom="3"),
}


def build_processes(vendor: Path) -> None:
    for name, p in PROCESSES.items():
        cfg = resolve(vendor, "process", p["src"])
        cfg.update({
            "layer_height": p["layer"],
            "top_shell_layers": p["top"],
            "bottom_shell_layers": p["bottom"],
            "initial_layer_print_height": "0.24",
            "wall_loops": "3",
            # Klipper config: max_velocity 300, max_accel 1000
            "default_acceleration": "1000",
            "outer_wall_acceleration": "500",
            "inner_wall_acceleration": "1000",
            "top_surface_acceleration": "800",
            "travel_acceleration": "1000",
            "initial_layer_acceleration": "500",
            "accel_to_decel_enable": "0",
            "default_jerk": "0", "initial_layer_jerk": "0", "outer_wall_jerk": "0",
            "inner_wall_jerk": "0", "infill_jerk": "0", "top_surface_jerk": "0",
            "travel_jerk": "0",
            "initial_layer_speed": "25",
            "initial_layer_infill_speed": "40",
            "outer_wall_speed": "40",
            "inner_wall_speed": "60",
            "sparse_infill_speed": "80",
            "internal_solid_infill_speed": "70",
            "top_surface_speed": "40",
            "gap_infill_speed": "40",
            "bridge_speed": "25",
            "support_speed": "60",
            "support_interface_speed": "40",
            "ironing_speed": "20",
            "travel_speed": "150",
            "overhang_1_4_speed": "40", "overhang_2_4_speed": "30",
            "overhang_3_4_speed": "20", "overhang_4_4_speed": "10",
            "enable_prime_tower": "0",
            "prime_tower_width": "35",
            "skirt_loops": "1",
            "filename_format": "{input_filename_base}_{layer_height}mm_{filament_type[0]}_{print_time}.gcode",
            "compatible_printers": PRINTER_NAMES,
            "compatible_printers_condition": "",
        })
        cfg = finish(cfg, "process", name, "print_settings_id")
        cfg["compatible_printers"] = PRINTER_NAMES
        cfg["compatible_printers_condition"] = ""
        write("process", name, cfg)


# -------------------------------------------------------------- filaments ----

FILAMENTS = {
    "Generic PLA @SV04":  dict(src="Generic PLA @Voron", temp=205, temp0=210, bed=60, bed0=60,
                               fan_min=100, fan_max=100, vol=12, type="PLA"),
    "Generic PETG @SV04": dict(src="Generic PETG @Voron", temp=235, temp0=240, bed=75, bed0=80,
                               fan_min=30, fan_max=50, vol=8, type="PETG"),
    "Generic ABS @SV04":  dict(src="Generic ABS @Voron", temp=245, temp0=250, bed=100, bed0=100,
                               fan_min=0, fan_max=20, vol=12, type="ABS"),
    "Generic TPU @SV04":  dict(src="Generic TPU @Voron", temp=220, temp0=225, bed=50, bed0=50,
                               fan_min=100, fan_max=100, vol=3.5, type="TPU"),
}
PLATES = ("cool_plate_temp", "eng_plate_temp", "hot_plate_temp",
          "textured_plate_temp", "supertack_plate_temp")


def build_filaments(vendor: Path) -> None:
    for name, f in FILAMENTS.items():
        cfg = resolve(vendor, "filament", f["src"])
        for plate in PLATES:
            cfg[plate] = [str(f["bed"])]
            cfg[plate + "_initial_layer"] = [str(f["bed0"])]
        cfg.update({
            "filament_type": [f["type"]],
            "filament_vendor": ["Generic"],
            "filament_diameter": ["1.75"],
            "nozzle_temperature": [str(f["temp"])],
            "nozzle_temperature_initial_layer": [str(f["temp0"])],
            "fan_min_speed": [str(f["fan_min"])],
            "fan_max_speed": [str(f["fan_max"])],
            "filament_max_volumetric_speed": [str(f["vol"])],
        })
        if f["type"] == "TPU":
            cfg["filament_retraction_length"] = ["1"]
            cfg["filament_retraction_speed"] = ["20"]
        cfg = finish(cfg, "filament", name, "filament_settings_id")
        cfg["filament_id"] = "null"
        cfg["compatible_printers"] = PRINTER_NAMES
        cfg["compatible_printers_condition"] = ""
        write("filament", name, cfg)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    voron = Path(sys.argv[1]) / "Voron"
    if not voron.is_dir():
        sys.exit(f"Voron profiles not found in {voron}")
    build_machines(voron)
    build_processes(voron)
    build_filaments(voron)
