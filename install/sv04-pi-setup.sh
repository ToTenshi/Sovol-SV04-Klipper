#!/usr/bin/env bash
# Sovol SV04 setup for a fresh MainsailOS - no KIAUH needed.
# Einrichtung des SV04 auf einem frischen MainsailOS - ohne KIAUH.
#
# On the Raspberry Pi (via SSH):
#   git clone <this repository> ~/Sovol-SV04-Klipper
#   ~/Sovol-SV04-Klipper/install/sv04-pi-setup.sh
#
# What it does (asks first):
#   1. optional: switch Klipper to the Bully85 fork (original Sovol display)
#   2. back up ~/printer_data/config and copy the SV04 configuration
#      (variables.cfg and an existing SV04 printer.cfg are kept)
#   3. select STM32/GD32 and the serial port of the printer
#   4. build the printer firmware (no make menuconfig needed) -> firmware.bin
#   5. optional: install KlipperScreen with its official installer
#   6. arrange the macros in Mainsail as tidy groups (panels)
#   7. restart Klipper
#
# Options: --update          refresh the macro files, offer to update printer.cfg (keeps your values)
#          --variant original|display   --chip stm32|gd32
#          --firmware yes|no --klipperscreen yes|no --macros yes|no
#          --printer-cfg yes|no   update an existing SV04 printer.cfg (keeps port, chip, SAVE_CONFIG)
#          --yes (no questions)
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
KLIPPER="${SV04_KLIPPER_DIR:-$HOME/klipper}"
CONFIG="${SV04_CONFIG_DIR:-$HOME/printer_data/config}"
SERIAL_DIR="${SV04_SERIAL_DIR:-/dev/serial/by-id}"
MOONRAKER_URL="${SV04_MOONRAKER_URL:-http://localhost:7125}"
FORK_URL="${SV04_FORK_URL:-https://github.com/Bully85/klipper}"
MAINLINE_URL="${SV04_MAINLINE_URL:-https://github.com/Klipper3d/klipper}"

VARIANT="" CHIP="" FIRMWARE="" KSCREEN="" MACROS="" PRINTERCFG="" UPDATE=0 YES=0 SWITCHED=0
while [ $# -gt 0 ]; do
    case "$1" in
        --update) UPDATE=1 ;;
        --variant) VARIANT="$2"; shift ;;
        --chip) CHIP="$2"; shift ;;
        --firmware) FIRMWARE="$2"; shift ;;
        --klipperscreen) KSCREEN="$2"; shift ;;
        --macros) MACROS="$2"; shift ;;
        --printer-cfg) PRINTERCFG="$2"; shift ;;
        --yes|-y) YES=1 ;;
        -h|--help) sed -n '2,26p' "$0"; exit 0 ;;
        *) echo "Unknown option $1"; exit 1 ;;
    esac
    shift
done

say()  { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
info() { printf '    %s\n' "$*"; }
warn() { printf '\033[1;33m    WARNING: %s\033[0m\n' "$*"; }
die()  { printf '\033[1;31mERROR: %s\033[0m\n' "$*" >&2; exit 1; }

ask() {   # ask <question> <default> -> echoes the answer
    local answer
    if [ $YES = 1 ] || [ ! -t 0 ]; then echo "$2"; return; fi
    read -r -p "    $1 [$2]: " answer
    echo "${answer:-$2}"
}

# ------------------------------------------------------------------ checks --
[ "$(id -u)" != 0 ] || die "Do not run as root (no sudo) - run as the normal user, e.g. pi"
[ -d "$KLIPPER" ] || die "$KLIPPER not found - is this a MainsailOS?"
[ -d "$CONFIG" ] || die "$CONFIG not found - is this a MainsailOS?"

if [ -z "$VARIANT" ]; then
    if git -C "$KLIPPER" remote get-url origin 2>/dev/null | grep -qi bully85; then def=display; else def=original; fi
    if [ $UPDATE = 1 ]; then VARIANT=$def; else
        info "Variant: 'original' = original Klipper, no Sovol display (recommended)"
        info "         'display'  = Bully85 Klipper fork with the original Sovol display"
        VARIANT=$(ask "original or display?" "$def")
    fi
fi
case "$VARIANT" in
    original) SRC="$REPO/config/Sv04-works-with origin-klipper" ;;
    display)  SRC="$REPO/config/SV04-with-display" ;;
    *) die "Unknown variant '$VARIANT' (original or display)" ;;
esac

# ------------------------------------------------------- 1. Klipper source --
switch_klipper() {   # switch_klipper <url> <label>
    say "Switching Klipper to $2"
    git -C "$KLIPPER" remote set-url origin "$1"
    git -C "$KLIPPER" fetch origin
    git -C "$KLIPPER" checkout -B master origin/master
    # the other Klipper version may need other Python packages
    if [ -x "$HOME/klippy-env/bin/pip" ] && [ -f "$KLIPPER/scripts/klippy-requirements.txt" ]; then
        "$HOME/klippy-env/bin/pip" install -q -r "$KLIPPER/scripts/klippy-requirements.txt"
    fi
    SWITCHED=1
}
if [ "$VARIANT" = display ] && ! git -C "$KLIPPER" remote get-url origin | grep -qi bully85; then
    switch_klipper "$FORK_URL" "the Bully85 fork (original Sovol display)"
    info "Mainsail may show Klipper as 'invalid' afterwards - see README (moonraker.env -g)."
elif [ "$VARIANT" = original ] && git -C "$KLIPPER" remote get-url origin | grep -qi bully85; then
    # the fork is from January 2024 - the 'original' config needs current Klipper
    switch_klipper "$MAINLINE_URL" "original Klipper (was: Bully85 fork)"
fi

# ------------------------------------------- Klipper must be current enough --
# Older MainsailOS images ship an old Klipper. Klipper must be updated BEFORE the
# firmware is built, because host and printer firmware have to match.
if [ "$VARIANT" = original ]; then
    kdate=$(git -C "$KLIPPER" log -1 --format=%ct 2>/dev/null || echo 0)
    if [ "$kdate" -lt 1710374400 ]; then   # 2024-03-14
        die "Klipper on this Pi is from $(date -d "@$kdate" +%Y-%m-%d 2>/dev/null || echo 'an old version') - too old.
       Update it first in Mainsail: Machine -> Update Manager -> update everything.
       Then run this script again (it builds the matching firmware)."
    fi
fi

# ------------------------------------------------------- 2. configuration --
say "Copying the SV04 configuration to $CONFIG"
BACKUP="$CONFIG/../config_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
tar -czf "$BACKUP" -C "$CONFIG" .
info "Backup: $(cd "$(dirname "$BACKUP")" && pwd)/$(basename "$BACKUP")"

FRESH_PRINTER_CFG=0
for f in "$SRC"/*; do
    name=$(basename "$f")
    case "$name" in
        variables.cfg)
            if [ -f "$CONFIG/$name" ]; then info "keep    $name (your offsets)"; continue; fi ;;
        printer.cfg)
            if [ -f "$CONFIG/$name" ] && grep -q '^\[dual_carriage\]' "$CONFIG/$name"; then
                # bring an existing SV04 printer.cfg up to date: serial port, chip, includes
                # and the SAVE_CONFIG block (z_offset, PID ...) are kept
                if python3 "$REPO/install/merge_printer_cfg.py" "$f" "$CONFIG/$name" > /tmp/sv04_printer_cfg.diff; then
                    info "keep    $name (up to date)"
                else
                    info "The repo has a newer printer.cfg. Changes (- yours, + new):"
                    sed 's/^/        /' /tmp/sv04_printer_cfg.diff
                    [ -n "$PRINTERCFG" ] || PRINTERCFG=$(ask "Update printer.cfg? Serial port, chip, includes and SAVE_CONFIG block are kept (yes/no)" yes)
                    if [ "$PRINTERCFG" = yes ]; then
                        python3 "$REPO/install/merge_printer_cfg.py" "$f" "$CONFIG/$name" --write | sed 's/^/    /'
                    else
                        info "keep    $name (not updated)"
                    fi
                fi
                rm -f /tmp/sv04_printer_cfg.diff
                continue
            fi
            [ $UPDATE = 1 ] && { info "skip    $name (--update)"; continue; }
            FRESH_PRINTER_CFG=1 ;;
    esac
    cp -r "$f" "$CONFIG/"
    info "copied  $name"
done

# ------------------------------------------------- 3. chip and serial port --
if [ $FRESH_PRINTER_CFG = 1 ]; then
    [ -n "$CHIP" ] || { info "Chip on the mainboard: STM32 (most printers) or GD32 (Giga Device)"; CHIP=$(ask "stm32 or gd32?" stm32); }
    case "$CHIP" in
        stm32) ;;
        gd32)
            say "Activating the GD32 Z stepper block"
            awk '
                /^#+ *Use this if yor Chip is STM32/ { mode = "stm"; print; next }
                /^#+ *Use this if yor Chip is Giga Device/ { mode = "gd"; print; next }
                /^#+$/ { mode = ""; print; next }
                mode == "stm" && /^[^#[:space:]]/ { print "#" $0; next }
                mode == "stm" && /^\[/ { print "#" $0; next }
                mode == "gd" && /^#[^#]/ { print substr($0, 2); next }
                { print }
            ' "$CONFIG/printer.cfg" > "$CONFIG/printer.cfg.tmp" && mv "$CONFIG/printer.cfg.tmp" "$CONFIG/printer.cfg" ;;
        *) die "Unknown chip '$CHIP' (stm32 or gd32)" ;;
    esac

    say "Serial port of the printer"
    ports=()
    for p in "$SERIAL_DIR"/*; do [ -e "$p" ] && ports+=("$p"); done
    port=""
    if [ ${#ports[@]} -eq 1 ]; then
        port="${ports[0]}"
    elif [ ${#ports[@]} -gt 1 ]; then
        for p in "${ports[@]}"; do case "$p" in *1a86*) port="$p" ;; esac; done
        for p in "${ports[@]}"; do info "found $p"; done
        port=$(ask "Which port is the printer?" "${port:-${ports[0]}}")
    fi
    if [ -n "$port" ]; then
        awk -v port="$port" '
            /^\[mcu\]/ { in_mcu = 1 } /^\[/ && !/^\[mcu\]/ { in_mcu = 0 }
            in_mcu && /^serial:/ { print "serial: " port; next } { print }
        ' "$CONFIG/printer.cfg" > "$CONFIG/printer.cfg.tmp" && mv "$CONFIG/printer.cfg.tmp" "$CONFIG/printer.cfg"
        info "serial: $port"
    else
        warn "No printer found in $SERIAL_DIR - connect it via USB, switch it on and set [mcu] serial: in printer.cfg"
    fi
fi

# ------------------------------------------------------------- 4. firmware --
# Compare the firmware on the printer with the Klipper version on the Pi (via Moonraker).
# After a Klipper update or a switch fork <-> original they differ, and Klipper warns
# "MCU 'mcu' has deprecated code ... Recompiling and flashing is recommended".
FW_MISMATCH=0
versions=$(curl -fsS "$MOONRAKER_URL/printer/objects/query?mcu" 2>/dev/null | python3 -c '
import json, sys
try:
    print(json.load(sys.stdin)["result"]["status"]["mcu"]["mcu_version"])
except Exception:
    pass' 2>/dev/null || true)
host_version=$(git -C "$KLIPPER" describe --always --tags --long --dirty 2>/dev/null || true)
if [ -n "$versions" ] && [ -n "$host_version" ] && [ "${versions%-dirty}" != "${host_version%-dirty}" ] && [ $SWITCHED = 0 ]; then
    FW_MISMATCH=1
    warn "Printer firmware ($versions) does not match Klipper on the Pi ($host_version) - rebuild and flash it"
fi
[ $SWITCHED = 1 ] && FW_MISMATCH=1   # new Klipper code always needs new printer firmware
if [ -z "$FIRMWARE" ]; then
    if [ $FW_MISMATCH = 1 ]; then FIRMWARE=$(ask "Build the matching printer firmware now? (yes/no)" yes)
    elif [ $UPDATE = 1 ]; then FIRMWARE=no
    else FIRMWARE=$(ask "Build the printer firmware now? (yes/no)" yes); fi
fi
if [ "$FIRMWARE" = yes ]; then
    say "Building the printer firmware (STM32F103, 28KiB bootloader, USART1 PA10/PA9, 115200 baud)"
    {
        echo "CONFIG_LOW_LEVEL_OPTIONS=y"
        echo "CONFIG_MACH_STM32=y"
        echo "CONFIG_MACH_STM32F103=y"
        echo "CONFIG_STM32_FLASH_START_7000=y"
        echo "CONFIG_STM32_CLOCK_REF_8M=y"
        echo "CONFIG_STM32_SERIAL_USART1=y"
        echo "CONFIG_SERIAL_BAUD=115200"
        if [ "$VARIANT" = display ]; then
            echo "CONFIG_T5UID1_SERIAL=y"
            echo "CONFIG_STM32_T5UID1_SERIAL_USART3_PB11_PB10=y"
        fi
    } > "$KLIPPER/.config"
    make -C "$KLIPPER" olddefconfig >/dev/null
    required="CONFIG_MACH_STM32F103=y CONFIG_STM32_FLASH_START_7000=y CONFIG_STM32_CLOCK_REF_8M=y CONFIG_STM32_SERIAL_USART1=y CONFIG_SERIAL_BAUD=115200"
    [ "$VARIANT" = display ] && required="$required CONFIG_T5UID1_SERIAL=y CONFIG_STM32_T5UID1_SERIAL_USART3_PB11_PB10=y"
    for opt in $required; do
        grep -qx "$opt" "$KLIPPER/.config" || die "Firmware option $opt was not accepted - run 'make menuconfig' in $KLIPPER and check the README"
    done
    make -C "$KLIPPER" clean >/dev/null
    make -C "$KLIPPER" -j"$(nproc)" >/dev/null
    cp "$KLIPPER/out/klipper.bin" "$CONFIG/firmware.bin"
    info "Firmware: $CONFIG/firmware.bin"
    info "-> In Mainsail (Machine) download firmware.bin, copy it to the printer SD card,"
    info "   unplug the original display, insert the card and switch the printer on."
    info "   Delete firmware.bin from the Mainsail config folder afterwards."
fi

# --------------------------------------------------------- 5. KlipperScreen --
[ -n "$KSCREEN" ] || { [ $UPDATE = 1 ] && KSCREEN=no || KSCREEN=$(ask "Install KlipperScreen for a touch screen? (yes/no)" no); }
if [ "$KSCREEN" = yes ]; then
    say "Installing KlipperScreen (official installer, answer its questions)"
    [ -d "$HOME/KlipperScreen" ] || git clone https://github.com/KlipperScreen/KlipperScreen.git "$HOME/KlipperScreen"
    "$HOME/KlipperScreen/scripts/KlipperScreen-install.sh"
    if ! grep -q '^\[update_manager KlipperScreen\]' "$CONFIG/moonraker.conf" 2>/dev/null; then
        cat >> "$CONFIG/moonraker.conf" <<'EOF'

[update_manager KlipperScreen]
type: git_repo
path: ~/KlipperScreen
origin: https://github.com/KlipperScreen/KlipperScreen.git
virtualenv: ~/.KlipperScreen-env
requirements: scripts/KlipperScreen-requirements.txt
managed_services: KlipperScreen
EOF
        info "Added KlipperScreen to the Mainsail update manager (moonraker.conf)"
    fi
fi

# ------------------------------------------------------- 6. Mainsail macros --
[ -n "$MACROS" ] || { [ $UPDATE = 1 ] && MACROS=yes || MACROS=$(ask "Arrange the macros in Mainsail as groups? (yes/no)" yes); }
if [ "$MACROS" = yes ]; then
    say "Arranging the macros in Mainsail"
    python3 "$REPO/install/mainsail_macro_groups.py" --url "$MOONRAKER_URL" | sed 's/^/    /' \
        || warn "Could not set up the macro groups - run install/mainsail_macro_groups.py later"
fi

# --------------------------------------------------------------- 7. restart --
say "Restarting Klipper"
# New Klipper code (fork switch) needs a service restart, a config change only RESTART
if [ $SWITCHED = 1 ]; then endpoint="machine/services/restart?service=klipper"; else endpoint="printer/restart"; fi
if command -v curl >/dev/null && curl -fsS -X POST "$MOONRAKER_URL/$endpoint" >/dev/null 2>&1; then
    info "Klipper restarted via Moonraker"
elif [ $SWITCHED = 1 ]; then
    sudo systemctl restart klipper && info "Klipper service restarted"
else
    info "Please restart Klipper in Mainsail (Power menu -> Klipper restart)"
fi

say "Done"
info "Next: flash firmware.bin (if built), then run SOVOL_MENU in Mainsail and calibrate."
info "Guide: $REPO/docs/Kalibrierung-Calibration.md"
