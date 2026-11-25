# Install Profile PrusaSlicer

## Automatic (recommended)

Close PrusaSlicer, then double-click `install/install-slicer-profiles-windows.cmd` (Windows) or run
`./install/install-slicer-profiles.sh prusa` (macOS/Linux, also Flatpak). The script splits the
bundle into single user presets and sets the bed model path for your system. No import is needed.

## Copy and import

- First copy the folder "SV04" in the Folder path:

```sh
C:\Program Files\Prusa3D\PrusaSlicer\resources\profiles
```

- than import the "PrusaSlicer_config_bundle_SV04_Klipper.ini" in PrusaSlicer

- The printer presets upload to `sv04.local` (OctoPrint API from Moonraker, no API key). For another
  address, use `--host 192.168.1.50` with the installer, or change it under *Printer Settings → Physical printer*.
- Linux/macOS: the bed model path in the profiles points to the Windows folder above. Set it in
  *Printer Settings → General → Bed shape → Model* to `SV04/SV04.STL`, or leave it empty (only cosmetic).
- COPY and MIRROR are limited to a 150 mm wide print area (left half of the bed), so the nozzles
  can't collide. `START_PRINT` extends the bed mesh to the second copy automatically.

## Use

- if you print in dual mode and dont use the other extruder select "NONE" Filament for the not used Extruder

- for the connection with klipper go to printer settings an clic the cog wheel.

![PrusaSV04](img/Prusa_connection_Sv04.PNG)



