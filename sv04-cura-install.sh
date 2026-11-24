#!/usr/bin/env bash
set -e
SRC="$(cd "$(dirname "$0")" && pwd)/Cura Profile"
[ -d "$SRC/definitions" ] || { echo "FEHLER: '$SRC' nicht gefunden – Skript im Repo-Ordner ausführen."; exit 1; }

TARGETS=()
for base in "$HOME/.local/share/cura" "$HOME/.var/app/com.ultimaker.cura/data/cura"; do
  for d in "$base"/5.*; do [ -d "$d" ] && TARGETS+=("$d"); done
done
if [ ${#TARGETS[@]} -eq 0 ]; then
  TARGETS=("$HOME/.local/share/cura/5.0")
  echo "Hinweis: Kein Cura-Ordner gefunden, nutze ${TARGETS[0]}"
fi

for T in "${TARGETS[@]}"; do
  echo "→ Installiere nach $T"
  mkdir -p "$T/definitions" "$T/extruders" "$T/meshes" "$T/scripts"
  cp -v "$SRC"/definitions/*.def.json "$T/definitions/"
  cp -v "$SRC"/extruders/*.def.json   "$T/extruders/"
  cp -v "$SRC"/meshes/*               "$T/meshes/"
  cp -v "$SRC"/MeshPrintSize.py       "$T/scripts/"
done
echo; echo "Fertig! Jetzt Cura starten."
