# Bambu Studio ↔ Mainsail

2026-11-26:

- `strings bambu-studio` (Bambu Studio 2.7.1.62, Flatpak): keys `print_host`, `print_host_webui`,
  `printhost_apikey`, `printhost_port`, `printhost_authorization_type`, `host_type`. Host types include
  `octoprint`, `prusalink`, `duet`, `flashair`, `astrobox`, `repetier`, `klipper`. UI texts
  "Hostname, IP or URL", **"Device UI"**, "Device Page".
- MainsailOS `modules/generic/files/moonraker.conf` (GitHub, develop): sections `[server]`,
  `[file_manager]`, `[authorization]`, **`[octoprint_compat]`**, `[history]`, `[announcements]`,
  `[update_manager …]`.
- Not tested in the GUI: whether the Device tab really embeds Mainsail (expected from "Device UI" /
  `print_host_webui`, as in OrcaSlicer).
