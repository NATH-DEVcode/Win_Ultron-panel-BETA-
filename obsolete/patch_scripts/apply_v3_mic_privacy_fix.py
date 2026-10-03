#!/usr/bin/env python3
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "gui" / "ultron.py"
BACKUP = ROOT / "gui" / "ultron.py.pre-v3-mic-privacy-backup"

if not TARGET.exists():
    raise SystemExit(f"No encontré: {TARGET}")

code = TARGET.read_text(encoding="utf-8")
if not BACKUP.exists():
    shutil.copy2(TARGET, BACKUP)

def replace_method(source, name, new_body):
    token = f"    def {name}("
    start = source.find(token)
    if start < 0:
        return source, False
    end = source.find("\n    def ", start + len(token))
    if end < 0:
        end = source.find("\n\nif __name__ == \"__main__\":", start)
    if end < 0:
        end = len(source)
    return source[:start] + new_body.strip("\n") + "\n" + source[end:], True

begin_method = """    def _begin_continuous_listening(self, generation=None):
        # Solo el CORE autorizado puede iniciar escucha.
        if generation is None:
            generation = self.consciousness_generation

        if not getattr(self, "mic_authorized", False):
            return
        if generation != self.consciousness_generation:
            return
        if not getattr(self, "consciousness_active", False):
            return
        if self.ai_busy:
            return

        self.ai_busy = True
        self._set_live_text("")
        self._set_consciousness_state(
            "LISTENING",
            "● CONCIENCIA ACTIVA",
            TURQUOISE
        )

        threading.Thread(
            target=self._voice_cycle,
            args=(generation,),
            daemon=True
        ).start()
"""

stop_method = """    def _stop_microphone_capture(self):
        # Detiene AudioAdapter (Linux/Windows).
        try:
            self.system.stop_audio_capture()
        except Exception:
            pass

        # Compatibilidad con parecord antiguo.
        proc = getattr(self, "mic_process", None)
        self.mic_process = None
        if proc and proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=1)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
"""

record_method = """    def _record_until_silence(self, wav_path, input_device=None):
        # Captura protegida por la autorización real del CORE.
        generation = self.consciousness_generation

        if not getattr(self, "mic_authorized", False):
            self._add_log("PRIVACY: captura rechazada — CORE no autorizado")
            return False

        if not getattr(self, "consciousness_active", False):
            self._add_log("PRIVACY: captura rechazada — CONCIENCIA inactiva")
            return False

        try:
            result = self.system.record_until_silence(
                wav_path=wav_path,
                input_device=input_device,
                max_seconds=12,
                silence_seconds=0.9,
            )
        except Exception as exc:
            self._add_log(f"Audio error: {exc}")
            return False

        # Si se apagó el CORE mientras grababa, descartar audio.
        if generation != self.consciousness_generation:
            return False
        if not getattr(self, "mic_authorized", False):
            return False
        if not getattr(self, "consciousness_active", False):
            return False

        return bool(result)
"""

for name, body in (
    ("_begin_continuous_listening", begin_method),
    ("_stop_microphone_capture", stop_method),
    ("_record_until_silence", record_method),
):
    code, ok = replace_method(code, name, body)
    if not ok:
        raise SystemExit(f"No encontré {name}; no se aplicó el parche.")

TARGET.write_text(code, encoding="utf-8")

print("ULTRON V3 // MIC PRIVACY FIX")
print("=" * 42)
print("Actualizado:", TARGET)
print("Backup:", BACKUP)
print("Prueba: python3 -m gui.ultron")
