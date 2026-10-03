#!/usr/bin/env python3
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "gui" / "ultron.py"
BACKUP = ROOT / "gui" / "ultron.py.pre-v3-tools-backup"

if not TARGET.exists():
    raise SystemExit(f"No encontré: {TARGET}")

code = TARGET.read_text(encoding="utf-8")
if not BACKUP.exists():
    shutil.copy2(TARGET, BACKUP)

def replace_method(source, name, body):
    token = f"    def {name}("
    start = source.find(token)
    if start < 0:
        return source, False
    end = source.find("\n    def ", start + len(token))
    if end < 0:
        end = source.find('\n\nif __name__ == "__main__":', start)
    if end < 0:
        end = len(source)
    return source[:start] + body.strip("\n") + "\n" + source[end:], True

body = r"""    def _execute_ai_tool(self, response_text):
        # ULTRON V3: herramientas locales mediante SystemBridge.
        text = response_text.strip()
        if not text.startswith("TOOL:"):
            return None

        parts = text.split(":", 2)
        tool = parts[1].strip() if len(parts) > 1 else ""
        arg = parts[2].strip() if len(parts) > 2 else ""

        try:
            if tool == "get_local_ip":
                data = self.system.summary()
                ip = data.get("local_ip", "No disponible")
                return f"Tu IP local es {ip}."

            if tool == "get_public_ip":
                req = urllib.request.Request(
                    "https://api.ipify.org",
                    headers={"User-Agent": "ULTRON-Core/3.0"}
                )
                with urllib.request.urlopen(req, timeout=8) as r:
                    ip = r.read().decode().strip()
                return f"IP pública: {ip}"

            if tool == "get_wifi_name":
                # La información de red ya se resuelve según el SO.
                info = self.system.network_module()
                return "Información de red:\n" + info

            if tool == "get_memory":
                # system_module usa psutil y funciona en Linux/Windows.
                return self.system.system_module()

            if tool == "get_disk":
                return self.system.files_module()

            if tool == "get_battery":
                return self.system.battery_module()

            if tool == "get_system_info":
                data = self.system.summary()
                return (
                    f"Equipo: {data.get('hostname', 'ULTRON')}. "
                    f"Sistema: {data.get('system', 'No disponible')}. "
                    f"Arquitectura: {data.get('architecture', 'No disponible')}. "
                    f"Python: {data.get('python', 'No disponible')}."
                )

            if tool == "open_url":
                if not arg.startswith(("https://", "http://")):
                    return "URL rechazada: solo se permiten direcciones http/https."
                if self.system.open_url(arg):
                    return f"Abrí {arg}"
                return f"No pude abrir {arg}"

            if tool == "open_app":
                key = arg.lower().strip()

                # Alias comunes para que el mismo comando sirva en ambos SO.
                aliases = {
                    "files": "archivos",
                    "file manager": "archivos",
                    "explorer": "archivos",
                    "consola": "terminal",
                    "cmd": "terminal",
                }
                key = aliases.get(key, key)

                if self.system.open_app(key):
                    return f"Abrí {arg}."

                return (
                    f"La aplicación '{arg}' no está disponible "
                    f"o todavía no está en la lista permitida para "
                    f"{self.system.os_name()}."
                )

            return f"Herramienta no permitida: {tool}"

        except Exception as exc:
            return f"No pude ejecutar {tool}: {exc}"
"""

code, ok = replace_method(code, "_execute_ai_tool", body)
if not ok:
    raise SystemExit("No encontré _execute_ai_tool; no se modificó el archivo.")

TARGET.write_text(code, encoding="utf-8")

print("ULTRON V3 // MULTIPLATFORM AI TOOLS")
print("=" * 46)
print("Actualizado:", TARGET)
print("Backup:", BACKUP)
print()
print("Prueba:")
print("  python3 -m gui.ultron")
