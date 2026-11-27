#!/usr/bin/env python3
"""Update an existing SV04 printer.cfg to the current template of the repository.

Kept from the user's file:
  - [mcu] serial
  - the active Z stepper block (STM32 or GD32)
  - which [include ...] lines are enabled/disabled (e.g. adxl345.cfg)
  - the complete #*# SAVE_CONFIG block (z_offset, PID, ...); options set there are commented out
    in the template part, exactly like Klipper's SAVE_CONFIG does - otherwise Klipper ignores them
Everything else comes from the template. Other own changes are shown as a diff before.

Usage: merge_printer_cfg.py TEMPLATE USER_CFG [--write]
  without --write: print the diff, exit code 0 = up to date, 10 = would change
"""
import configparser
import difflib
import re
import sys

AUTOSAVE = "#*# <---------------------- SAVE_CONFIG ---------------------->"


def split_autosave(text):
    i = text.find(AUTOSAVE)
    return (text, "") if i < 0 else (text[:i].rstrip("\n") + "\n", text[i:])


def mcu_serial(text):
    m = re.search(r"(?ms)^\[mcu\]\s*$(.*?)(?=^\[)", text + "\n[")
    if m:
        s = re.search(r"(?m)^serial:\s*(\S.*)$", m.group(1))
        if s:
            return s.group(1).strip()
    return None


def chip(text):
    cp = configparser.RawConfigParser(strict=False, inline_comment_prefixes=(";", "#"))
    try:
        cp.read_string(text)
        return "gd32" if cp.get("stepper_z", "step_pin").strip() == "PB3" else "stm32"
    except (configparser.Error, KeyError):
        return "stm32"


def to_gd32(text):
    out, mode = [], ""
    for line in text.split("\n"):
        if re.match(r"^#+ *Use this if yor Chip is STM32", line):
            mode = "stm"
        elif re.match(r"^#+ *Use this if yor Chip is Giga Device", line):
            mode = "gd"
        elif re.match(r"^#+$", line):
            mode = ""
        elif mode == "stm" and line and not line[0] in "# \t":
            line = "#" + line
        elif mode == "gd" and re.match(r"^#[^#]", line):
            line = line[1:]
        out.append(line)
    return "\n".join(out)


def autosave_options(autosave):
    """{section: {option, ...}} from the #*# SAVE_CONFIG block"""
    cp = configparser.RawConfigParser(strict=False)
    lines = [l[4:] if l.startswith("#*# ") else l[3:] for l in autosave.splitlines() if l.startswith("#*#")]
    # skip the header lines ("<--- SAVE_CONFIG --->", "DO NOT EDIT ...") up to the first section
    first = next((i for i, l in enumerate(lines) if l.startswith("[")), len(lines))
    body = "\n".join(lines[first:])
    try:
        cp.read_string(body)
    except configparser.Error:
        return {}
    return {sec: set(cp.options(sec)) for sec in cp.sections()}


def strip_duplicates(text, saved):
    """Comment out options that the SAVE_CONFIG block sets - exactly like Klipper's SAVE_CONFIG
    (klippy/configfile.py _strip_duplicates). Otherwise Klipper IGNORES the saved value
    (e.g. a calibrated z_offset or PID values) and uses the template value instead."""
    out, section, dup = [], None, False
    for line in text.split("\n"):
        pruned = re.sub(r"[#;].*$", "", line).rstrip()
        if not pruned:
            out.append(line)
            continue
        if pruned[0].isspace():
            out.append("#" + line if dup else line)
            continue
        dup = False
        if pruned.startswith("["):
            section = pruned[1:].split("]")[0].strip()
            out.append(line)
            continue
        field = re.split(r"[:=]", pruned, maxsplit=1)[0].strip().lower()
        if section in saved and field in saved[section]:
            dup = True
            line = "#" + line
        out.append(line)
    return "\n".join(out)


def includes(text):
    return {m.group(2): m.group(1) == "#" for m in re.finditer(r"(?m)^(#?)\[include ([^\]]+)\]", text)}


def merge(template, user):
    body, autosave = split_autosave(user)
    body = body.rstrip("\n") + "\n"
    new = split_autosave(template)[0].rstrip("\n") + "\n"
    serial = mcu_serial(body)
    if serial:
        new = re.sub(r"(?ms)(^\[mcu\]\s*$.*?^serial:)[ \t]*\S.*?$", lambda m: m.group(1) + " " + serial, new, count=1)
    if chip(body) == "gd32":
        new = to_gd32(new)
    user_inc = includes(body)
    for name, commented in user_inc.items():
        new = re.sub(r"(?m)^#?\[include " + re.escape(name) + r"\]", ("#" if commented else "") + "[include " + name + "]", new)
    new = strip_duplicates(new, autosave_options(autosave))
    return body, new, (new.rstrip("\n") + "\n\n" + autosave if autosave else new)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    template = open(sys.argv[1], encoding="utf-8").read()
    user = open(sys.argv[2], encoding="utf-8").read()
    body, new_body, result = merge(template, user)
    diff = list(difflib.unified_diff(body.splitlines(), new_body.splitlines(),
                                     "your printer.cfg", "new printer.cfg", n=0, lineterm=""))
    if not diff:
        print("printer.cfg is up to date")
        return 0
    if "--write" in sys.argv:
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            f.write(result)
        print("printer.cfg updated (serial, chip, includes and SAVE_CONFIG block kept)")
        return 0
    print("\n".join(diff))
    return 10


if __name__ == "__main__":
    sys.exit(main())
