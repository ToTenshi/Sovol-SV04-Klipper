# Install the Cura profiles (Cura 4.x and 5.x)

**Recommended:** copy the files into your Cura **user folder**. This works for every Cura 5 version
and survives Cura updates. Replace `5.x` with your version, e.g. `5.8` (Cura 4: e.g. `4.13`):

| Repo folder | Windows | Linux |
|-------------|---------|-------|
| `definitions/*.def.json` | `%APPDATA%\cura\5.x\definitions` | `~/.local/share/cura/5.x/definitions` |
| `extruders/*.def.json` | `%APPDATA%\cura\5.x\extruders` | `~/.local/share/cura/5.x/extruders` |
| `meshes/SV04.STL` | `%APPDATA%\cura\5.x\meshes` | `~/.local/share/cura/5.x/meshes` |
| `MeshPrintSize.py` | `%APPDATA%\cura\5.x\scripts` | `~/.local/share/cura/5.x/scripts` |

Create missing folders. The installer does all of this automatically: `install/install-slicer-profiles-windows.cmd`
(Windows) or `./install/install-slicer-profiles.sh cura` (macOS/Linux, also Flatpak). macOS folder:
`~/Library/Application Support/cura/5.x/`.
Restart Cura afterwards.

COPY and MIRROR are limited to a 150 mm wide print area (left half of the bed), so the
nozzles can't collide. `START_PRINT` extends the bed mesh to the second copy automatically.

## Alternative: program folder (old method)


```sh
C:\Program Files\Ultimaker Cura 4.12.1\resources\definitions
```
```sh
C:\Program Files\Ultimaker Cura 4.12.1\resources\extruders
```
```sh
C:\Program Files\Ultimaker Cura 4.12.1\resources\meshes
```
## Path change version 5

```sh
C:\Program Files\Ultimaker Cura 5.1.0\share\cura\resources\definitions
```
```sh
C:\Program Files\Ultimaker Cura 5.1.0\share\cura\resources\extruders
```
```sh
C:\Program Files\Ultimaker Cura 5.1.0\share\cura\resources\meshes
```

## add Bed Mesh printarea

paste the file "MeshPrintSize.py" to the folder Script. Look photos

![pic1SV04](img/Unbenannt1.PNG)
![pic2SV04](img/Unbenannt2.PNG)
![pic3SV04](img/Unbenannt3.PNG)
![pic4SV04](img/Unbenannt4.PNG)

- reboot Cura

![pic5SV04](img/Unbenannt5.PNG)
![pic6SV04](img/Unbenannt6.PNG)
![pic7SV04](img/Unbenannt7.PNG)
![pic8SV04](img/Unbenannt8.PNG)
![pic9SV04](img/Unbenannt9.PNG)