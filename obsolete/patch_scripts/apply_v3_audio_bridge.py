#!/usr/bin/env python3
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "gui" / "ultron.py"
BACKUP = ROOT / "gui" / "ultron.py.pre-v3-audio-backup"

if not TARGET.exists():
    raise SystemExit(f"No encontré {TARGET}")

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

changed = []

new_record = '''    def _record_until_silence(self, wav_path, input_device=None):
        # ULTRON V3: captura multiplataforma y bloqueada si CONCIENCIA está apagada.
        if not getattr(self, "conciencia_active", False):
            self._add_log("Audio bloqueado: CONCIENCIA inactiva.")
            return False

        try:
            return self.system.record_until_silence(
                wav_path=wav_path,
                input_device=input_device,
                max_seconds=12,
                silence_seconds=0.9,
            )
        except Exception as exc:
            self._add_log(f"Audio error: {exc}")
            return False
'''

code, ok = replace_method(code, "_record_until_silence", new_record)
if ok:
    changed.append("_record_until_silence")

# Añade una parada explícita del backend en métodos de desactivación/cierre si existen.
for method_name in ("_stop_conciencia", "_deactivate_conciencia", "_on_close", "_close", "on_close"):
    token = f"    def {method_name}("
    start = code.find(token)
    if start < 0:
        continue
    first_line_end = code.find("\n", start)
    block_end = code.find("\n    def ", first_line_end)
    if block_end < 0:
        block_end = len(code)
    block = code[start:block_end]
    if "self.system.stop_audio_capture()" not in block:
        injection = (
            "\n        try:\n"
            "            self.system.stop_audio_capture()\n"
            "        except Exception:\n"
            "            pass\n"
        )
        code = code[:first_line_end] + injection + code[first_line_end:]
        changed.append(method_name)

TARGET.write_text(code, encoding="utf-8")

print("ULTRON V3 // CONCIENCIA AUDIO PATCH")
print("=" * 44)
print("Actualizado:", TARGET)
print("Backup:", BACKUP)
print("Cambios:", ", ".join(changed) if changed else "ninguno")
print("Prueba con: python3 -m gui.ultron")
