<#
  Install the Sovol SV04 Klipper slicer profiles on Windows.
  Installiert die SV04-Slicer-Profile unter Windows.

  Easiest: double-click install-slicer-profiles-windows.cmd
  Or:      powershell -ExecutionPolicy Bypass -File install-slicer-profiles.ps1 [-PrinterHost 192.168.1.50] [bambu] [cura] [prusa]

  Supported: Bambu Studio, Cura 4/5, PrusaSlicer. Close the slicers before running.
  Works with Windows PowerShell 5.1 (preinstalled) and PowerShell 7.
#>
param(
    [string]$PrinterHost = 'sv04.local',
    [Parameter(ValueFromRemainingArguments = $true)][string[]]$Only
)

$ErrorActionPreference = 'Stop'
if (-not $Only -or $Only.Count -eq 0) { $Only = @('bambu', 'cura', 'prusa') }
$Repo = Split-Path -Parent $PSScriptRoot
$AppData = $env:APPDATA
$Utf8 = New-Object System.Text.UTF8Encoding $false   # UTF-8 without BOM
$script:Installed = 0

function Test-Running([string[]]$Names) {
    foreach ($n in $Names) {
        if (Get-Process -Name $n -ErrorAction SilentlyContinue) { return $true }
    }
    return $false
}

function New-Dir([string]$Path) {
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
}

# ------------------------------------------------------------ Bambu Studio --
function Install-Bambu {
    $base = Join-Path $AppData 'BambuStudio'
    if (-not (Test-Path $base)) { Write-Host 'Bambu Studio: not found (start it once, then run again)'; return }
    if (Test-Running @('bambu-studio', 'BambuStudio')) {
        Write-Warning 'Bambu Studio is running - close it and run the script again (skipped)'; return
    }
    $src = Join-Path $Repo 'Bambu Studio Profile'
    New-Dir (Join-Path $base 'sv04')
    New-Dir (Join-Path $base 'user\default')
    $stl = Join-Path $base 'sv04\SV04.stl'
    Copy-Item -LiteralPath (Join-Path $src 'bed\SV04.stl') -Destination $stl -Force
    $stlJson = $stl -replace '\\', '/'
    foreach ($user in Get-ChildItem -LiteralPath (Join-Path $base 'user') -Directory) {
        Write-Host "Bambu Studio -> $($user.FullName)"
        foreach ($kind in @('machine', 'process', 'filament')) {
            $dst = Join-Path $user.FullName $kind
            New-Dir $dst
            foreach ($f in Get-ChildItem -LiteralPath (Join-Path $src $kind) -Filter '*.json') {
                Copy-Item -LiteralPath $f.FullName -Destination (Join-Path $dst $f.Name) -Force
            }
        }
        # printer address for upload / Mainsail page in the "Device" tab; bed model for 300 mm presets
        foreach ($f in Get-ChildItem -LiteralPath (Join-Path $user.FullName 'machine') -Filter 'Sovol SV04 Klipper *.json') {
            $text = [System.IO.File]::ReadAllText($f.FullName).Replace('sv04.local', $PrinterHost)
            [System.IO.File]::WriteAllText($f.FullName, $text, $Utf8)
            if ($text.Contains('"300x0"') -and -not $text.Contains('"bed_custom_model"')) {
                $text = '{' + "`n" + '    "bed_custom_model": "' + $stlJson + '",' + $text.Substring($text.IndexOf('{') + 1)
                [System.IO.File]::WriteAllText($f.FullName, $text, $Utf8)
            }
        }
    }
    $script:Installed++
}

# -------------------------------------------------------------------- Cura --
function Install-Cura {
    $base = Join-Path $AppData 'cura'
    $versions = @()
    if (Test-Path $base) { $versions = @(Get-ChildItem -LiteralPath $base -Directory | Where-Object { $_.Name -match '^\d+\.\d+$' }) }
    if ($versions.Count -eq 0) { Write-Host 'Cura: not found (start it once, then run again)'; return }
    if (Test-Running @('UltiMaker-Cura', 'Ultimaker-Cura', 'Cura')) {
        Write-Warning 'Cura is running - close it and run the script again (skipped)'; return
    }
    $src = Join-Path $Repo 'Cura Profile'
    foreach ($ver in $versions) {
        Write-Host "Cura -> $($ver.FullName)"
        foreach ($pair in @(@('definitions', '*.def.json'), @('extruders', '*.def.json'), @('meshes', '*'))) {
            $dst = Join-Path $ver.FullName $pair[0]
            New-Dir $dst
            foreach ($f in Get-ChildItem -LiteralPath (Join-Path $src $pair[0]) -Filter $pair[1] -File) {
                Copy-Item -LiteralPath $f.FullName -Destination (Join-Path $dst $f.Name) -Force
            }
        }
        New-Dir (Join-Path $ver.FullName 'scripts')
        Copy-Item -LiteralPath (Join-Path $src 'MeshPrintSize.py') -Destination (Join-Path $ver.FullName 'scripts\MeshPrintSize.py') -Force
        $script:Installed++
    }
}

# ------------------------------------------------------------- PrusaSlicer --
# Splits the config bundle into single user presets (printer/print/filament).
function Install-Prusa {
    $base = Join-Path $AppData 'PrusaSlicer'
    if (-not (Test-Path $base)) { Write-Host 'PrusaSlicer: not found (start it once, then run again)'; return }
    if (Test-Running @('prusa-slicer', 'PrusaSlicer')) {
        Write-Warning 'PrusaSlicer is running - close it and run the script again (skipped)'; return
    }
    $src = Join-Path $Repo 'Prusaslicer Profile'
    Write-Host "PrusaSlicer -> $base"
    foreach ($kind in @('printer', 'print', 'filament', 'sv04')) { New-Dir (Join-Path $base $kind) }
    $stl = Join-Path $base 'sv04\SV04.STL'
    Copy-Item -LiteralPath (Join-Path $src 'SV04\SV04.STL') -Destination $stl -Force
    $model = $stl -replace '\\', '/'

    $out = $null
    $buffer = New-Object System.Collections.Generic.List[string]
    $flush = {
        if ($out) { [System.IO.File]::WriteAllText($out, (($buffer -join "`n") + "`n"), $Utf8) }
    }
    foreach ($line in [System.IO.File]::ReadAllLines((Join-Path $src 'PrusaSlicer_config_bundle_SV04_Klipper.ini'))) {
        if ($line -match '^\[(printer|print|filament):(.+)\]$') {
            & $flush
            $out = Join-Path (Join-Path $base $Matches[1]) ($Matches[2] + '.ini')
            $buffer.Clear()
            $buffer.Add('# generated by the SV04 installer from PrusaSlicer_config_bundle_SV04_Klipper.ini')
        }
        elseif ($line.StartsWith('[')) {
            & $flush
            $out = $null
            $buffer.Clear()
        }
        elseif ($out) {
            if ($line -match '^bed_custom_model = .') { $line = 'bed_custom_model = ' + $model }
            if ($out -like '*\printer\*' -and $line.StartsWith('print_host = ')) { $line = 'print_host = ' + $PrinterHost }
            $buffer.Add($line)
        }
    }
    & $flush
    $script:Installed++
}

if ($Only -contains 'bambu') { Install-Bambu }
if ($Only -contains 'cura')  { Install-Cura }
if ($Only -contains 'prusa') { Install-Prusa }

Write-Host ''
if ($script:Installed -gt 0) {
    Write-Host "Done ($($script:Installed) target(s)). Start the slicer and choose a 'SV04' printer."
    Write-Host "Printer address for upload / Mainsail: $PrinterHost (change with -PrinterHost)"
} else {
    Write-Host 'Nothing installed - no supported slicer found.'
    exit 1
}
