@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title ULTRON PANEL - Instalador
echo.
echo ==========================================
echo       ULTRON PANEL - INSTALACION
echo ==========================================
echo.

set "PYEXE="
where py >nul 2>nul && set "PYEXE=py -3.13"
if not defined PYEXE (
  where python >nul 2>nul && set "PYEXE=python"
)
if not defined PYEXE (
  echo [1/5] Instalando Python...
  where winget >nul 2>nul || goto :no_winget
  winget install -e --id Python.Python.3.13 --accept-source-agreements --accept-package-agreements
  set "PYEXE=%LocalAppData%\Programs\Python\Python313\python.exe"
) else (
  echo [1/5] Python encontrado.
)

echo [2/5] Creando entorno ligero...
if not exist ".venv\Scripts\python.exe" %PYEXE% -m venv .venv
if errorlevel 1 goto :fail

echo [3/5] Instalando dependencias de ULTRON...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check --upgrade pip
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements-windows.txt
if errorlevel 1 goto :fail

echo [4/5] Comprobando FFmpeg...
where ffmpeg >nul 2>nul
if errorlevel 1 (
  where winget >nul 2>nul || goto :no_winget
  winget install -e --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements
) else (
  echo FFmpeg ya esta instalado.
)

echo [5/5] Creando lanzador...
> "INICIAR-ULTRON-WINDOWS.bat" echo @echo off
>>"INICIAR-ULTRON-WINDOWS.bat" echo cd /d "%%~dp0"
>>"INICIAR-ULTRON-WINDOWS.bat" echo set "PATH=%%LocalAppData%%\Microsoft\WinGet\Links;%%PATH%%"
>>"INICIAR-ULTRON-WINDOWS.bat" echo ".venv\Scripts\pythonw.exe" -m gui.ultron

echo.
echo ==========================================
echo  ULTRON LISTO. Ejecuta:
echo  INICIAR-ULTRON-WINDOWS.bat
echo ==========================================
pause
exit /b 0

:no_winget
echo ERROR: Windows Package Manager ^(winget^) no esta disponible.
goto :fail

:fail
echo.
echo La instalacion no termino correctamente.
pause
exit /b 1
