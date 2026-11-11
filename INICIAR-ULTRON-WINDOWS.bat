@echo off
cd /d "%~dp0"
set PYTHONUTF8=1
set "PATH=%~dp0.venv\Scripts;%PATH%"
start "" ".venv\Scripts\pythonw.exe" launcher.py
