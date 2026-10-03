#!/usr/bin/env python3
"""
ULTRON PANEL V3 // PLATFORM ADAPTER
Compatibilidad base para Linux y Windows.
"""

import os
import platform
import shutil
import socket
import subprocess
import webbrowser
from pathlib import Path

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    psutil = None
    HAS_PSUTIL = False

SYSTEM = platform.system().lower()
IS_WINDOWS = SYSTEM == "windows"
IS_LINUX = SYSTEM == "linux"


def platform_name():
    if IS_WINDOWS:
        return "Windows"
    if IS_LINUX:
        return "Linux"
    return platform.system() or "Desconocido"


def run_command(command, timeout=20):
    try:
        result = subprocess.run(
            command,
            shell=isinstance(command, str),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        return (result.stdout or "").strip() or "Sin salida"
    except subprocess.TimeoutExpired:
        return "Tiempo de espera agotado"
    except Exception as exc:
        return f"No disponible: {exc}"


def hostname():
    try:
        return socket.gethostname()
    except Exception:
        return "ULTRON"


def local_ip():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
        finally:
            sock.close()
    except Exception:
        try:
            return socket.gethostbyname(hostname())
        except Exception:
            return "No disponible"


def system_info():
    lines = [
        f"Sistema: {platform.system()} {platform.release()}",
        f"Version: {platform.version()}",
        f"Arquitectura: {platform.machine()}",
        f"Equipo: {hostname()}",
        f"Procesador: {platform.processor() or 'No disponible'}",
    ]
    if HAS_PSUTIL:
        try:
            ram = psutil.virtual_memory()
            root = Path.home().anchor if IS_WINDOWS else "/"
            disk = psutil.disk_usage(root)
            lines += [
                f"CPU: {psutil.cpu_percent(interval=0.2):.0f}%",
                f"RAM: {ram.percent:.0f}% ({ram.used/1024**3:.1f} / {ram.total/1024**3:.1f} GB)",
                f"Disco: {disk.percent:.0f}% ({disk.used/1024**3:.1f} / {disk.total/1024**3:.1f} GB)",
            ]
        except Exception:
            pass
    return "\n".join(lines)


def network_info():
    if IS_WINDOWS:
        return f"IP local: {local_ip()}\n\nCONFIGURACION DE RED:\n{run_command(['ipconfig', '/all'], 25)}"
    if IS_LINUX:
        if shutil.which("nmcli"):
            devices = run_command(["nmcli", "device", "status"])
            general = run_command(["nmcli", "general"])
            return f"IP local: {local_ip()}\n\nDISPOSITIVOS:\n{devices}\n\nESTADO GENERAL:\n{general}"
        details = run_command(["ip", "addr"]) if shutil.which("ip") else "nmcli/ip no disponibles"
        return f"IP local: {local_ip()}\n\nRED:\n{details}"
    return f"IP local: {local_ip()}"


def open_ports():
    if IS_WINDOWS:
        return run_command(["netstat", "-ano"])
    if IS_LINUX and shutil.which("ss"):
        return run_command(["ss", "-tuln"])
    if IS_LINUX and shutil.which("netstat"):
        return run_command(["netstat", "-tuln"])
    return "No disponible"


def running_services():
    if IS_WINDOWS:
        return run_command([
            "powershell", "-NoProfile", "-Command",
            "Get-Service | Where-Object {$_.Status -eq 'Running'} | Select-Object -First 30 Status,Name,DisplayName | Format-Table -AutoSize"
        ], 25)
    if IS_LINUX and shutil.which("systemctl"):
        return run_command(["systemctl", "--type=service", "--state=running", "--no-pager"], 25)
    return "No disponible"


def security_info():
    return (
        f"SISTEMA:\n{platform.system()} {platform.release()}\n\n"
        f"PUERTOS / CONEXIONES:\n{open_ports()}\n\n"
        f"SERVICIOS ACTIVOS:\n{running_services()}"
    )


def disk_info():
    if HAS_PSUTIL:
        lines = []
        try:
            for part in psutil.disk_partitions(all=False):
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    lines.append(
                        f"{part.device}  {part.mountpoint}  "
                        f"{usage.percent:.0f}%  "
                        f"{usage.used/1024**3:.1f}/{usage.total/1024**3:.1f} GB"
                    )
                except (PermissionError, OSError):
                    pass
        except Exception:
            pass
        if lines:
            return "\n".join(lines)

    if IS_WINDOWS:
        return run_command([
            "powershell", "-NoProfile", "-Command",
            "Get-CimInstance Win32_LogicalDisk | Select-Object DeviceID,VolumeName,FileSystem,Size,FreeSpace | Format-Table -AutoSize"
        ])
    if IS_LINUX:
        return run_command(["df", "-h"])
    return "No disponible"


def process_info(limit=20):
    if HAS_PSUTIL:
        rows = []
        try:
            procs = []
            for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
                try:
                    procs.append(proc.info)
                except Exception:
                    pass
            procs.sort(key=lambda p: p.get("cpu_percent") or 0, reverse=True)
            for p in procs[:limit]:
                rows.append(
                    f"{p.get('pid', 0):>6}  {(p.get('cpu_percent') or 0):>5.1f}%  "
                    f"{(p.get('memory_percent') or 0):>5.1f}%  {p.get('name') or '?'}"
                )
            return "PID     CPU     RAM    PROCESO\n" + "\n".join(rows)
        except Exception:
            pass
    if IS_WINDOWS:
        return run_command(["tasklist"])
    if IS_LINUX:
        return run_command("ps aux --sort=-%cpu | head -21")
    return "No disponible"



def temperature_info():
    """Devuelve las temperaturas disponibles del equipo."""
    if HAS_PSUTIL:
        try:
            temps = psutil.sensors_temperatures()
            lines = []

            for chip, entries in temps.items():
                for entry in entries:
                    label = entry.label or chip
                    current = entry.current

                    if current is not None:
                        lines.append(f"{label}: {current:.1f} °C")

            if lines:
                return "TEMPERATURAS:\n" + "\n".join(lines)
        except Exception:
            pass

    if IS_LINUX and shutil.which("sensors"):
        return run_command(["sensors"])

    return "Temperatura no disponible en este sistema."


def battery_info():
    if not HAS_PSUTIL:
        return "psutil no instalado"
    try:
        batt = psutil.sensors_battery()
        if batt is None:
            return "Bateria no disponible"
        return f"Bateria: {batt.percent:.0f}%\nConectado a corriente: {'Si' if batt.power_plugged else 'No'}"
    except Exception:
        return "Bateria no disponible"


def open_url(url):
    try:
        return bool(webbrowser.open(url))
    except Exception:
        return False


def open_path(path):
    target = str(Path(path).expanduser())
    try:
        if IS_WINDOWS:
            os.startfile(target)
            return True
        if IS_LINUX and shutil.which("xdg-open"):
            subprocess.Popen(["xdg-open", target],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
            return True
    except Exception:
        pass
    return False


def open_terminal():
    try:
        if IS_WINDOWS:
            subprocess.Popen(["cmd.exe"])
            return True
        for terminal in ("x-terminal-emulator", "gnome-terminal", "konsole", "xfce4-terminal", "kitty", "alacritty"):
            if shutil.which(terminal):
                subprocess.Popen([terminal],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
                return True
    except Exception:
        pass
    return False


def open_app(app):
    name = app.strip().lower()

    urls = {
        "youtube": "https://www.youtube.com",
        "whatsapp": "https://web.whatsapp.com",
        "spotify": "https://open.spotify.com",
    }
    if name in urls:
        return open_url(urls[name])

    try:
        if IS_WINDOWS:
            apps = {
                "terminal": ["cmd.exe"],
                "cmd": ["cmd.exe"],
                "powershell": ["powershell.exe"],
                "explorer": ["explorer.exe"],
                "archivos": ["explorer.exe"],
                "notepad": ["notepad.exe"],
                "bloc de notas": ["notepad.exe"],
                "calculadora": ["calc.exe"],
            }
            cmd = apps.get(name)
            if cmd:
                subprocess.Popen(cmd)
                return True

        if IS_LINUX:
            if name in {"terminal", "consola"}:
                return open_terminal()
            if name == "archivos" and shutil.which("xdg-open"):
                subprocess.Popen(["xdg-open", str(Path.home())],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
                return True
    except Exception:
        pass

    return False


def platform_summary():
    return {
        "system": platform_name(),
        "is_windows": IS_WINDOWS,
        "is_linux": IS_LINUX,
        "hostname": hostname(),
        "local_ip": local_ip(),
        "python": platform.python_version(),
        "architecture": platform.machine(),
    }


if __name__ == "__main__":
    print("ULTRON // PLATFORM ADAPTER")
    print("=" * 40)
    for key, value in platform_summary().items():
        print(f"{key}: {value}")
