#!/usr/bin/env bash
# Installiert die Sovol-SV04-Klipper-Profile in Bambu Studio (Linux, nativ + Flatpak).
# Installs the Sovol SV04 Klipper presets into Bambu Studio (Linux, native + Flatpak).
set -e
SRC="$(cd "$(dirname "$0")" && pwd)/Bambu Studio Profile"
[ -d "$SRC/machine" ] || { echo "FEHLER: '$SRC' nicht gefunden – Skript im Repo-Ordner ausführen."; exit 1; }

if pgrep -f -i bambu-studio >/dev/null 2>&1; then
  echo "Bitte Bambu Studio zuerst schließen / Please close Bambu Studio first."; exit 1
fi

BASES=()
for b in "$HOME/.config/BambuStudio" "$HOME/.var/app/com.bambulab.BambuStudio/config/BambuStudio"; do
  [ -d "$b" ] && BASES+=("$b")
done
[ ${#BASES[@]} -gt 0 ] || { echo "Kein Bambu-Studio-Konfigurationsordner gefunden. Bambu Studio einmal starten und erneut versuchen."; exit 1; }

for B in "${BASES[@]}"; do
  # Druckbett-Modell neben die Konfiguration legen (Flatpak darf $HOME lesen)
  mkdir -p "$B/sv04"
  cp "$SRC/bed/SV04.stl" "$B/sv04/SV04.stl"
  # user/default = nicht angemeldet, user/<ID> = Bambu-Konto
  USERS=("$B/user/default")
  for u in "$B"/user/*/; do u="${u%/}"; [ "$u" != "$B/user/default" ] && USERS+=("$u"); done
  for U in "${USERS[@]}"; do
    echo "→ Installiere nach $U"
    for kind in machine process filament; do
      mkdir -p "$U/$kind"
      cp "$SRC/$kind"/*.json "$U/$kind/"
    done
    # 3D-Bettmodell nur für die Profile mit vollem 300-mm-Bett eintragen
    python3 - "$U/machine" "$B/sv04/SV04.stl" <<'EOF'
import json, sys, pathlib
for p in pathlib.Path(sys.argv[1]).glob("Sovol SV04 Klipper *.json"):
    d = json.loads(p.read_text())
    if d.get("printable_area", [""])[1].startswith("300x"):
        d["bed_custom_model"] = sys.argv[2]
        p.write_text(json.dumps(d, indent=4, ensure_ascii=False) + "\n")
EOF
  done
done
echo; echo "Fertig! Bambu Studio starten und unter 'Drucker' → 'Benutzer-Presets' einen 'Sovol SV04 Klipper …' wählen."
