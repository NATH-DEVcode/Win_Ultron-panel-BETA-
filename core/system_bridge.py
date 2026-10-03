#!/usr/bin/env python3
"""
ULTRON PANEL V3 // SYSTEM BRIDGE
Conecta la GUI con platform_adapter.py y audio_adapter.py.

Este archivo NO reemplaza gui/ultron.py todavía.
Sirve como una API estable para que la GUI use Linux o Windows
sin ejecutar comandos específicos del SO directamente.
"""

from __future__ import annotations

from pathlib import Path

from core import platform_adapter as platform
from core.audio_adapter import AudioAdapter
from core.tts_adapter import TTSAdapter


class UltronSystemBridge:
    def __init__(self):
        self.audio = AudioAdapter()
        self.tts = TTSAdapter()

    # -------- Plataforma --------
    @property
    def is_windows(self):
        return platform.IS_WINDOWS

    @property
    def is_linux(self):
        return platform.IS_LINUX

    def os_name(self):
        return platform.platform_name()

    def summary(self):
        return platform.platform_summary()

    # -------- Módulos GUI --------
    def system_module(self):
        return platform.system_info()

    def network_module(self):
        return platform.network_info()

    def security_module(self):
        return platform.security_info()

    def files_module(self):
        return platform.disk_info()

    def processes_module(self):
        return platform.process_info()

    def battery_module(self):
        return platform.battery_info()

    def temperature_module(self):
        return platform.temperature_info()

    # -------- Acciones --------
    def open_url(self, url):
        return platform.open_url(url)

    def open_app(self, name):
        return platform.open_app(name)

    def open_path(self, path):
        return platform.open_path(path)

    def open_terminal(self):
        return platform.open_terminal()

    # -------- Audio --------
    def audio_backend(self):
        return self.audio.backend_name()

    def audio_ready(self):
        return self.audio.is_ready_for_input()

    def input_devices(self):
        return self.audio.list_input_devices()

    def output_devices(self):
        return self.audio.list_output_devices()

    def default_input(self):
        return self.audio.default_input()

    def default_output(self):
        return self.audio.default_output()

    def record_until_silence(
        self,
        wav_path,
        input_device=None,
        max_seconds=12,
        silence_seconds=0.9,
        threshold=700,
    ):
        return self.audio.record_until_silence(
            wav_path=wav_path,
            input_device=input_device,
            rate=16000,
            channels=1,
            max_seconds=max_seconds,
            silence_seconds=silence_seconds,
            threshold=threshold,
            require_quiet_lead=True,
        )

    def stop_audio_capture(self):
        self.audio.stop_capture()


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

    def speak(self, text, output_device=None, volume=None):
        if volume is not None:
            self.tts.set_volume(volume)
        return self.tts.speak(text, output_device=output_device)

    def stop_speaking(self):
        self.tts.stop()

    def tts_ready(self):
        return self.tts.is_ready()

    def tts_backend(self):
        return self.tts.backend_name()

    # -------- Diagnóstico --------
    def diagnostics(self):
        data = self.summary()
        lines = [
            "ULTRON V3 // PLATFORM DIAGNOSTICS",
            "=" * 42,
            f"Sistema: {data['system']}",
            f"Equipo: {data['hostname']}",
            f"Arquitectura: {data['architecture']}",
            f"Python: {data['python']}",
            f"IP local: {data['local_ip']}",
            f"Audio backend: {self.audio_backend()}",
            f"Micrófono disponible: {'SI' if self.audio_ready() else 'NO'}",
            f"Entrada: {self.default_input() or 'No disponible'}",
            f"Salida: {self.default_output() or 'No disponible'}",
        ]
        return "\n".join(lines)


def create_bridge():
    return UltronSystemBridge()


if __name__ == "__main__":
    bridge = create_bridge()
    print(bridge.diagnostics())
