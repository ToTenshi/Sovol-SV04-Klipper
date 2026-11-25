# SV04 Klipper Wiki

Knowledge base for AI assistants and developers of this repository. It holds what can't be read
directly from the code: background, decisions, pitfalls, test methods. It follows the
[LLM Wiki pattern](https://llmwiki.app/) (Karpathy): raw sources plus pages written and maintained by the LLM.

## Structure (schema)

| Layer | Location | Rule |
|-------|----------|------|
| Raw sources | [`sources/`](sources/README.md) | Immutable. One file per finding/research (date + topic), always with origin (URL, file, command). |
| Wiki pages | `wiki/*.md` | One topic per page, written by the LLM, with links to sources and to other pages. |
| Index and log | this page, [log.md](log.md) | Every new page goes into the index, every change into the log. |

## Pages

| Page | Contents |
|------|----------|
| [repo-structure.md](repo-structure.md) | Folders, which files belong together, the two config variants |
| [printer-hardware.md](printer-hardware.md) | MCU, pins, bed, probe, limits, fans |
| [idex.md](idex.md) | Dual carriage, COPY/MIRROR, START_PRINT logic |
| [leveling.md](leveling.md) | Probe, Z tilt, bed mesh, bed screws, PREHEAT |
| [offsets.md](offsets.md) | Z/XY offsets T0/T1, babysteps, calibration wizards |
| [input-shaper.md](input-shaper.md) | Preset, per-carriage values, ADXL345, SAVE_CONFIG lock |
| [klipper-jinja-pitfalls.md](klipper-jinja-pitfalls.md) | Klipper/Jinja traps, Mainsail prompts, fork vs. mainline |
| [slicers.md](slicers.md) | Start G-code conventions, Bambu/Cura/PrusaSlicer specifics |
| [mainsail.md](mainsail.md) | Macro groups, how Mainsail stores settings, prompts |
| [installation.md](installation.md) | MainsailOS, `sv04-pi-setup.sh`, slicer installers, OS paths |
| [testing.md](testing.md) | How to test without a printer |
| [open-points.md](open-points.md) | Untested or open items |

## Operations

- **Ingest:** Save a new finding as a file in `sources/`, then update the affected pages and link the source.
- **Query:** Read the matching pages first. If a fact is missing, research it, save it as a source, then answer.
- **Lint** (with every change in the repo):
  1. Do code, wiki pages, `CHANGELOG.md` (`[Unreleased]`) and both READMEs (DE+EN, same content) agree?
  2. Is every page listed in the index? Do all links work?
  3. Contradictions between pages or with sources? Fix them or record them in [open-points.md](open-points.md).
  4. Add an entry to [log.md](log.md).

## Fixed rules

- Installation is documented **only** for a fresh MainsailOS (no custom image, no KIAUH requirement).
- Users must never lose `variables.cfg` or the `#*# SAVE_CONFIG` block.
- Edit shared config files in `config/SV04-with-display` and copy them to `config/Sv04-works-with origin-klipper`.
