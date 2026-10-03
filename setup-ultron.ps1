$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
function Find-Python {
  $p = Join-Path $env:LOCALAPPDATA "Programs\Python\Python313\python.exe"
  if (Test-Path $p) { return $p }
  $cmd = Get-Command python -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  return $null
}
$python = Find-Python
if (-not $python) {
  if (-not (Get-Command winget -ErrorAction SilentlyContinue)) { throw "winget no disponible para instalar Python." }
  winget install -e --id Python.Python.3.13 --scope user --accept-source-agreements --accept-package-agreements --silent
  $python = Find-Python
  if (-not $python) { throw "Python no quedo disponible despues de instalarlo." }
}
if (-not (Test-Path ".venv\Scripts\python.exe")) { & $python -m venv .venv }
& ".venv\Scripts\python.exe" -m pip install --disable-pip-version-check --upgrade pip
& ".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements-windows.txt
if ($LASTEXITCODE -ne 0) { throw "No se pudieron instalar las dependencias de ULTRON." }
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
  if (-not (Get-Command winget -ErrorAction SilentlyContinue)) { throw "FFmpeg no esta instalado y winget no esta disponible." }
  winget install -e --id Gyan.FFmpeg --scope user --accept-source-agreements --accept-package-agreements --silent
}
Write-Host "ULTRON configurado correctamente."
