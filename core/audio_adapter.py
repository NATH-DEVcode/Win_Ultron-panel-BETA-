#!/usr/bin/env python3
"""
ULTRON PANEL V3 // AUDIO ADAPTER
Audio multiplataforma para Linux y Windows.

Objetivos:
- Mantener PulseAudio/PipeWire (parecord/pactl/paplay) en Linux.
- Usar sounddevice/PortAudio en Windows sin NumPy.
- No abrir el micrófono por sí solo.
- La GUI debe decidir cuándo autorizar la captura.
"""

from __future__ import annotations

import math
import os
import platform
import shutil
import subprocess
import threading
import time
import wave

SYSTEM = platform.system().lower()
IS_WINDOWS = SYSTEM == "windows"
IS_LINUX = SYSTEM == "linux"

try:
    import sounddevice as sd
    HAS_SOUNDDEVICE = True
except Exception:
    sd = None
    HAS_SOUNDDEVICE = False


class AudioAdapter:
    def __init__(self):
        self._stop_event = threading.Event()
        self._linux_process = None

    # --------------------------------------------------------
    # Estado / dispositivos
    # --------------------------------------------------------
    def backend_name(self):
        if IS_LINUX and shutil.which("parecord"):
            return "PulseAudio/PipeWire"
        if HAS_SOUNDDEVICE:
            return "PortAudio/sounddevice"
        return "No disponible"

    def is_ready_for_input(self):
        if IS_LINUX and shutil.which("parecord"):
            return True
        return HAS_SOUNDDEVICE

    def list_input_devices(self):
        if IS_LINUX and shutil.which("pactl"):
            devices = []
            try:
                out = subprocess.check_output(
                    ["pactl", "list", "short", "sources"],
                    text=True,
                    stderr=subprocess.DEVNULL,
                )
                for line in out.splitlines():
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        name = parts[1].strip()
                        if not name.endswith(".monitor"):
                            devices.append(name)
            except Exception:
                pass
            if devices:
                return devices

        if HAS_SOUNDDEVICE:
            devices = []
            try:
                for index, info in enumerate(sd.query_devices()):
                    if int(info.get("max_input_channels", 0)) > 0:
                        devices.append(f"{index}: {info.get('name', 'Micrófono')}")
            except Exception:
                pass
            return devices

        return []

    def list_output_devices(self):
        if IS_LINUX and shutil.which("pactl"):
            devices = []
            try:
                out = subprocess.check_output(
                    ["pactl", "list", "short", "sinks"],
                    text=True,
                    stderr=subprocess.DEVNULL,
                )
                for line in out.splitlines():
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        devices.append(parts[1].strip())
            except Exception:
                pass
            if devices:
                return devices

        if HAS_SOUNDDEVICE:
            devices = []
            try:
                for index, info in enumerate(sd.query_devices()):
                    if int(info.get("max_output_channels", 0)) > 0:
                        devices.append(f"{index}: {info.get('name', 'Salida')}")
            except Exception:
                pass
            return devices

        return []

    def default_input(self):
        if IS_LINUX and shutil.which("pactl"):
            try:
                return subprocess.check_output(
                    ["pactl", "get-default-source"],
                    text=True,
                    stderr=subprocess.DEVNULL,
                ).strip()
            except Exception:
                pass

        if HAS_SOUNDDEVICE:
            try:
                idx = sd.default.device[0]
                if idx is not None and int(idx) >= 0:
                    info = sd.query_devices(int(idx))
                    return f"{int(idx)}: {info['name']}"
            except Exception:
                pass

        return ""

    def default_output(self):
        if IS_LINUX and shutil.which("pactl"):
            try:
                return subprocess.check_output(
                    ["pactl", "get-default-sink"],
                    text=True,
                    stderr=subprocess.DEVNULL,
                ).strip()
            except Exception:
                pass

        if HAS_SOUNDDEVICE:
            try:
                idx = sd.default.device[1]
                if idx is not None and int(idx) >= 0:
                    info = sd.query_devices(int(idx))
                    return f"{int(idx)}: {info['name']}"
            except Exception:
                pass

        return ""

    # --------------------------------------------------------
    # Captura
    # --------------------------------------------------------
    def stop_capture(self):
        """Detiene una captura iniciada por la GUI."""
        self._stop_event.set()

        proc = self._linux_process
        self._linux_process = None
        if proc and proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=1)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass

    @staticmethod
    def _rms_s16le(data):
        """RMS puro Python; no usa NumPy/audioop."""
        if not data:
            return 0

        usable = len(data) - (len(data) % 2)
        if usable <= 0:
            return 0

        samples = memoryview(data[:usable]).cast("h")
        if not samples:
            return 0

        total = 0
        for sample in samples:
            total += sample * sample
        return int(math.sqrt(total / len(samples)))

    @staticmethod
    def _device_index(value):
        if value in (None, "", "Automático", "Automatico"):
            return None
        text = str(value).strip()
        try:
            return int(text.split(":", 1)[0].strip())
        except Exception:
            return None

    def record_until_silence(
        self,
        wav_path,
        input_device=None,
        rate=16000,
        channels=1,
        max_seconds=12,
        silence_seconds=1.0,
        threshold=450,
        require_quiet_lead=True,
    ):
        """
        Graba audio únicamente cuando esta función es llamada.
        Devuelve True si se detectó voz y se creó un WAV válido.
        """
        self._stop_event.clear()

        if IS_LINUX and shutil.which("parecord"):
            return self._record_linux(
                wav_path,
                input_device,
                rate,
                channels,
                max_seconds,
                silence_seconds,
                threshold,
                require_quiet_lead,
            )

        if HAS_SOUNDDEVICE:
            return self._record_sounddevice(
                wav_path,
                input_device,
                rate,
                channels,
                max_seconds,
                silence_seconds,
                threshold,
                require_quiet_lead,
            )

        raise RuntimeError(
            "No hay backend de captura disponible. "
            "En Windows instala: pip install sounddevice"
        )

    def _record_linux(
        self,
        wav_path,
        input_device,
        rate,
        channels,
        max_seconds,
        silence_seconds,
        threshold,
        require_quiet_lead,
    ):
        cmd = ["parecord"]
        if input_device and input_device not in ("Automático", "Automatico"):
            cmd.append(f"--device={input_device}")
        cmd.extend([
            "--raw",
            "--format=s16le",
            f"--rate={rate}",
            f"--channels={channels}",
        ])

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self._linux_process = proc

        sample_width = 2
        chunk_ms = 100
        chunk_bytes = int(rate * channels * sample_width * chunk_ms / 1000)
        max_chunks = max(1, int(max_seconds * 1000 / chunk_ms))
        silence_needed = max(1, int(silence_seconds * 1000 / chunk_ms))

        frames = []
        started = False
        silent = 0
        quiet_lead = 0

        try:
            for _ in range(max_chunks):
                if self._stop_event.is_set():
                    return False

                data = proc.stdout.read(chunk_bytes)
                if not data:
                    break

                frames.append(data)
                level = self._rms_s16le(data)

                if not started:
                    if level < threshold:
                        quiet_lead += 1
                    elif not require_quiet_lead or quiet_lead >= 2:
                        started = True
                        silent = 0
                elif level >= threshold:
                    silent = 0
                else:
                    silent += 1
                    if silent >= silence_needed:
                        break
        finally:
            self._linux_process = None
            try:
                proc.terminate()
                proc.wait(timeout=1)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass

        if not started or not frames:
            return False

        with wave.open(str(wav_path), "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(rate)
            wf.writeframes(b"".join(frames))

        return True

    def _record_sounddevice(
        self,
        wav_path,
        input_device,
        rate,
        channels,
        max_seconds,
        silence_seconds,
        threshold,
        require_quiet_lead,
    ):
        device_index = self._device_index(input_device)

        sample_width = 2
        chunk_ms = 100
        blocksize = int(rate * chunk_ms / 1000)
        max_chunks = max(1, int(max_seconds * 1000 / chunk_ms))
        silence_needed = max(1, int(silence_seconds * 1000 / chunk_ms))

        frames = []
        started = False
        silent = 0
        quiet_lead = 0

        with sd.RawInputStream(
            samplerate=rate,
            blocksize=blocksize,
            device=device_index,
            channels=channels,
            dtype="int16",
        ) as stream:
            for _ in range(max_chunks):
                if self._stop_event.is_set():
                    return False

                data, overflowed = stream.read(blocksize)
                raw = bytes(data)
                frames.append(raw)

                level = self._rms_s16le(raw)

                if not started:
                    if level < threshold:
                        quiet_lead += 1
                    elif not require_quiet_lead or quiet_lead >= 2:
                        started = True
                        silent = 0
                elif level >= threshold:
                    silent = 0
                else:
                    silent += 1
                    if silent >= silence_needed:
                        break

        if not started or not frames:
            return False

        with wave.open(str(wav_path), "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(rate)
            wf.writeframes(b"".join(frames))

        return True

    # --------------------------------------------------------
    # Prueba simple
    # --------------------------------------------------------
    def test_microphone(self, wav_path, input_device=None, seconds=3):
        """Graba una prueba fija de pocos segundos."""
        self._stop_event.clear()

        if IS_LINUX and shutil.which("parecord"):
            cmd = ["parecord"]
            if input_device and input_device not in ("Automático", "Automatico"):
                cmd.append(f"--device={input_device}")
            cmd.extend([
                "--file-format=wav",
                "--format=s16le",
                "--rate=16000",
                "--channels=1",
                str(wav_path),
            ])

            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
            self._linux_process = proc
            try:
                proc.wait(timeout=seconds)
            except subprocess.TimeoutExpired:
                proc.terminate()
                try:
                    proc.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    proc.kill()
            finally:
                self._linux_process = None

        elif HAS_SOUNDDEVICE:
            device_index = self._device_index(input_device)
            rate = 16000
            blocksize = 1600
            frames = []
            end = time.monotonic() + seconds

            with sd.RawInputStream(
                samplerate=rate,
                blocksize=blocksize,
                device=device_index,
                channels=1,
                dtype="int16",
            ) as stream:
                while time.monotonic() < end and not self._stop_event.is_set():
                    data, overflowed = stream.read(blocksize)
                    frames.append(bytes(data))

            with wave.open(str(wav_path), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(rate)
                wf.writeframes(b"".join(frames))

        else:
            raise RuntimeError(
                "No hay backend de micrófono. "
                "En Windows instala: pip install sounddevice"
            )

        return os.path.getsize(wav_path) if os.path.exists(wav_path) else 0


if __name__ == "__main__":
    audio = AudioAdapter()
    print("ULTRON // AUDIO ADAPTER")
    print("=" * 40)
    print("Sistema:", platform.system())
    print("Backend:", audio.backend_name())
    print("Entrada predeterminada:", audio.default_input() or "No disponible")
    print("Salida predeterminada:", audio.default_output() or "No disponible")
    print("\nEntradas:")
    for item in audio.list_input_devices():
        print(" -", item)
