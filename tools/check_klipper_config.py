#!/usr/bin/env python3
"""Static check of the SV04 Klipper configs (no printer needed).

- parses every *.cfg like Klipper (configparser, inline comments ';' and '#')
- compiles every gcode template with Klipper's Jinja delimiters
- checks variable_* values with ast.literal_eval (like Klipper)
- warns about '{-' (Jinja whitespace control, not a minus sign)
- applies Klipper's command parser to macro names, rename_existing and every
  command line: digits in the MIDDLE of a name break it ("SV04_MENU" -> "SV04")
- compares the two config folders (only printer.cfg/t5uid1.cfg may differ)

Usage: python3 tools/check_klipper_config.py   (needs: pip install jinja2)
"""
import ast
import configparser
import filecmp
import re
import sys
from pathlib import Path

import jinja2

ROOT = Path(__file__).resolve().parent.parent / "config"
FOLDERS = ["SV04-with-display", "Sv04-works-with origin-klipper"]
ALLOWED_DIFF = {"printer.cfg", "t5uid1.cfg"}
env = jinja2.Environment("{%", "%}", "{", "}")
ARGS_R = re.compile(r"([A-Z_]+|[A-Z*])")   # klippy/gcode.py GCodeDispatch.args_r


def klipper_command(line: str) -> str:
    """The command name Klipper's parser extracts from a G-code line."""
    parts = ARGS_R.split(line.upper())
    return parts[1] + parts[2].strip() if len(parts) >= 3 else ""


def check_name(name: str, where: str) -> int:
    if klipper_command(name) != name.upper():
        print(f"BAD NAME {where}: '{name}' is seen by Klipper as '{klipper_command(name)}' "
              "(no digits in the middle of a command name)")
        return 1
    return 0


def check_folder(folder: Path) -> int:
    errors = 0
    macros = 0
    for f in sorted(folder.glob("*.cfg")):
        if f.name == "variables.cfg":
            continue
        cp = configparser.RawConfigParser(strict=False, inline_comment_prefixes=(";", "#"))
        try:
            cp.read_string(f.read_text(), str(f))
        except configparser.Error as e:
            print(f"PARSE ERROR {f}: {e}")
            errors += 1
            continue
        for sec in cp.sections():
            if sec.startswith("gcode_macro "):
                errors += check_name(sec.split(None, 1)[1].strip(), f"{f.name} [{sec}]")
            if cp.has_option(sec, "rename_existing"):
                errors += check_name(cp.get(sec, "rename_existing"), f"{f.name} [{sec}] rename_existing")
            if not sec.startswith(("gcode_macro ", "delayed_gcode ", "homing_override")):
                continue
            opts = dict(cp.items(sec))
            for line in opts.get("gcode", "").splitlines():
                line = line.strip()
                token = line.split()[0] if line else ""
                if not token or token.startswith(("{", "#", ";")) or "{" in token:
                    continue
                if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", token) and klipper_command(token) != token.upper():
                    print(f"BAD CALL {f.name} [{sec}]: '{token}' is seen by Klipper as '{klipper_command(token)}'")
                    errors += 1
            tpl = opts.get("gcode", "")
            macros += 1
            if re.search(r"\{-(?!%)", tpl):
                print(f"WARNING {f.name} [{sec}]: '{{-' is Jinja whitespace control, write '{{0.0 - x}}'")
                errors += 1
            try:
                env.from_string(tpl)
            except jinja2.TemplateError as e:
                print(f"TEMPLATE ERROR {f.name} [{sec}]: {e}")
                errors += 1
            for key, value in opts.items():
                if key.startswith("variable_"):
                    try:
                        ast.literal_eval(value)
                    except (ValueError, SyntaxError) as e:
                        print(f"VARIABLE ERROR {f.name} [{sec}] {key}={value!r}: {e}")
                        errors += 1
    print(f"{folder.name}: {macros} macros, {'OK' if errors == 0 else f'{errors} problem(s)'}")
    return errors


def compare_folders() -> int:
    a, b = (ROOT / FOLDERS[0]), (ROOT / FOLDERS[1])
    cmp = filecmp.dircmp(a, b)
    problems = [n for n in cmp.diff_files if n not in ALLOWED_DIFF]
    problems += [n for n in cmp.left_only + cmp.right_only if n not in ALLOWED_DIFF]
    for n in problems:
        print(f"FOLDERS DIFFER: {n} (copy shared files from {FOLDERS[0]})")
    if not problems:
        print("Config folders consistent (only printer.cfg / t5uid1.cfg differ)")
    return len(problems)


if __name__ == "__main__":
    total = sum(check_folder(ROOT / f) for f in FOLDERS) + compare_folders()
    sys.exit(1 if total else 0)
