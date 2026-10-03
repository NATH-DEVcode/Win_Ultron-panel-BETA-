#!/usr/bin/env python3
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "gui" / "ultron.py"
BACKUP = ROOT / "gui" / "ultron.py.v2-backup"

if not TARGET.exists():
    raise SystemExit(f"No encontré: {TARGET}")

code = TARGET.read_text(encoding="utf-8")

# 1) Importar bridge.
bridge_import = "from core.system_bridge import create_bridge\n"
if bridge_import not in code:
    marker = "try:\n    import psutil"
    if marker in code:
        code = code.replace(marker, bridge_import + "\n" + marker, 1)
    elif "import subprocess\n" in code:
        code = code.replace(
            "import subprocess\n",
            "import subprocess\n" + bridge_import,
            1
        )
    else:
        raise SystemExit("No pude localizar la zona de imports.")

# Path para métricas Windows.
if "from pathlib import Path\n" not in code:
    marker = "import subprocess\n"
    if marker in code:
        code = code.replace(marker, marker + "from pathlib import Path\n", 1)

# 2) Crear bridge.
if "self.system = create_bridge()" not in code:
    marker = "        self.root = root\n"
    if marker not in code:
        raise SystemExit("No encontré UltronGUI.__init__")
    code = code.replace(
        marker,
        marker + "        self.system = create_bridge()\n",
        1
    )

code = code.replace(
    'self.root.title("ULTRON // CORE")',
    'self.root.title(f"ULTRON // CORE — {self.system.os_name()}")',
    1
)

def replace_method(source, name, body):
    start = source.find(f"    def {name}(")
    if start < 0:
        return source, False
    end = source.find("\n    def ", start + 8)
    if end < 0:
        end = source.find('\n\nif __name__ == "__main__":', start)
    if end < 0:
        end = len(source)
    return source[:start] + body.strip("\n") + "\n" + source[end:], True

methods = {
    "_on_system": '''    def _on_system(self):
        self._add_log(f"Module SISTEMA selected [{self.system.os_name()}]")
        self._show_module("SISTEMA", self.system.system_module())
''',
    "_on_network": '''    def _on_network(self):
        self._add_log(f"Module RED selected [{self.system.os_name()}]")
        self._show_module("RED", self.system.network_module())
''',
    "_on_security": '''    def _on_security(self):
        self._add_log(f"Module SEGURIDAD selected [{self.system.os_name()}]")
        self._show_module("SEGURIDAD", self.system.security_module())
''',
    "_on_files": '''    def _on_files(self):
        self._add_log(f"Module ARCHIVOS selected [{self.system.os_name()}]")
        self._show_module("ARCHIVOS", self.system.files_module())
''',
    "_on_diagnostics": '''    def _on_diagnostics(self):
        self._add_log(f"Module DIAGNOSTICO selected [{self.system.os_name()}]")
        info = (
            self.system.diagnostics()
            + "\\n\\nPROCESOS:\\n"
            + self.system.processes_module()
            + "\\n\\nBATERIA:\\n"
            + self.system.battery_module()
        )
        self._show_module("DIAGNOSTICO", info)
''',
    "_on_tools": '''    def _on_tools(self):
        self._add_log(f"Module HERRAMIENTAS selected [{self.system.os_name()}]")
        data = self.system.summary()
        info = (
            "ULTRON V3 // HERRAMIENTAS MULTIPLATAFORMA\\n\\n"
            f"Sistema detectado: {data['system']}\\n"
            f"Equipo: {data['hostname']}\\n"
            f"Arquitectura: {data['architecture']}\\n"
            f"Python: {data['python']}\\n"
            f"IP local: {data['local_ip']}\\n\\n"
            "La capa V3 ya dispone de funciones portables para abrir "
            "terminal, archivos, URLs y aplicaciones compatibles."
        )
        self._show_module("HERRAMIENTAS", info)
''',
}

changed = []
for name, body in methods.items():
    code, ok = replace_method(code, name, body)
    if ok:
        changed.append(name)

# 3) Disco portable para métricas.
code = code.replace(
    'psutil.disk_usage("/").percent',
    'psutil.disk_usage((Path.home().anchor if self.system.is_windows else "/")).percent'
)

# 4) Backup y escritura.
if not BACKUP.exists():
    shutil.copy2(TARGET, BACKUP)

TARGET.write_text(code, encoding="utf-8")

print("ULTRON V3 // GUI BRIDGE PATCH")
print("=" * 42)
print("Actualizado:", TARGET)
print("Backup:", BACKUP)
print("Conectados:", ", ".join(changed) if changed else "ninguno")
print("Ahora prueba: python3 gui/ultron.py")
