#!/usr/bin/env python3
"""
ULTRON PANEL V3 // TTS ADAPTER
Voz multiplataforma Linux + Windows.

Generación:
    edge-tts -> es-MX-JorgeNeural

Procesamiento/reproducción:
    ffplay + filtros FFmpeg en tiempo real

Linux:
    Puede ajustar volumen mediante pactl si está disponible.

Windows:
    No depende de pactl/PulseAudio. ffplay usa la salida predeterminada
    de Windows.

Este módulo no clona la voz de ninguna persona real.
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import tempfile
import threading


IS_WINDOWS = platform.system().lower() == "windows"
IS_LINUX = platform.system().lower() == "linux"


class TTSAdapter:
    def __init__(
        self,
        voice="es-MX-JorgeNeural",
        rate="+4%",
        pitch="-7Hz",
        volume=90,
    ):
        self.voice = voice
        self.rate = rate
        self.pitch = pitch
        self.volume = int(volume)

        self._process = None
        self._lock = threading.Lock()

    # ---------------------------------------------------------
    # Diagnóstico
    # ---------------------------------------------------------
    def edge_tts_path(self):
        path = shutil.which("edge-tts")
        if path:
            return path
        try:
            import edge_tts  # noqa: F401
            return "PYTHON_MODULE"
        except Exception:
            return None

    def ffplay_path(self):
        return shutil.which("ffplay")

    def mpv_path(self):
        return shutil.which("mpv")

    def backend_name(self):
        if IS_WINDOWS:
            return "ULTRON Neural FX"
        if self.ffplay_path():
            return "edge-tts + ffplay/FFmpeg"
        if self.mpv_path():
            return "edge-tts + mpv"
        return "No disponible"

    def is_ready(self):
        if IS_WINDOWS:
            return True
        return bool(
            self.edge_tts_path()
            and (self.ffplay_path() or self.mpv_path())
        )

    # ---------------------------------------------------------
    # Configuración
    # ---------------------------------------------------------
    def set_volume(self, value):
        try:
            value = int(value)
        except Exception:
            value = 90

        self.volume = max(0, min(150, value))

    def set_voice(self, voice):
        if voice:
            self.voice = str(voice)

    # ---------------------------------------------------------
    # Síntesis
    # ---------------------------------------------------------
    def prepare_speech(self, text):
        text = str(text).strip()
        if not text:
            raise ValueError("No hay texto para sintetizar.")

        edge_tts_backend = self.edge_tts_path()
        if not edge_tts_backend:
            raise RuntimeError(
                "Falta edge-tts. Instala el paquete edge-tts."
            )

        raw_file = tempfile.NamedTemporaryFile(
            prefix="ultron_neural_",
            suffix=".mp3",
            delete=False,
        )
        raw_path = raw_file.name
        raw_file.close()

        try:
            if edge_tts_backend == "PYTHON_MODULE":
                import asyncio
                import edge_tts as edge_tts_module

                async def _save():
                    communicate = edge_tts_module.Communicate(
                        text=text,
                        voice=self.voice,
                        rate=self.rate,
                        pitch=self.pitch,
                    )
                    await communicate.save(raw_path)

                asyncio.run(_save())
            else:
                synth = subprocess.run(
                    [
                        edge_tts_backend,
                        "--voice", self.voice,
                        f"--rate={self.rate}",
                        f"--pitch={self.pitch}",
                        "--text", text,
                        "--write-media", raw_path,
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=45,
                    creationflags=(getattr(subprocess, "CREATE_NO_WINDOW", 0) if IS_WINDOWS else 0),
                )

                if synth.returncode != 0:
                    error = (synth.stderr or "").strip()
                    raise RuntimeError(
                        "No pude generar la voz neural de ULTRON."
                        + (f" Detalle: {error}" if error else "")
                    )

            if not os.path.exists(raw_path) or os.path.getsize(raw_path) == 0:
                raise RuntimeError("No pude generar la voz neural de ULTRON.")

            return raw_path

        except Exception:
            try:
                os.remove(raw_path)
            except Exception:
                pass
            raise

    # ---------------------------------------------------------
    # Efecto ULTRON
    # ---------------------------------------------------------
    @staticmethod
    def ultron_filter():
        """
        Mantiene el carácter de la versión actual:
        grave, grueso, comprimido, borde digital y eco corto.
        """
        return (
            "highpass=f=58,"
            "lowpass=f=8200,"
            "bass=g=5:f=115:w=0.7,"
            "equalizer=f=220:t=q:w=1.0:g=2.5,"
            "equalizer=f=3100:t=q:w=1.1:g=-1.3,"
            "acompressor=threshold=-20dB:ratio=2.8:"
            "attack=8:release=150:makeup=1.8,"
            "acrusher=bits=13:mix=0.13,"
            "aecho=0.76:0.13:36:0.06,"
            "alimiter=limit=0.92"
        )

    def _set_linux_volume(self, sink=None):
        """
        Solo Linux/PulseAudio-PipeWire.
        En Windows se omite completamente.
        """
        if not IS_LINUX:
            return

        pactl = shutil.which("pactl")
        if not pactl:
            return

        if not sink:
            try:
                sink = subprocess.check_output(
                    [pactl, "get-default-sink"],
                    text=True,
                    stderr=subprocess.DEVNULL,
                    timeout=3,
                ).strip()
            except Exception:
                return

        if not sink:
            return

        try:
            subprocess.run(
                [
                    pactl,
                    "set-sink-volume",
                    sink,
                    f"{self.volume}%",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=3,
            )
        except Exception:
            pass

    # ---------------------------------------------------------
    # Reproducción
    # ---------------------------------------------------------
    def play_prepared_speech(self, speech_path, output_device=None):
        if not os.path.exists(speech_path):
            raise FileNotFoundError(speech_path)

        ffplay = self.ffplay_path()
        mpv = self.mpv_path()

        if not ffplay and not mpv:
            raise RuntimeError(
                "Falta ffplay/FFmpeg o mpv. "
                "En Windows instala FFmpeg y añádelo al PATH."
            )

        # Linux puede conservar el volumen/sink actual.
        self._set_linux_volume(output_device)

        try:
            if ffplay:
                cmd = [
                    ffplay,
                    "-nodisp",
                    "-autoexit",
                    "-loglevel", "quiet",
                    "-af", self.ultron_filter(),
                    speech_path,
                ]
            else:
                cmd = [
                    mpv,
                    "--no-video",
                    "--really-quiet",
                    speech_path,
                ]

            with self._lock:
                popen_kwargs = {
                    "stdout": subprocess.DEVNULL,
                    "stderr": subprocess.DEVNULL,
                }
                if IS_WINDOWS:
                    popen_kwargs["creationflags"] = getattr(
                        subprocess, "CREATE_NO_WINDOW", 0
                    )
                self._process = subprocess.Popen(cmd, **popen_kwargs)

            return_code = self._process.wait()
            if return_code:
                raise RuntimeError(
                    f"El reproductor de audio terminó con código {return_code}."
                )

        finally:
            with self._lock:
                self._process = None

            try:
                os.remove(speech_path)
            except Exception:
                pass

    def speak(self, text, output_device=None):
        # Mantén siempre la voz neural de ULTRON. El respaldo SAPI de Windows
        # suena distinto y puede degradar la experiencia; si Edge TTS falla,
        # deja que la GUI muestre el error real.
        speech_path = self.prepare_speech(text)
        self.play_prepared_speech(
            speech_path,
            output_device=output_device,
        )

    def stop(self):
        """Detiene inmediatamente la voz que se esté reproduciendo."""
        with self._lock:
            process = self._process
            self._process = None

        if process and process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=1)
            except Exception:
                try:
                    process.kill()
                except Exception:
                    pass

    def _speak_windows_cinematic(self, text):
        """Voz neural procesada y reproducida sin ventanas externas."""
        import wave
        import sounddevice as sd

        edge = self.edge_tts_path()
        ffmpeg = shutil.which("ffmpeg")
        if not edge or not ffmpeg:
            return self._speak_windows_sapi(text)

        mp3 = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        mp3.close()
        wav.close()
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            # Voz neural masculina mexicana; ligeramente más lenta antes del efecto.
            subprocess.run(
                [edge, "--voice", "es-MX-JorgeNeural", "--rate=-6%",
                 "--text", str(text), "--write-media", mp3.name],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                creationflags=flags,
            )
            # Timbre más oscuro + resonancia mecánica sutil + eco corto.
            af = (
                "asetrate=44100*0.88,aresample=44100,"
                "equalizer=f=120:t=q:w=1.1:g=5,"
                "equalizer=f=2800:t=q:w=1.4:g=-3,"
                "aecho=0.8:0.32:38:0.16,"
                "acompressor=threshold=-18dB:ratio=2.5:attack=10:release=90,"
                "volume=1.15"
            )
            subprocess.run(
                [ffmpeg, "-y", "-loglevel", "error", "-i", mp3.name,
                 "-af", af, "-ac", "1", "-ar", "44100",
                 "-c:a", "pcm_s16le", wav.name],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                creationflags=flags,
            )
            with wave.open(wav.name, "rb") as wf:
                frames = wf.readframes(wf.getnframes())
                channels = wf.getnchannels()
                rate = wf.getframerate()
                width = wf.getsampwidth()
            if width != 2:
                raise RuntimeError("Formato WAV inesperado")
            import array
            samples = array.array("h")
            samples.frombytes(frames)
            sd.play(samples, rate, blocking=True)
        finally:
            for f in (mp3.name, wav.name):
                try:
                    os.remove(f)
                except OSError:
                    pass

    def _speak_windows_sapi(self, text):
        """Fallback de voz nativa de Windows."""
        import base64
        payload = base64.b64encode(str(text).encode("utf-8")).decode("ascii")
        ps = (
            "$ErrorActionPreference='Stop';"
            "$b=[Convert]::FromBase64String('" + payload + "');"
            "$t=[Text.Encoding]::UTF8.GetString($b);"
            "$v=New-Object -ComObject SAPI.SpVoice;"
            "$es=$v.GetVoices() | Where-Object {$_.GetDescription() -match 'Spanish|Espa'} | Select-Object -First 1;"
            "if($es){$v.Voice=$es};"
            "$v.Rate=-1;$v.Volume=100;"
            "$null=$v.Speak($t)"
        )
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            subprocess.run(
                ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                timeout=45,
                check=True,
                creationflags=flags,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            detail = getattr(exc, "stderr", "")
            detail = (detail or str(exc)).strip()[:240]
            raise RuntimeError(
                "La voz local de Windows no pudo reproducirse. " + detail
            ) from exc

    def diagnostics(self):
        return {
            "system": platform.system(),
            "voice": self.voice,
            "backend": self.backend_name(),
            "edge_tts": self.edge_tts_path() or "NO",
            "ffplay": self.ffplay_path() or "NO",
            "mpv": self.mpv_path() or "NO",
            "ready": self.is_ready(),
        }


if __name__ == "__main__":
    tts = TTSAdapter()
    info = tts.diagnostics()

    print("ULTRON V3 // TTS ADAPTER")
    print("=" * 40)
    for key, value in info.items():
        print(f"{key}: {value}")

