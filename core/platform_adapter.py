#!/usr/bin/env python3
"""
ULTRON PANEL V3 // PLATFORM ADAPTER
Compatibilidad base para Linux y Windows.
"""

import os
import platform
import re
import shutil
import shlex
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
        if isinstance(command, str):
            command = shlex.split(command, posix=not IS_WINDOWS)
        process_options = {}
        if IS_WINDOWS:
            # Las consultas automáticas (ping, netsh, etc.) no deben abrir
            # una ventana de consola encima de ULTRON.
            process_options["creationflags"] = getattr(
                subprocess, "CREATE_NO_WINDOW", 0x08000000
            )
        result = subprocess.run(
            command,
            shell=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
            **process_options,
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


def _connected_wifi_name():
    if IS_WINDOWS:
        output = run_command(["netsh", "wlan", "show", "interfaces"], timeout=8)
        for line in output.splitlines():
            label, separator, value = line.partition(":")
            if separator and label.strip().casefold() == "ssid":
                return value.strip()
    elif IS_LINUX:
        if shutil.which("iwgetid"):
            name = run_command(["iwgetid", "-r"], timeout=5)
            if name and not name.startswith("No disponible"):
                return name
        if shutil.which("nmcli"):
            output = run_command(
                ["nmcli", "-t", "-f", "ACTIVE,SSID", "device", "wifi"],
                timeout=8,
            )
            for line in output.splitlines():
                if line.startswith("yes:"):
                    return line[4:].replace("\\:", ":")
    return ""


def network_info():
    if not HAS_PSUTIL:
        return (
            "No pude resumir la conexión porque falta el componente de "
            "información del sistema (psutil)."
        )

    try:
        addresses = psutil.net_if_addrs()
        statuses = psutil.net_if_stats()
    except Exception:
        return "No pude consultar el estado de las conexiones de red."

    connected = []
    for name, status in statuses.items():
        folded = name.casefold()
        if not status.isup or folded in {"lo", "loopback"}:
            continue
        ipv4 = next(
            (
                address.address
                for address in addresses.get(name, [])
                if address.family == socket.AF_INET
                and not address.address.startswith(("127.", "169.254."))
            ),
            None,
        )
        if ipv4:
            connected.append((name, ipv4))

    if not connected:
        return (
            "ESTADO: Sin conexión local activa\n\n"
            "No encontré una conexión Wi-Fi o Ethernet con dirección de red. "
            "Revisa que el Wi-Fi esté encendido o que el cable esté conectado."
        )

    lines = ["ESTADO: Conectado a una red local"]
    for name, address in connected[:5]:
        folded = name.casefold()
        if any(token in folded for token in ("wi-fi", "wifi", "wlan", "wireless")):
            kind = "Wi-Fi"
        elif any(token in folded for token in ("ethernet", "eth", "enp", "eno")):
            kind = "Ethernet"
        else:
            kind = "Red"
        lines.extend((f"\n{kind}: {name}", f"Dirección local: {address}"))
        if kind == "Wi-Fi":
            wifi_name = _connected_wifi_name()
            if wifi_name:
                lines.append(f"Red Wi-Fi: {wifi_name}")
    lines.append(
        "\nLa dirección local identifica este equipo dentro de tu red."
    )
    return "\n".join(lines)


def network_snapshot():
    """Obtiene IP, tipo de enlace, nombre Wi-Fi y latencia en una sola consulta."""
    interfaces = []
    if HAS_PSUTIL:
        try:
            addresses = psutil.net_if_addrs()
            statuses = psutil.net_if_stats()
            for name, status in statuses.items():
                folded = name.casefold()
                if not status.isup or folded in {"lo", "lo0", "loopback"}:
                    continue
                ipv4 = next((
                    address.address
                    for address in addresses.get(name, [])
                    if address.family == socket.AF_INET
                    and not address.address.startswith(("127.", "169.254."))
                ), None)
                if not ipv4:
                    continue
                if any(tag in folded for tag in ("wi-fi", "wifi", "wlan", "wireless")):
                    kind = "Wi-Fi"
                elif any(tag in folded for tag in ("ethernet", "eth", "enp", "eno")):
                    kind = "Cable"
                else:
                    kind = "Red local"
                interfaces.append({"type": kind, "ip": ipv4})
        except Exception:
            pass

    wifi_name = _connected_wifi_name() if any(
        item["type"] == "Wi-Fi" for item in interfaces
    ) else ""

    ping_command = (
        ["ping", "-n", "1", "-w", "1000", "1.1.1.1"]
        if IS_WINDOWS
        else ["ping", "-c", "1", "-W", "1", "1.1.1.1"]
    )
    ping_output = run_command(ping_command, timeout=2)
    match = re.search(r"(?:time|tiempo)\s*[=<]\s*([\d.,]+)\s*ms", ping_output, re.IGNORECASE)
    if match:
        latency = match.group(1).replace(",", ".")
        ping = f"<{latency} ms" if "<" in match.group(0) else f"{latency} ms"
    else:
        ping = "Sin respuesta"

    return {"interfaces": interfaces, "wifi_name": wifi_name, "ping": ping}


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
        disks = []
        seen = set()
        try:
            for part in psutil.disk_partitions(all=False):
                mount = part.mountpoint
                folded_mount = mount.casefold()
                if (
                    folded_mount in seen
                    or any(folded_mount.startswith(path) for path in ("/proc", "/sys", "/dev", "/run"))
                    or part.fstype.casefold() in {"squashfs", "tmpfs", "devtmpfs", "overlay"}
                ):
                    continue
                try:
                    usage = psutil.disk_usage(mount)
                except (PermissionError, OSError):
                    continue
                if usage.total <= 0:
                    continue
                seen.add(folded_mount)
                if IS_WINDOWS:
                    name = f"Disco {mount.rstrip(':/')}"
                elif mount == "/":
                    name = "Disco del sistema"
                elif mount == str(Path.home()):
                    name = "Carpeta personal"
                else:
                    name = f"Unidad {mount}"
                free_gb = usage.free / 1024**3
                total_gb = usage.total / 1024**3
                disks.append(
                    f"{name}\n"
                    f"  {free_gb:.1f} GB libres de {total_gb:.1f} GB "
                    f"({usage.percent:.0f}% usado)"
                )
        except Exception:
            return "No pude consultar el espacio de almacenamiento."
        if disks:
            return (
                "ESPACIO DE ALMACENAMIENTO\n\n"
                + "\n\n".join(disks[:8])
                + "\n\nEl porcentaje indica cuánto espacio está ocupado."
            )
    return "No pude consultar el espacio de almacenamiento en este equipo."


def installed_programs(limit=40):
    """List installed apps with a short, human-readable description."""
    programs = []

    if IS_WINDOWS:
        try:
            import winreg

            uninstall_paths = (
                r"Software\Microsoft\Windows\CurrentVersion\Uninstall",
                r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
            )
            for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
                for path in uninstall_paths:
                    try:
                        root = winreg.OpenKey(hive, path, 0, winreg.KEY_READ)
                    except OSError:
                        continue
                    with root:
                        count = winreg.QueryInfoKey(root)[0]
                        for index in range(count):
                            try:
                                subkey_name = winreg.EnumKey(root, index)
                                with winreg.OpenKey(root, subkey_name) as subkey:
                                    name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                    if not isinstance(name, str) or not name.strip():
                                        continue
                                    try:
                                        if winreg.QueryValueEx(subkey, "SystemComponent")[0]:
                                            continue
                                    except OSError:
                                        pass
                                    try:
                                        version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                                    except OSError:
                                        version = ""
                                    try:
                                        publisher = winreg.QueryValueEx(subkey, "Publisher")[0]
                                    except OSError:
                                        publisher = ""
                                    try:
                                        description = winreg.QueryValueEx(subkey, "Comments")[0]
                                    except OSError:
                                        description = ""
                                    programs.append(
                                        (name.strip(), version, description, publisher)
                                    )
                            except OSError:
                                continue
        except (ImportError, OSError):
            return "No pude leer la lista de programas instalados."
    elif IS_LINUX and shutil.which("dpkg-query"):
        output = run_command(
            ["dpkg-query", "-W", "-f=${binary:Package}\\t${Version}\\t${binary:Summary}\\n"],
            timeout=30,
        )
        if output.startswith(("No disponible:", "Tiempo de espera agotado")):
            return "No pude leer la lista de programas instalados."
        for line in output.splitlines():
            name, _, details = line.partition("\t")
            version, _, summary = details.partition("\t")
            if name and name != "Sin salida":
                programs.append((name, version, summary, ""))
    elif IS_LINUX and shutil.which("rpm"):
        output = run_command(
            ["rpm", "-qa", "--qf", "%{NAME}\\t%{VERSION}\\t%{SUMMARY}\\n"],
            timeout=30,
        )
        if output.startswith(("No disponible:", "Tiempo de espera agotado")):
            return "No pude leer la lista de programas instalados."
        for line in output.splitlines():
            name, _, details = line.partition("\t")
            version, _, summary = details.partition("\t")
            if name and name != "Sin salida":
                programs.append((name, version, summary, ""))
    elif IS_LINUX and shutil.which("pacman"):
        output = run_command(["pacman", "-Q"], timeout=30)
        if output.startswith(("No disponible:", "Tiempo de espera agotado")):
            return "No pude leer la lista de programas instalados."
        for line in output.splitlines():
            name, _, version = line.partition(" ")
            if name and name != "Sin salida":
                programs.append((name, version, "Paquete instalado", ""))

    unique = {}
    for name, version, description, publisher in programs:
        unique.setdefault(name.casefold(), (name, version, description, publisher))
    rows = sorted(unique.values(), key=lambda item: item[0].casefold())
    if not rows:
        return "No pude encontrar programas instalados en este equipo."

    lines = [f"PROGRAMAS INSTALADOS ({len(rows)})", ""]
    for name, version, description, publisher in rows[:limit]:
        lines.append(f"• {name}")
        if version:
            lines.append(f"  Versión: {version}")
        if description:
            readable_description = " ".join(str(description).split())
            lines.append(f"  {readable_description[:150]}")
        if publisher:
            lines.append(f"  Editor: {publisher}")
    if len(rows) > limit:
        lines.extend(("", f"Se muestran {limit} de {len(rows)}. Usa Buscar para localizar uno."))
    return "\n".join(lines)


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
        return run_command(["ps", "-eo", "pid,comm,%cpu", "--sort=-%cpu"])
    return "No disponible"



def cpu_temperature_c():
    """Devuelve una lectura etiquetada explícitamente como temperatura de CPU."""
    if not HAS_PSUTIL:
        return None
    try:
        temps = psutil.sensors_temperatures()
    except Exception:
        return None

    cpu_hints = ("cpu", "package", "processor", "tctl", "tdie", "coretemp")
    readings = []
    for chip, entries in (temps or {}).items():
        chip_name = str(chip).casefold()
        for entry in entries or []:
            label = str(entry.label or "").casefold()
            if entry.current is None:
                continue
            if any(hint in chip_name or hint in label for hint in cpu_hints):
                readings.append(float(entry.current))
    return max(readings) if readings else None


def temperature_info():
    """Devuelve la temperatura de CPU o N/A si Windows no expone el sensor."""
    temperature = cpu_temperature_c()
    if temperature is None:
        return "Temperatura de CPU: N/A"
    return f"Temperatura de CPU: {temperature:.1f} °C"


def battery_status():
    """Devuelve un snapshot seguro de batería, incluido tiempo restante estimado."""
    if not HAS_PSUTIL:
        return None
    try:
        battery = psutil.sensors_battery()
        if battery is None:
            return None
        seconds_left = battery.secsleft
        percent = float(battery.percent)
        plugged = bool(battery.power_plugged)
    except Exception:
        return None

    unknown_time = getattr(psutil, "POWER_TIME_UNKNOWN", -1)
    unlimited_time = getattr(psutil, "POWER_TIME_UNLIMITED", -2)
    if seconds_left in (unknown_time, unlimited_time):
        seconds_left = None
    elif seconds_left is not None and seconds_left < 0:
        seconds_left = None

    return {
        "percent": percent,
        "plugged": plugged,
        "charging": plugged and percent < 100.0,
        "seconds_left": seconds_left,
    }


def battery_info():
    status = battery_status()
    if status is None:
        return "Batería: N/A"
    charging = "Sí" if status["charging"] else "No"
    plugged = "Sí" if status["plugged"] else "No"
    remaining = status["seconds_left"]
    if remaining is None:
        estimate = "N/A"
    else:
        hours, seconds = divmod(int(remaining), 3600)
        minutes = seconds // 60
        estimate = f"{hours} h {minutes} min"
    return (
        f"Batería: {status['percent']:.0f}%\n"
        f"Cargando: {charging}\n"
        f"Conectada a corriente: {plugged}\n"
        f"Tiempo restante estimado: {estimate}"
    )


def open_url(url):
    try:
        if IS_WINDOWS:
            os.startfile(url)
            return True
        if re.match(r"^[a-z][a-z0-9+.-]*:", str(url), re.IGNORECASE):
            if IS_LINUX and shutil.which("xdg-open"):
                subprocess.Popen(
                    ["xdg-open", str(url)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
                return True
            return False
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
