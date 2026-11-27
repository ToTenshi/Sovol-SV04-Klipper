#!/usr/bin/env python3
"""Live check of a running SV04 (Moonraker API, READ ONLY - nothing is moved or changed).

Finds the problems we hit in practice:
  - Klipper not ready, config warnings, printer firmware != Klipper version
  - SAVE_CONFIG values that Klipper ignores (option also active above the SAVE_CONFIG block)
  - z_offset not calibrated / not loaded, implausible T1 offset
  - macro files on the Pi older than the repo (run sv04-pi-setup.sh --update)
  - macro names Klipper can't call, missing SV04 macros
  - runs tools/check_klipper_config.py and tools/simulate_z_offset.py on the
    configuration that is INSTALLED on the Pi

Usage:  python3 tools/printer_check.py [--host 192.168.178.199] [--key APIKEY]
Host/key can also come from SV04_HOST / SV04_API_KEY or tools/printer.local.env
(HOST=... and KEY=... lines; that file is git-ignored - never commit the API key).
Exit code 1 if a check FAILs.
"""
import argparse
import configparser
import filecmp
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "install"))
import merge_printer_cfg  # noqa: E402  (autosave helpers)

ARGS_R = re.compile(r"([A-Z_]+|[A-Z*])")
EXPECTED_MACROS = ["SOVOL_MENU", "Z_OFFSET_CALIBRATE", "CALIBRATE_Z_T1", "SET_OFFSET_T1", "SAVE_Z_OFFSET",
                   "Z_OFFSET_MENU", "Z_OFFSET_UP", "Z_OFFSET_DOWN", "PROBE_CHECK", "BED_SCREWS_CHECK",
                   "BED_LEVEL_SCREWS", "Z_TILT_HOME", "INPUT_SHAPER_STATUS", "LOAD_FILAMENT",
                   "UNLOAD_FILAMENT", "PREHEAT", "T0", "T1", "START_PRINT", "END_PRINT"]
results = []


def report(level, text):
    results.append(level)
    print(f"  {level:4s} {text}")


def load_local_env():
    env = {}
    path = os.path.join(HERE, "printer.local.env")
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.strip().split("=", 1)
                env[k.strip().upper()] = v.strip()
    return env


class Moonraker:
    def __init__(self, host, key):
        # resolve IPv4 ourselves - *.local often resolves to an unreachable IPv6 address first
        try:
            ip = socket.getaddrinfo(host, 80, socket.AF_INET)[0][4][0]
        except socket.gaierror:
            ip = host
        self.base, self.key = f"http://{ip}", key

    def get(self, path, raw=False):
        req = urllib.request.Request(self.base + path, headers={"X-Api-Key": self.key} if self.key else {})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = r.read()
        return data if raw else json.loads(data)["result"]

    def query(self, *objects):
        q = "&".join(urllib.parse.quote(o) for o in objects)
        return self.get("/printer/objects/query?" + q)["status"]


def klipper_command(name):
    parts = ARGS_R.split(name.upper())
    return parts[1] + parts[2].strip() if len(parts) >= 3 else ""


def main():
    env = load_local_env()
    ap = argparse.ArgumentParser(description="Read-only live check of the SV04")
    ap.add_argument("--host", default=os.environ.get("SV04_HOST", env.get("HOST", "sv04.local")))
    ap.add_argument("--key", default=os.environ.get("SV04_API_KEY", env.get("KEY", "")))
    args = ap.parse_args()
    m = Moonraker(args.host, args.key)

    print(f"SV04 live check - {args.host} ({m.base})\n")
    print("Klipper / firmware")
    try:
        info = m.get("/printer/info")
    except Exception as e:  # noqa: BLE001
        print(f"  FAIL Moonraker not reachable: {e}")
        return 1
    report("OK" if info["state"] == "ready" else "FAIL", f"Klipper state: {info['state']} - {info['state_message'].strip()[:90]}")
    st = m.query("mcu", "configfile", "save_variables", "print_stats", "gcode_move", "gcode_macro _SOVOL_TOOL_OFFSET",
                 "dual_carriage", "toolhead")
    host_v, mcu_v = info["software_version"], st["mcu"].get("mcu_version", "?")
    report("OK" if host_v.split("-dirty")[0] == mcu_v.split("-dirty")[0] else "WARN",
           f"firmware {mcu_v} / Klipper {host_v}" + ("" if host_v == mcu_v else " -> sv04-pi-setup.sh --update --firmware yes, then flash"))
    for w in st["configfile"].get("warnings", []):
        report("WARN", "Klipper: " + w.get("message", str(w)).strip()[:150])
    state = st["print_stats"]["state"]
    report("INFO", f"print state: {state}" + (" (checks are read-only, nothing is sent)" if state in ("printing", "paused") else ""))

    print("\nZ offset")
    cfg = st["configfile"]
    settings = cfg["settings"]
    loaded = settings.get("bltouch", {}).get("z_offset")
    printer_cfg = m.get("/server/files/config/printer.cfg", raw=True).decode("utf-8", "replace")
    body, autosave = merge_printer_cfg.split_autosave(printer_cfg)
    saved = merge_printer_cfg.autosave_options(autosave)
    main_cp = configparser.RawConfigParser(strict=False, inline_comment_prefixes=(";", "#"))
    main_cp.read_string(body)
    ignored = [f"[{sec}] {opt}" for sec, opts in saved.items() for opt in opts
               if main_cp.has_section(sec) and main_cp.has_option(sec, opt)]
    report("FAIL" if ignored else "OK",
           ("SAVE_CONFIG values IGNORED by Klipper (also active above the block): " + ", ".join(ignored) +
            " -> sv04-pi-setup.sh --update (comments them out)") if ignored else "no SAVE_CONFIG value is overridden")
    file_z = re.search(r"(?m)^#\*# z_offset = (\S+)", autosave)
    if loaded is None:
        report("FAIL", "no [bltouch] z_offset loaded")
    elif float(loaded) == 0.0:
        report("FAIL", f"z_offset loaded by Klipper is 0 (file: {file_z.group(1) if file_z else 'none'}) -> Z_OFFSET_CALIBRATE + SAVE_CONFIG")
    else:
        report("OK", f"z_offset loaded: {loaded}")
    if file_z and loaded is not None and abs(float(file_z.group(1)) - float(loaded)) > 0.0005:
        report("FAIL", f"z_offset in printer.cfg {file_z.group(1)} != loaded {loaded} (ignored or Klipper not restarted)")
    pending = [s for s in cfg.get("save_config_pending_items", {}) if not s.startswith("bed_mesh")]
    report("WARN" if pending else "OK", f"pending for SAVE_CONFIG: {', '.join(pending)}" if pending else "nothing important pending for SAVE_CONFIG")
    sv = st["save_variables"]["variables"]
    dz = float(sv.get("dual_z_offset", 0))
    report("FAIL" if abs(dz) > 0.5 else "WARN" if abs(dz) > 0.3 else "OK",
           f"T1 Z offset (dual_z_offset) {dz:+.3f} mm" + (" - implausible, measured with a wrong T0 offset? -> CALIBRATE_Z_T1 again" if abs(dz) > 0.3 else ""))
    tov = st.get("gcode_macro _SOVOL_TOOL_OFFSET", {})
    hz = st["gcode_move"]["homing_origin"][2]
    if "baby0" in tov:
        t1part = (tov["baby0"] + tov["applied_z"]) if tov.get("tool") == 1 else 0.0
        live = hz - tov.get("sync_z", 0) - t1part
        b0 = live if tov.get("tool") == 0 else tov["baby0"]
        b1 = live if tov.get("tool") == 1 else tov["baby1"]
        report("INFO", f"active T{tov.get('tool')}, unsaved babysteps T0 {b0:+.3f} / T1 {b1:+.3f}, G-code Z offset {hz:+.3f}")
    else:
        report("WARN", "old Z offset macros installed (no babystep per nozzle) -> sv04-pi-setup.sh --update")

    print("\nMacros")
    cmds = m.get("/printer/gcode/help")
    bad = sorted(c for c in cmds if klipper_command(c) != c.upper())
    report("FAIL" if bad else "OK", ("not callable (digit inside the name): " + ", ".join(bad)) if bad else f"{len(cmds)} commands, all callable")
    missing = [c for c in EXPECTED_MACROS if c not in cmds]
    report("FAIL" if missing else "OK", ("missing: " + ", ".join(missing)) if missing else "all SV04 macros present")

    print("\nInstalled configuration vs. repository")
    files = [f["path"] for f in m.get("/server/files/list?root=config")]
    variant = "SV04-with-display" if re.search(r"(?m)^\[include t5uid1\.cfg\]", body) else "Sv04-works-with origin-klipper"
    repo_dir = os.path.join(REPO, "config", variant)
    with tempfile.TemporaryDirectory() as tmp:
        for name in os.listdir(repo_dir):
            if name.endswith(".cfg") and name in files:
                with open(os.path.join(tmp, name), "wb") as f:
                    f.write(m.get("/server/files/config/" + urllib.parse.quote(name), raw=True))
        outdated = [n for n in sorted(os.listdir(tmp))
                    if n not in ("printer.cfg", "variables.cfg") and not filecmp.cmp(os.path.join(tmp, n), os.path.join(repo_dir, n), shallow=False)]
        report("WARN" if outdated else "OK",
               (f"differs from the repo ({variant}): " + ", ".join(outdated) + " -> git pull + sv04-pi-setup.sh --update")
               if outdated else f"macro files identical to the repo ({variant})")
        for tool, label in (("simulate_z_offset.py", "Z offset simulation of the installed macros"),):
            r = subprocess.run([sys.executable, "-I", os.path.join(HERE, tool), tmp], capture_output=True, text=True)
            last = (r.stdout.strip().splitlines() or ["?"])[-1]
            report("OK" if r.returncode == 0 else "FAIL", f"{label}: {last}")
            if r.returncode != 0:
                for line in r.stdout.splitlines():
                    if line.strip().startswith("BAD"):
                        print("         " + line.strip())

    fails, warns = results.count("FAIL"), results.count("WARN")
    print(f"\n{fails} FAIL, {warns} WARN")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
