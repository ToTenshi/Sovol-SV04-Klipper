@echo off
rem Installs the Sovol SV04 slicer profiles (Bambu Studio, Cura, PrusaSlicer) - double-click me
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-slicer-profiles.ps1" %*
pause
