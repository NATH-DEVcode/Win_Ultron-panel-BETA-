#!/usr/bin/env python3
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "gui" / "ultron.py"
BRIDGE = ROOT / "core" / "system_bridge.py"
BACKUP = ROOT / "gui" / "ultron.py.pre-v3-tts-backup"

if not TARGET.exists():
    raise SystemExit(f"No encontré: {TARGET}")
if not BRIDGE.exists():
    raise SystemExit(f"No encontré: {BRIDGE}")

code = TARGET.read_text(encoding="utf-8")
bridge = BRIDGE.read_text(encoding="utf-8")

if not BACKUP.exists():
    shutil.copy2(TARGET, BACKUP)

# 1) Conectar TTSAdapter al system bridge.
tts_import = "from core.tts_adapter import TTSAdapter\n"
if tts_import not in bridge:
    marker = "from core.audio_adapter import AudioAdapter\n"
    if marker not in bridge:
        raise SystemExit("No encontré el import de AudioAdapter en system_bridge.py")
    bridge = bridge.replace(marker, marker + tts_import, 1)

if "self.tts = TTSAdapter()" not in bridge:
    marker = "        self.audio = AudioAdapter()\n"
    if marker not in bridge:
        raise SystemExit("No encontré AudioAdapter() en system_bridge.py")
    bridge = bridge.replace(marker, marker + "        self.tts = TTSAdapter()\n", 1)

# Métodos TTS del bridge.
if "    def prepare_speech(self, text):" not in bridge:
    insertion = """
    # -------- Voz / TTS --------
    def prepare_speech(self, text):
        return self.tts.prepare_speech(text)

    def play_prepared_speech(self, speech_path, output_device=None, volume=None):
        if volume is not None:
            self.tts.set_volume(volume)
        return self.tts.play_prepared_speech(
            speech_path,
            output_device=output_device,
        )

    def stop_speaking(self):
        self.tts.stop()

    def tts_ready(self):
        return self.tts.is_ready()

    def tts_backend(self):
        return self.tts.backend_name()

"""
    marker = "    # -------- Diagnóstico --------\n"
    if marker not in bridge:
        raise SystemExit("No encontré la sección Diagnóstico en system_bridge.py")
    bridge = bridge.replace(marker, insertion + marker, 1)

BRIDGE.write_text(bridge, encoding="utf-8")


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


stop_body = """    def _stop_speaking(self):
        # ULTRON V3: detiene TTS en Linux o Windows.
        try:
            self.system.stop_speaking()
        except Exception:
            pass

        # Compatibilidad con procesos de versiones anteriores.
        process = getattr(self, "tts_process", None)
        self.tts_process = None
        if process and process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=1)
            except Exception:
                try:
                    process.kill()
                except Exception:
                    pass
"""

prepare_body = """    def _prepare_speech(self, text):
        # ULTRON V3: edge-tts gestionado por TTSAdapter.
        return self.system.prepare_speech(text)
"""

play_body = """    def _play_prepared_speech(self, speech_path):
        # ULTRON V3: FFmpeg/ffplay multiplataforma.
        output_device = None

        # Solo Linux necesita conservar el sink PulseAudio/PipeWire.
        if self.system.is_linux:
            try:
                output_device = self._resolve_output_device()
            except Exception:
                output_device = None

        volume = getattr(self, "ultron_volume", 90)

        return self.system.play_prepared_speech(
            speech_path,
            output_device=output_device,
            volume=volume,
        )
"""

speak_body = """    def _speak_text(self, text):
        # Compatibilidad con llamadas existentes.
        speech_path = self._prepare_speech(text)
        self._play_prepared_speech(speech_path)
"""

for name, body in (
    ("_stop_speaking", stop_body),
    ("_prepare_speech", prepare_body),
    ("_play_prepared_speech", play_body),
    ("_speak_text", speak_body),
):
    code, ok = replace_method(code, name, body)
    if not ok:
        raise SystemExit(f"No encontré {name}; se canceló el parche.")

TARGET.write_text(code, encoding="utf-8")

print("ULTRON V3 // TTS GUI BRIDGE")
print("=" * 40)
print("GUI:", TARGET)
print("Bridge:", BRIDGE)
print("Backup:", BACKUP)
print()
print("Prueba:")
print("  python3 -m gui.ultron")
