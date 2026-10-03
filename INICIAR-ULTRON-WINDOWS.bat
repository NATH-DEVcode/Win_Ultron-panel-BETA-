@echo off
cd /d "%~dp0"
set PYTHONUTF8=1
set "PATH=%~dp0.venv\Scripts;%PATH%"
for /f "tokens=2,*" %%A in ('reg query HKCU\Environment /v GROQ_API_KEY 2^>nul ^| find "GROQ_API_KEY"') do set "GROQ_API_KEY=%%B"
start "" ".venv\Scripts\pythonw.exe" -m gui.ultron
