# Open points

| Item | Status |
|------|--------|
| Dual tool change in Bambu Studio | Not tested in the GUI/on hardware (CLI can't do two filaments) |
| Windows installer (`install-slicer-profiles.ps1`) | Written for PS 5.1, not executed (no PowerShell available) |
| How did the fork get onto the test Pi? | Unclear (old image or an earlier `display` run). Clarify with the user |
| `sv04-pi-setup.sh` on a real MainsailOS | Tested in a mock environment; the real Kconfig run (`olddefconfig`) is only verified by the script itself |
| Fork (January 2024) on a brand-new MainsailOS | Python compatibility unchecked |
| Clone URL in the READMEs | Points to `ToTenshi/Sovol-SV04-Klipper` branch `sv04-bambu-calibration`. Adjust after merging into main/upstream |
| Input shaper preset | Estimated (no SV04 measurements found). Real measurements welcome as `sources/` |
| Macro simulator | Z offset part is in the repo (`tools/simulate_z_offset.py`), IDEX/shaper scenarios not yet |
| Mainsail *Reset* while T1 is active | Also deletes the T1 share (see offsets) |
| Discord link | May expire, only the maintainer can create a permanent one |
| Bed screw positions | `[screws_tilt_adjust]` (probe over 31/0, 270/0, 270/240, 31/240) doesn't match `[bed_screws]` (nozzle over 25/35, 295/35, 295/295, 25/295). Check on the printer with `BED_SCREWS_CHECK` |
| Mainsail in the Bambu Device tab | Keys are set, not checked in the GUI |
| Load cell (automatic Z offset) | Hardware idea, see [hardware-ideas](hardware-ideas.md) |
| Licence | The original repo has no licence. Clarify with Bully85 before publishing standalone |
