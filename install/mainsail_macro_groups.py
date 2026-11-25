#!/usr/bin/env python3
"""Arrange the SV04 macros in Mainsail as tidy macro groups (panels).

Writes the groups into the Mainsail settings in the Moonraker database
(namespace "mainsail", key "macros.macrogroups.<id>") and switches the macro
mode to "expert", so Mainsail shows only the groups instead of every macro.
Fixed group ids: running it again updates the groups instead of duplicating them.
Groups you created yourself are left untouched.

Usage (on the Pi):  python3 mainsail_macro_groups.py [--url http://localhost:7125] [--remove]
Then reload Mainsail in the browser (F5).
"""
import argparse
import json
import sys
import urllib.error
import urllib.request

S, P, A = "standby", "printing", "paused"   # printer states in which a macro is shown

# (group id, name, colour, [ (macro, colour, states) ])  - names are sorted by Mainsail
GROUPS = [
    ("sv04-1-main", "1 SV04", "primary", [
        ("SV04_MENU", "group", {S, A}),
        ("LOAD_FILAMENT", "group", {S, A}),
        ("UNLOAD_FILAMENT", "group", {S, A}),
    ]),
    ("sv04-2-print", "2 During print", "warning", [
        ("M600", "group", {P}),
        ("SAVE_Z_OFFSET", "group", {S, P, A}),
    ]),
    ("sv04-3-calibration", "3 Calibration", "secondary", [
        ("Z_TILT_HOME", "group", {S}),
        ("BED_LEVEL_SCREWS", "group", {S}),
        ("Z_OFFSET_CALIBRATE", "primary", {S}),
        ("CALIBRATE_T1_Z", "primary", {S}),
        ("PID_TUNE_BED", "warning", {S}),
        ("PID_TUNE_HOTEND", "warning", {S}),
        ("INPUT_SHAPER_STATUS", "group", {S}),
        ("SHAPER_CALIBRATE_SV04", "warning", {S}),   # only visible with adxl345.cfg
    ]),
    ("sv04-4-idex", "4 IDEX", "success", [
        ("T0", "group", {S}),
        ("T1", "group", {S}),
        ("ACTIVATE_COPY_MODE", "group", {S}),
        ("ACTIVATE_MIRROR_MODE", "group", {S}),
        ("CLEAN_NOZZLE", "group", {S}),
    ]),
    ("sv04-5-settings", "5 Settings", "secondary", [
        ("SET_T1_OFFSET", "group", {S}),
        ("INPUT_SHAPER_SET", "group", {S}),
        ("PREHEAT60", "group", {S}),
        ("PREHEAT80", "group", {S}),
    ]),
]


def request(url, method="GET", body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode() or "{}")


def group_value(gid, name, colour, macros):
    states = set().union(*(m[2] for m in macros))
    return {
        "id": None,
        "name": name,
        "color": colour,
        "showInStandby": S in states,
        "showInPrinting": P in states,
        "showInPause": A in states,
        "macros": [{
            "pos": pos,
            "name": macro,
            "color": mcolour,
            "showInStandby": S in st,
            "showInPrinting": P in st,
            "showInPause": A in st,
        } for pos, (macro, mcolour, st) in enumerate(macros, start=1)],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--url", default="http://localhost:7125", help="Moonraker URL")
    ap.add_argument("--remove", action="store_true", help="remove the SV04 groups again")
    args = ap.parse_args()
    db = args.url.rstrip("/") + "/server/database/item"

    # Read the whole Mainsail namespace: Mainsail only stores the key "macros"
    # once somebody changed a macro setting, so it is usually missing.
    try:
        namespace = request(db + "?namespace=mainsail")["result"]["value"]
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("Mainsail has not created its settings yet - open Mainsail in the browser once, then run again.")
            return 1
        raise
    except (urllib.error.URLError, OSError) as e:
        print(f"Moonraker not reachable at {args.url}: {e}")
        return 1

    current = namespace.get("macros", {}) if isinstance(namespace, dict) else {}
    existing = current.get("macrogroups", {}) or {}
    ours = {g[0] for g in GROUPS}
    if args.remove:
        for gid in ours & set(existing):
            request(f"{db}?namespace=mainsail&key=macros.macrogroups.{gid}", "DELETE")
            print(f"removed {existing[gid].get('name', gid)}")
        print("Done - reload Mainsail (F5). Switch back to simple mode under Settings -> Macros if you like.")
        return 0

    foreign = [g.get("name", k) for k, g in existing.items() if k not in ours]
    if foreign:
        print("Keeping your own macro groups:", ", ".join(foreign))
    for gid, name, colour, macros in GROUPS:
        request(db, "POST", {"namespace": "mainsail", "key": f"macros.macrogroups.{gid}",
                             "value": group_value(gid, name, colour, macros)})
        print(f"{'updated' if gid in existing else 'created'} group '{name}'")
    request(db, "POST", {"namespace": "mainsail", "key": "macros.mode", "value": "expert"})
    print("Macro mode set to 'expert'. Reload Mainsail in the browser (F5).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
