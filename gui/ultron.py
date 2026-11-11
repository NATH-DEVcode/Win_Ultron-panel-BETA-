#!/usr/bin/env python3
"""
ULTRON // CORE  -  GUI V2
Centro de operaciones futurista para Windows
Estética: negro + naranja | Core con anillos orbitando | Mapa plano
"""

import tkinter as tk
from tkinter import font as tkfont, colorchooser
import math
import time
import socket
import platform
import subprocess
from pathlib import Path
import json
import os
import re
import unicodedata
import base64
import ctypes
from ctypes import wintypes
import threading
import shlex
import tempfile
import shutil
import urllib.request
import urllib.error
from urllib.parse import urlsplit
import uuid
import sqlite3
import hashlib
import secrets
import wave
import zlib

from core.system_bridge import create_bridge

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


# ============================================================
# PALETA ULTRON  (naranja + turquesa + verde)
# ============================================================
BG            = "#050505"
BG_PANEL      = "#0c0c0c"
BG_PANEL2     = "#111111"
ORANGE        = "#ff6b00"
ORANGE_L      = "#ff9500"
ORANGE_D      = "#cc5500"
ORANGE_DIM    = "#3a2200"
TURQUOISE     = "#00d4c8"
TURQUOISE_D   = "#008b84"
TURQUOISE_DIM = "#003d3a"
GRAY          = "#1a1a1a"
GRAY2         = "#2a2a2a"
TEXT          = "#e0e0e0"
TEXT_DIM      = "#888888"
GREEN         = "#00cc66"
RED           = "#ff3333"

VOICE_ALERT_CONFIG = (
    Path(__file__).resolve().parent.parent / "config" / "ultron_features.json"
)
DEFAULT_FEATURE_CONFIG = {
    "voice": {
        "apps": {
            "calculadora": ["calc.exe"],
            "bloc de notas": ["notepad.exe"],
            "explorador de archivos": ["explorer.exe"],
            "paint": ["mspaint.exe"],
        },
        "websites": {
            "google": "https://www.google.com/",
            "youtube": "https://www.youtube.com/",
            "whatsapp": "https://web.whatsapp.com/",
            "chatgpt": "https://chatgpt.com/",
        },
    },
    "alerts": {
        "sample_seconds": 5,
        "cpu_percent": 85,
        "cpu_sustained_seconds": 30,
        "memory_percent": 90,
        "disk_percent": 90,
        "battery_percent": 15,
        "temperature_c": 85,
        "ping_ms": 180,
        "network_loss_after_failures": 3,
        "beep_enabled": True,
    },
}


def _normalize_voice_text(value):
    text = unicodedata.normalize("NFKD", str(value or "").casefold())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def _load_feature_config():
    """Carga allowlists y umbrales editables; si faltan, usa valores seguros."""
    try:
        with VOICE_ALERT_CONFIG.open("r", encoding="utf-8") as config_file:
            raw = json.load(config_file)
        if not isinstance(raw, dict):
            raise ValueError("La raíz del JSON debe ser un objeto.")
    except (OSError, ValueError, TypeError):
        raw = {}

    voice = raw.get("voice", {})
    if not isinstance(voice, dict):
        voice = {}

    raw_apps = voice.get("apps", DEFAULT_FEATURE_CONFIG["voice"]["apps"])
    apps = {}
    if isinstance(raw_apps, dict):
        for name, command in raw_apps.items():
            if (
                isinstance(name, str)
                and name.strip()
                and isinstance(command, list)
                and command
                and all(isinstance(part, str) and part.strip() for part in command)
            ):
                apps[name.strip()] = [part.strip() for part in command]

    raw_sites = voice.get("websites", DEFAULT_FEATURE_CONFIG["voice"]["websites"])
    websites = {}
    if isinstance(raw_sites, dict):
        for name, url in raw_sites.items():
            if not isinstance(name, str) or not isinstance(url, str):
                continue
            parsed = urlsplit(url.strip())
            if (
                name.strip()
                and parsed.scheme in ("http", "https")
                and parsed.hostname
                and not parsed.username
            ):
                websites[name.strip()] = url.strip()

    alerts = raw.get("alerts", {})
    if not isinstance(alerts, dict):
        alerts = {}
    alert_config = dict(DEFAULT_FEATURE_CONFIG["alerts"])
    for key, value in alerts.items():
        if key not in alert_config:
            continue
        if key == "beep_enabled":
            if isinstance(value, bool):
                alert_config[key] = value
        else:
            try:
                alert_config[key] = max(0.0, float(value))
            except (TypeError, ValueError):
                pass

    return {"voice": {"apps": apps, "websites": websites}, "alerts": alert_config}

# Fronteras internacionales simplificadas para dar escala sin llenar el mapa
# de límites administrativos. Coordenadas geográficas (longitud, latitud).
MAJOR_COUNTRY_BORDERS = (
    # Alaska / Canadá.
    ((-141, 69), (-141, 66), (-141, 63), (-141, 60)),
    # Canadá / Estados Unidos, incluida la salida hacia los Grandes Lagos.
    ((-123, 49), (-118, 49), (-114, 49), (-110, 49), (-106, 49),
     (-102, 49), (-98, 49), (-95, 49), (-92, 47), (-89, 47),
     (-86, 45), (-83, 45), (-80, 43), (-77, 44), (-74, 45), (-71, 45)),
    # Estados Unidos / México.
    ((-117, 32.5), (-114.8, 32.5), (-111.1, 31.3), (-108.2, 31.3),
     (-106.5, 31.8), (-104.4, 29.6), (-103, 29), (-102, 29.8),
     (-100.5, 29.4), (-99.2, 27.5), (-97.2, 25.9)),
    # Chile / Argentina, siguiendo de forma estilizada la cordillera andina.
    ((-69, -22), (-68, -27), (-69, -32), (-70, -37), (-71, -42),
     (-72, -47), (-73, -52)),
)


def _tint_outline_png(png_data, color):
    """Recolorea el PNG de contornos sin depender de Pillow."""
    try:
        if png_data[:8] != b"\x89PNG\r\n\x1a\n":
            raise ValueError("PNG no válido")
        offset = 8
        chunks = []
        image_data = bytearray()
        width = height = bit_depth = color_type = interlace = None
        while offset < len(png_data):
            size = int.from_bytes(png_data[offset:offset + 4], "big")
            kind = png_data[offset + 4:offset + 8]
            payload = png_data[offset + 8:offset + 8 + size]
            offset += size + 12
            if kind == b"IHDR":
                width = int.from_bytes(payload[:4], "big")
                height = int.from_bytes(payload[4:8], "big")
                bit_depth, color_type, interlace = payload[8], payload[9], payload[12]
                chunks.append((kind, payload))
            elif kind == b"IDAT":
                image_data.extend(payload)
            elif kind == b"IEND":
                break
        if bit_depth != 8 or color_type != 6 or interlace != 0:
            raise ValueError("Formato de mapa no compatible")

        rgb = bytes.fromhex(color.lstrip("#"))
        pixels = bytearray(zlib.decompress(image_data))
        stride = width * 4
        for y in range(height):
            row_start = y * (stride + 1)
            if pixels[row_start] != 0:
                raise ValueError("Filtro de mapa no compatible")
            for pos in range(row_start + 1, row_start + 1 + stride, 4):
                if pixels[pos + 3]:
                    pixels[pos:pos + 3] = rgb

        def make_chunk(kind, payload):
            return (
                len(payload).to_bytes(4, "big") + kind + payload
                + (zlib.crc32(kind + payload) & 0xffffffff).to_bytes(4, "big")
            )

        result = b"\x89PNG\r\n\x1a\n"
        result += make_chunk(b"IHDR", chunks[0][1])
        result += make_chunk(b"IDAT", zlib.compress(bytes(pixels), 6))
        result += make_chunk(b"IEND", b"")
        return base64.b64encode(result).decode("ascii")
    except Exception:
        return base64.b64encode(png_data).decode("ascii")


# ============================================================
# SISTEMA DE APARIENCIAS / THEMES
# ============================================================
CONFIG_FILE = os.path.join(
    os.path.expanduser("~"),
    ".ultron_core_theme.json"
)

THEMES = {
    "ULTRON CLASSIC": {
        "BG": "#050505",
        "BG_PANEL": "#0c0c0c",
        "BG_PANEL2": "#111111",
        "PRIMARY": "#ff6b00",
        "PRIMARY_L": "#ff9500",
        "PRIMARY_D": "#cc5500",
        "PRIMARY_DIM": "#3a2200",
        "SECONDARY": "#00d4c8",
        "SECONDARY_D": "#008b84",
        "SECONDARY_DIM": "#003d3a",
        "TEXT": "#e0e0e0",
        "TEXT_DIM": "#888888",
        "GOOD": "#00cc66",
        "DANGER": "#ff3333",
    },

    "ULTRON CRIMSON": {
        "BG": "#040000",
        "BG_PANEL": "#100505",
        "BG_PANEL2": "#180808",
        "PRIMARY": "#ff2a2a",
        "PRIMARY_L": "#ff5c5c",
        "PRIMARY_D": "#a90000",
        "PRIMARY_DIM": "#3b0707",
        "SECONDARY": "#ffb000",
        "SECONDARY_D": "#b26f00",
        "SECONDARY_DIM": "#4a2c00",
        "TEXT": "#f2e8e8",
        "TEXT_DIM": "#9b8080",
        "GOOD": "#56e39f",
        "DANGER": "#ff3030",
    },

    "STARK ARC": {
        "BG": "#020609",
        "BG_PANEL": "#071018",
        "BG_PANEL2": "#0b1722",
        "PRIMARY": "#00bfff",
        "PRIMARY_L": "#65dcff",
        "PRIMARY_D": "#0074a6",
        "PRIMARY_DIM": "#003346",
        "SECONDARY": "#ffffff",
        "SECONDARY_D": "#8aa8b8",
        "SECONDARY_DIM": "#263844",
        "TEXT": "#e8f7ff",
        "TEXT_DIM": "#7892a3",
        "GOOD": "#00e690",
        "DANGER": "#ff4655",
    },

    "COBALT DRIVE": {
        "BG": "#070914",
        "BG_PANEL": "#0e1224",
        "BG_PANEL2": "#171d35",
        "PRIMARY": "#5577ff",
        "PRIMARY_L": "#9aabff",
        "PRIMARY_D": "#354eb8",
        "PRIMARY_DIM": "#202d66",
        "SECONDARY": "#ff7bd5",
        "SECONDARY_D": "#b94e98",
        "SECONDARY_DIM": "#512343",
        "TEXT": "#f0f1ff",
        "TEXT_DIM": "#969bb8",
        "GOOD": "#58e6a5",
        "DANGER": "#ff5968",
    },

    "VOID PROTOCOL": {
        "BG": "#030304",
        "BG_PANEL": "#0b0b10",
        "BG_PANEL2": "#11111a",
        "PRIMARY": "#8d5cff",
        "PRIMARY_L": "#b094ff",
        "PRIMARY_D": "#5d35bc",
        "PRIMARY_DIM": "#21143e",
        "SECONDARY": "#2ef2d0",
        "SECONDARY_D": "#169f8a",
        "SECONDARY_DIM": "#083f37",
        "TEXT": "#eeeaff",
        "TEXT_DIM": "#8b849f",
        "GOOD": "#48f08b",
        "DANGER": "#ff476f",
    },

    "NIGHT VISION": {
        "BG": "#010401",
        "BG_PANEL": "#061006",
        "BG_PANEL2": "#0a170a",
        "PRIMARY": "#38ff66",
        "PRIMARY_L": "#8dffa7",
        "PRIMARY_D": "#169a35",
        "PRIMARY_DIM": "#0b3914",
        "SECONDARY": "#b7ff00",
        "SECONDARY_D": "#6c9600",
        "SECONDARY_DIM": "#273700",
        "TEXT": "#dcffe3",
        "TEXT_DIM": "#6f9477",
        "GOOD": "#57ff80",
        "DANGER": "#ff4a4a",
    },

    "ARCTIC CIRCUIT": {
        "BG": "#040a10",
        "BG_PANEL": "#081522",
        "BG_PANEL2": "#0d2030",
        "PRIMARY": "#44c8ff",
        "PRIMARY_L": "#9be4ff",
        "PRIMARY_D": "#1682b0",
        "PRIMARY_DIM": "#10394f",
        "SECONDARY": "#b5f5f5",
        "SECONDARY_D": "#64baba",
        "SECONDARY_DIM": "#204747",
        "TEXT": "#e8f8ff",
        "TEXT_DIM": "#8ba9b8",
        "GOOD": "#54e6a5",
        "DANGER": "#ff5364",
    },

    "OBSIDIAN ROSE": {
        "BG": "#10070d",
        "BG_PANEL": "#1b0d17",
        "BG_PANEL2": "#281321",
        "PRIMARY": "#ff5c9a",
        "PRIMARY_L": "#ff9cbe",
        "PRIMARY_D": "#bf356b",
        "PRIMARY_DIM": "#542039",
        "SECONDARY": "#d6a5ff",
        "SECONDARY_D": "#9465ba",
        "SECONDARY_DIM": "#3d2852",
        "TEXT": "#fff0f6",
        "TEXT_DIM": "#b49aa9",
        "GOOD": "#65e6a5",
        "DANGER": "#ff5968",
    },

    "COPPER DUSK": {
        "BG": "#0d0907",
        "BG_PANEL": "#19110d",
        "BG_PANEL2": "#251914",
        "PRIMARY": "#d98b52",
        "PRIMARY_L": "#f2b47e",
        "PRIMARY_D": "#995a31",
        "PRIMARY_DIM": "#49301f",
        "SECONDARY": "#8fc7b0",
        "SECONDARY_D": "#568b75",
        "SECONDARY_DIM": "#263f35",
        "TEXT": "#f8eee5",
        "TEXT_DIM": "#a99a8d",
        "GOOD": "#74d6a2",
        "DANGER": "#e65e58",
    },

    "EMERALD MATRIX": {
        "BG": "#030a07",
        "BG_PANEL": "#07140d",
        "BG_PANEL2": "#0b1d12",
        "PRIMARY": "#00e676",
        "PRIMARY_L": "#73ffb2",
        "PRIMARY_D": "#00994e",
        "PRIMARY_DIM": "#0b3d26",
        "SECONDARY": "#c6ff5e",
        "SECONDARY_D": "#83ad2c",
        "SECONDARY_DIM": "#354516",
        "TEXT": "#e8ffef",
        "TEXT_DIM": "#83a892",
        "GOOD": "#58f59b",
        "DANGER": "#ff5964",
    },

    "SOLAR FLARE": {
        "BG": "#0b0710",
        "BG_PANEL": "#160c18",
        "BG_PANEL2": "#211126",
        "PRIMARY": "#ffb000",
        "PRIMARY_L": "#ffd166",
        "PRIMARY_D": "#bf7000",
        "PRIMARY_DIM": "#4a2b0a",
        "SECONDARY": "#ff4d6d",
        "SECONDARY_D": "#ba2948",
        "SECONDARY_DIM": "#4a1424",
        "TEXT": "#fff1e8",
        "TEXT_DIM": "#b49aa5",
        "GOOD": "#65e6a5",
        "DANGER": "#ff5263",
    },
}


def load_theme_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception:
        return {"theme": "ULTRON CLASSIC"}


def save_theme_config(data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def apply_theme_globals(theme_data):
    global BG, BG_PANEL, BG_PANEL2
    global ORANGE, ORANGE_L, ORANGE_D, ORANGE_DIM
    global TURQUOISE, TURQUOISE_D, TURQUOISE_DIM
    global TEXT, TEXT_DIM, GREEN, RED

    BG = theme_data["BG"]
    BG_PANEL = theme_data["BG_PANEL"]
    BG_PANEL2 = theme_data["BG_PANEL2"]

    ORANGE = theme_data["PRIMARY"]
    ORANGE_L = theme_data["PRIMARY_L"]
    ORANGE_D = theme_data["PRIMARY_D"]
    ORANGE_DIM = theme_data["PRIMARY_DIM"]

    TURQUOISE = theme_data["SECONDARY"]
    TURQUOISE_D = theme_data["SECONDARY_D"]
    TURQUOISE_DIM = theme_data["SECONDARY_DIM"]

    TEXT = theme_data["TEXT"]
    TEXT_DIM = theme_data["TEXT_DIM"]
    GREEN = theme_data["GOOD"]
    RED = theme_data["DANGER"]


_THEME_CFG = load_theme_config()
_THEME_NAME = _THEME_CFG.get("theme", "ULTRON CLASSIC")

if _THEME_NAME == "CUSTOM":
    custom = _THEME_CFG.get("custom_theme")
    if isinstance(custom, dict):
        apply_theme_globals(custom)
else:
    apply_theme_globals(THEMES.get(_THEME_NAME, THEMES["ULTRON CLASSIC"]))


class UltronCore:
    """
    Núcleo visual ULTRON V11.
    Inspirado en HUDs circulares: segmentos, marcas y anillos técnicos.

    El pulso central es una respiración lenta, no un latido rápido.
    """

    def __init__(self, canvas, cx, cy, base_radius=110, on_activate=None):
        self.canvas = canvas
        self.cx = cx
        self.cy = cy
        self.base_r = base_radius
        self.on_activate = on_activate

        self.angle = [0.0] * 6
        self.base_speed = [0.22, -0.16, 0.31, -0.12, 0.18, -0.09]
        self.speed = list(self.base_speed)

        self.state = "IDLE"
        self.pulse_phase = 0.0
        self.rings = []
        self.segment_items = []
        self._build()

    def _arc(self, rel, start, extent, color, width=2):
        r = self.base_r
        return self.canvas.create_arc(
            self.cx-r*rel, self.cy-r*rel,
            self.cx+r*rel, self.cy+r*rel,
            start=start, extent=extent,
            style=tk.ARC,
            outline=color,
            width=width,
            tags=("ultron_core",)
        )

    def _build(self):
        c = self.canvas
        cx, cy, r = self.cx, self.cy, self.base_r

        # Halo exterior técnico.
        for rel, width, color in [
            (1.58, 1, ORANGE_DIM),
            (1.47, 1, ORANGE_DIM),
            (1.34, 2, ORANGE_D),
        ]:
            c.create_oval(
                cx-r*rel, cy-r*rel,
                cx+r*rel, cy+r*rel,
                outline=color,
                width=width,
                tags=("ultron_core",)
            )

        # Dos anillos principales, intencionalmente más gruesos.
        ring_specs = [
            (1.26, 5, ORANGE_L, 298, 0.20),
            (1.10, 3, ORANGE,   250, -0.16),
            (0.95, 6, ORANGE_L, 224, 0.31),
            (0.80, 2, ORANGE_D, 290, -0.12),
            (0.65, 3, ORANGE,   208, 0.18),
            (0.54, 2, ORANGE_D, 275, -0.09),
        ]

        for idx, (rel, width, color, extent, spd) in enumerate(ring_specs):
            a = self._arc(rel, idx*34, extent, color, width)
            self.rings.append((a, idx, extent))

            # Segmento secundario opuesto para aspecto de HUD.
            b = self._arc(
                rel,
                180 + idx*28,
                max(28, int((360-extent)*0.72)),
                ORANGE_D,
                max(1, width-2)
            )
            self.rings.append((b, idx, max(28, int((360-extent)*0.72))))

        # Bloques/ticks externos tipo indicador.
        for deg in range(0, 360, 10):
            rad = math.radians(deg)
            major = (deg % 30 == 0)

            inner = 1.35 if major else 1.39
            outer = 1.48 if major else 1.44

            x1 = cx + math.cos(rad) * r * inner
            y1 = cy + math.sin(rad) * r * inner
            x2 = cx + math.cos(rad) * r * outer
            y2 = cy + math.sin(rad) * r * outer

            c.create_line(
                x1, y1, x2, y2,
                fill=ORANGE if major else ORANGE_DIM,
                width=3 if major else 1,
                tags=("ultron_core",)
            )

        # Barras rectangulares alrededor de la zona media.
        for deg in range(0, 360, 20):
            if deg % 60 == 0:
                continue
            rad = math.radians(deg)
            rr = r * 0.72
            x = cx + math.cos(rad) * rr
            y = cy + math.sin(rad) * rr
            tang = rad + math.pi/2
            half = r * 0.035

            x1 = x + math.cos(tang) * half
            y1 = y + math.sin(tang) * half
            x2 = x - math.cos(tang) * half
            y2 = y - math.sin(tang) * half

            c.create_line(
                x1, y1, x2, y2,
                fill=ORANGE_D,
                width=4,
                tags=("ultron_core",)
            )

        # Núcleo central por capas.
        self.outer_core = c.create_oval(
            cx-r*0.47, cy-r*0.47,
            cx+r*0.47, cy+r*0.47,
            fill=BG_PANEL2,
            outline=ORANGE_D,
            width=3,
            tags=("ultron_core", "core_click")
        )

        # Anillo inmediato alrededor del núcleo eliminado.
        # Conservamos el objeto invisible para mantener compatibilidad
        # con el sistema de estados.
        self.mid_core = c.create_oval(
            cx-r*0.35, cy-r*0.35,
            cx+r*0.35, cy+r*0.35,
            fill="",
            outline="",
            width=0,
            state=tk.HIDDEN,
            tags=("ultron_core",)
        )

        self.inner_core = c.create_oval(
            cx-r*0.235, cy-r*0.235,
            cx+r*0.235, cy+r*0.235,
            fill=ORANGE,
            outline=ORANGE_L,
            width=3,
            tags=("ultron_core", "core_click")
        )

        self.center_core = c.create_oval(
            cx-r*0.105, cy-r*0.105,
            cx+r*0.105, cy+r*0.105,
            fill=ORANGE_L,
            outline="",
            tags=("ultron_core", "core_click")
        )

        # Zona clickeable amplia, invisible.
        c.create_oval(
            cx-r*0.50, cy-r*0.50,
            cx+r*0.50, cy+r*0.50,
            fill="", outline="",
            tags=("core_click",)
        )

        c.tag_bind("core_click", "<Button-1>", self._handle_click)
        c.tag_bind("core_click", "<Enter>", self._handle_enter)
        c.tag_bind("core_click", "<Leave>", self._handle_leave)

        self._apply_state_style()

    def _handle_click(self, _event=None):
        if callable(self.on_activate):
            self.on_activate()

    def _handle_enter(self, _event=None):
        self.canvas.configure(cursor="hand2")
        if self.state == "IDLE":
            self.canvas.itemconfig(
                self.inner_core,
                outline=TURQUOISE,
                width=4
            )

    def _handle_leave(self, _event=None):
        self.canvas.configure(cursor="")
        self._apply_state_style()

    def set_state(self, state):
        state = str(state).upper().strip()
        if state not in {"IDLE", "LISTENING", "THINKING", "SPEAKING"}:
            state = "IDLE"

        self.state = state

        self.speed = {
            "IDLE":      list(self.base_speed),
            "LISTENING": [0.32, -0.24, 0.42, -0.18, 0.27, -0.13],
            "THINKING":  [0.82, -0.64, 0.98, -0.52, 0.71, -0.38],
            "SPEAKING":  [0.40, -0.30, 0.50, -0.24, 0.35, -0.18],
        }[state]

        self._apply_state_style()

    def _apply_state_style(self):
        styles = {
            "IDLE":      (ORANGE, ORANGE_L, ORANGE_D),
            "LISTENING": (TURQUOISE, "#75fff7", TURQUOISE_D),
            "THINKING":  (ORANGE_L, "#ffd166", ORANGE),
            "SPEAKING":  (GREEN, "#8cffbd", TURQUOISE),
        }

        primary, bright, dim = styles[self.state]

        self.canvas.itemconfig(
            self.outer_core,
            outline=dim
        )
        # mid_core permanece oculto intencionalmente.
        self.canvas.itemconfig(
            self.inner_core,
            fill=primary,
            outline=bright,
            width=4 if self.state != "IDLE" else 3
        )
        self.canvas.itemconfig(
            self.center_core,
            fill=bright
        )

    def _animate_pulse(self):
        # Respiración profunda y lenta.
        # La esfera exterior se contrae casi hasta tocar la esfera central
        # y después vuelve a expandirse suavemente.
        self.pulse_phase += 0.022

        # 0 -> 1 con curva suave.
        breath = (math.sin(self.pulse_phase) + 1.0) / 2.0
        smooth = breath * breath * (3.0 - 2.0 * breath)

        cx, cy, r = self.cx, self.cy, self.base_r

        # Esfera central pequeña: casi estable.
        center_min = r * 0.100
        center_max = r * 0.112
        center_r = center_min + (center_max - center_min) * smooth

        # Esfera grande: contracción muy visible.
        # Mínimo apenas mayor que la esfera central.
        inner_min = r * 0.125
        inner_max = r * 0.245

        # LISTENING/SPEAKING tienen una expansión ligeramente mayor.
        if self.state == "LISTENING":
            inner_max = r * 0.260
        elif self.state == "THINKING":
            inner_max = r * 0.235
        elif self.state == "SPEAKING":
            inner_max = r * 0.270

        inner_r = inner_min + (inner_max - inner_min) * smooth

        self.canvas.coords(
            self.inner_core,
            cx-inner_r, cy-inner_r,
            cx+inner_r, cy+inner_r
        )
        self.canvas.coords(
            self.center_core,
            cx-center_r, cy-center_r,
            cx+center_r, cy+center_r
        )

    def animate(self):
        for ring_id, idx, extent in self.rings:
            self.angle[idx] = (
                self.angle[idx] + self.speed[idx]
            ) % 360

            offset = 0 if ring_id == self.rings[idx*2][0] else 180
            self.canvas.itemconfig(
                ring_id,
                start=(self.angle[idx] + offset) % 360,
                extent=extent
            )

        self._animate_pulse()


# ============================================================
# AUTENTICACIÓN LOCAL ULTRON
# ============================================================
AUTH_DIR = os.path.join(os.path.expanduser("~"), ".ultron")
AUTH_DB = os.path.join(AUTH_DIR, "users.db")
SESSION_FILE = os.path.join(AUTH_DIR, "session.json")
GROQ_KEYS_FILE = os.path.join(AUTH_DIR, "groq_keys.json")
GROQ_KEY_URL = "https://console.groq.com/keys"
GROQ_KEYRING_SERVICE = "ULTRON Panel / Groq API"


def _secure_keyring():
    """Return only supported OS credential stores, never a plaintext backend."""
    try:
        import keyring

        backend = keyring.get_keyring()
        backend_name = type(backend).__module__.casefold()
        is_supported = (
            os.name == "nt" and "windows" in backend_name
        ) or (
            os.name != "nt"
            and ("secretservice" in backend_name or "kwallet" in backend_name)
        )
        return keyring if is_supported and getattr(backend, "priority", 0) > 0 else None
    except Exception:
        return None


def _windows_dpapi(data, decrypt=False):
    """Protect data for the current Windows account using DPAPI."""
    if os.name != "nt":
        raise RuntimeError("DPAPI solo está disponible en Windows.")

    class DataBlob(ctypes.Structure):
        _fields_ = [
            ("cbData", wintypes.DWORD),
            ("pbData", ctypes.POINTER(ctypes.c_ubyte)),
        ]

    source_buffer = (ctypes.c_ubyte * len(data)).from_buffer_copy(data)
    source = DataBlob(
        len(data), ctypes.cast(source_buffer, ctypes.POINTER(ctypes.c_ubyte))
    )
    result = DataBlob()
    crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    if decrypt:
        description = wintypes.LPWSTR()
        function = crypt32.CryptUnprotectData
        function.argtypes = [
            ctypes.POINTER(DataBlob), ctypes.POINTER(wintypes.LPWSTR),
            ctypes.POINTER(DataBlob), ctypes.c_void_p, ctypes.c_void_p,
            wintypes.DWORD, ctypes.POINTER(DataBlob),
        ]
        succeeded = function(
            ctypes.byref(source), ctypes.byref(description), None,
            None, None, 0x1, ctypes.byref(result),
        )
    else:
        function = crypt32.CryptProtectData
        function.argtypes = [
            ctypes.POINTER(DataBlob), wintypes.LPCWSTR, ctypes.POINTER(DataBlob),
            ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD,
            ctypes.POINTER(DataBlob),
        ]
        succeeded = function(
            ctypes.byref(source), "ULTRON Groq API key", None,
            None, None, 0x1, ctypes.byref(result),
        )
    if not succeeded:
        raise ctypes.WinError(ctypes.get_last_error())

    try:
        return ctypes.string_at(result.pbData, result.cbData)
    finally:
        kernel32.LocalFree.argtypes = [ctypes.c_void_p]
        kernel32.LocalFree.restype = ctypes.c_void_p
        kernel32.LocalFree(ctypes.cast(result.pbData, ctypes.c_void_p))
        if decrypt and description:
            kernel32.LocalFree(ctypes.cast(description, ctypes.c_void_p))


def _read_legacy_groq_keys():
    try:
        if os.name != "nt":
            os.chmod(AUTH_DIR, 0o700)
            if os.path.exists(GROQ_KEYS_FILE):
                os.chmod(GROQ_KEYS_FILE, 0o600)
        with open(GROQ_KEYS_FILE, "r", encoding="utf-8") as key_file:
            keys = json.load(key_file)
        if not isinstance(keys, dict):
            return {}
        for account, stored in list(keys.items()):
            if isinstance(stored, dict) and isinstance(stored.get("dpapi"), str):
                encrypted = base64.b64decode(stored["dpapi"], validate=True)
                keys[account] = _windows_dpapi(encrypted, decrypt=True).decode("utf-8")
            elif isinstance(stored, dict):
                keys.pop(account, None)
        return keys
    except (OSError, ValueError, TypeError):
        return {}


def _write_legacy_groq_keys(keys):
    if not keys:
        try:
            os.remove(GROQ_KEYS_FILE)
        except FileNotFoundError:
            pass
        return
    os.makedirs(AUTH_DIR, mode=0o700, exist_ok=True)
    try:
        os.chmod(AUTH_DIR, 0o700)
    except OSError:
        pass
    temporary_file = GROQ_KEYS_FILE + "." + uuid.uuid4().hex + ".tmp"
    stored_keys = {
        account: (
            {"dpapi": base64.b64encode(
                _windows_dpapi(value.encode("utf-8"))
            ).decode("ascii")}
            if os.name == "nt" and isinstance(value, str)
            else value
        )
        for account, value in keys.items()
    }
    descriptor = os.open(
        temporary_file,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL,
        0o600,
    )
    with os.fdopen(descriptor, "w", encoding="utf-8") as key_file:
        json.dump(stored_keys, key_file, indent=2)
    os.replace(temporary_file, GROQ_KEYS_FILE)


def _load_groq_key(username):
    account = username.casefold()
    keyring = _secure_keyring()
    if keyring:
        try:
            value = keyring.get_password(GROQ_KEYRING_SERVICE, account)
            if value:
                return value
        except Exception:
            pass

    # Import keys saved by older versions, then migrate and erase each plaintext
    # entry as soon as the OS credential manager accepts it.
    keys = _read_legacy_groq_keys()
    value = keys.get(account, "")
    if value and keyring:
        try:
            keyring.set_password(GROQ_KEYRING_SERVICE, account, value)
            keys.pop(account, None)
            _write_legacy_groq_keys(keys)
        except Exception:
            if os.name == "nt":
                try:
                    _write_legacy_groq_keys(keys)
                except Exception:
                    pass
    elif value and os.name == "nt":
        try:
            _write_legacy_groq_keys(keys)
        except Exception:
            pass
    return value


def _save_groq_key(username, api_key):
    account = username.casefold()
    keyring = _secure_keyring()
    if keyring:
        try:
            keyring.set_password(GROQ_KEYRING_SERVICE, account, api_key)
        except Exception:
            pass
        else:
            keys = _read_legacy_groq_keys()
            if account in keys:
                keys.pop(account, None)
                try:
                    _write_legacy_groq_keys(keys)
                except OSError:
                    pass
            return "almacén seguro del sistema"

    # Keep desktops usable without a keyring: Windows uses per-account DPAPI;
    # Linux uses a private 0600 file when Secret Service/KWallet is absent.
    keys = _read_legacy_groq_keys()
    keys[account] = api_key
    _write_legacy_groq_keys(keys)
    if os.name == "nt":
        return "archivo local cifrado con DPAPI para tu cuenta de Windows"
    return "archivo local con permisos restringidos (sin almacén seguro disponible)"


def _delete_groq_key(username):
    account = username.casefold()
    keyring = _secure_keyring()
    keyring_read_error = None
    if keyring:
        try:
            stored = keyring.get_password(GROQ_KEYRING_SERVICE, account)
        except Exception as exc:
            keyring_read_error = exc
            stored = None
        if stored:
            try:
                keyring.delete_password(GROQ_KEYRING_SERVICE, account)
            except Exception as exc:
                raise RuntimeError(
                    "No se pudo borrar la clave del almacén del sistema."
                ) from exc
    keys = _read_legacy_groq_keys()
    if keyring_read_error and account not in keys:
        raise RuntimeError(
            "No se pudo comprobar la clave en el almacén del sistema."
        ) from keyring_read_error
    if account in keys:
        keys.pop(account, None)
        _write_legacy_groq_keys(keys)


def _normalize_groq_api_key(value):
    """Acepta la clave sola o pegada desde una variable/comando común."""
    api_key = str(value or "").strip()
    if api_key.casefold().startswith("authorization:"):
        api_key = api_key.split(":", 1)[1].strip()
    if api_key.casefold().startswith("bearer "):
        api_key = api_key[7:].strip()
    if api_key.casefold().startswith("groq_api_key="):
        api_key = api_key.split("=", 1)[1].strip()
    api_key = api_key.strip().strip("\"'")
    # Las API keys no contienen espacios; elimina saltos de línea introducidos
    # al copiar desde una terminal o un documento.
    return "".join(api_key.split())


def _validate_groq_api_key(api_key, timeout=6):
    request = urllib.request.Request(
        "https://api.groq.com/openai/v1/models",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            # Avoid urllib's default Python-urllib signature, which Groq's
            # edge protection may block before it can validate credentials.
            "User-Agent": "ULTRON-Core/3.0",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if isinstance(payload, dict) and isinstance(payload.get("data"), list):
            return "valid", "Clave validada con Groq."
        return "unverified", "Groq respondió en un formato inesperado."
    except urllib.error.HTTPError as exc:
        if exc.code == 401:
            return "invalid", "Groq rechazó la clave. Revisa que esté completa y activa."
        if exc.code == 403:
            try:
                error_body = exc.read(2048).decode("utf-8", errors="replace")
                error_data = json.loads(error_body)
            except (OSError, ValueError, UnicodeDecodeError):
                error_data = {}
            if error_data.get("error_code") == 1010:
                return (
                    "unverified",
                    "Cloudflare bloqueó la comprobación de ULTRON (error 1010); "
                    "esto no significa que tu clave sea inválida. La guardaré y "
                    "ULTRON la comprobará al conectar con Groq.",
                )
            return (
                "unverified",
                "Groq no autorizó la comprobación (HTTP 403); no se pudo "
                "confirmar si la clave es válida.",
            )
        if exc.code == 429:
            return "unverified", "Groq limitó la comprobación. Espera un momento y reintenta."
        return "unverified", f"Groq respondió con HTTP {exc.code}."
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        reason = getattr(exc, "reason", None)
        if isinstance(reason, TimeoutError):
            return "unverified", "Se agotó el tiempo al conectar con Groq."
        return "unverified", "No se pudo conectar con Groq. Revisa tu conexión e inténtalo otra vez."
    except (ValueError, UnicodeDecodeError):
        return "unverified", "Groq respondió con datos que no se pudieron leer."


def _format_recovery_code(code):
    return " ".join(code[index:index + 4] for index in range(0, len(code), 4))


def _show_recovery_code(parent, username, code):
    dialog = tk.Toplevel(parent)
    dialog.title("ULTRON // CÓDIGO DE RECUPERACIÓN")
    dialog.configure(bg=BG)
    dialog.resizable(False, False)
    dialog.transient(parent)
    dialog.grab_set()
    dialog.geometry("500x290")

    body = tk.Frame(dialog, bg=BG)
    body.pack(fill=tk.BOTH, expand=True, padx=22, pady=20)
    tk.Label(
        body,
        text="GUARDA TU CÓDIGO DE RECUPERACIÓN",
        fg=ORANGE,
        bg=BG,
        font=("Segoe UI", 13, "bold"),
    ).pack(anchor="w")
    tk.Label(
        body,
        text=(
            f"Este código permite restablecer la contraseña de {username}. "
            "Solo se mostrará ahora. Guárdalo en un lugar seguro."
        ),
        fg=TEXT,
        bg=BG,
        font=("Segoe UI", 9),
        wraplength=450,
        justify="left",
    ).pack(anchor="w", pady=(9, 14))

    code_var = tk.StringVar(value=_format_recovery_code(code))
    code_entry = tk.Entry(
        body,
        textvariable=code_var,
        state="readonly",
        justify="center",
        bg=BG_PANEL2,
        fg=TURQUOISE,
        readonlybackground=BG_PANEL2,
        relief=tk.FLAT,
        font=("Consolas", 14, "bold"),
    )
    code_entry.pack(fill=tk.X, ipady=10)

    status = tk.Label(body, text="", fg=TURQUOISE, bg=BG,
                      font=("Segoe UI", 9))
    status.pack(anchor="w", pady=(7, 0))

    buttons = tk.Frame(body, bg=BG)
    buttons.pack(fill=tk.X, side=tk.BOTTOM)

    def copy_code():
        dialog.clipboard_clear()
        dialog.clipboard_append(code)
        status.configure(text="Código copiado al portapapeles.")

    def close_dialog():
        try:
            dialog.grab_release()
        except tk.TclError:
            pass
        dialog.destroy()

    tk.Button(
        buttons, text="COPIAR CÓDIGO", command=copy_code,
        fg=BG, bg=TURQUOISE, activebackground=TURQUOISE_D,
        relief=tk.FLAT, font=("Segoe UI", 9, "bold"), padx=12, pady=8,
    ).pack(side=tk.LEFT)
    tk.Button(
        buttons, text="CONTINUAR", command=close_dialog,
        fg=BG, bg=ORANGE, activebackground=ORANGE_L,
        relief=tk.FLAT, font=("Segoe UI", 9, "bold"), padx=12, pady=8,
    ).pack(side=tk.RIGHT)

    dialog.protocol("WM_DELETE_WINDOW", lambda: None)
    dialog.wait_window()


def _list_registered_users():
    if not os.path.exists(AUTH_DB):
        return []
    try:
        with sqlite3.connect(AUTH_DB) as db:
            rows = db.execute(
                "SELECT username FROM users ORDER BY username COLLATE NOCASE"
            ).fetchall()
        return [row[0] for row in rows]
    except sqlite3.Error:
        return []


def _delete_registered_user(username):
    # Remove secrets first. If the OS credential manager is unavailable, keep
    # the account intact instead of orphaning a Groq key under its username.
    _delete_groq_key(username)
    with sqlite3.connect(AUTH_DB) as db:
        db.execute(
            "DELETE FROM users WHERE username = ? COLLATE NOCASE",
            (username,),
        )

    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as session_file:
            session = json.load(session_file)
        if session.get("username", "").casefold() == username.casefold():
            os.remove(SESSION_FILE)
    except (OSError, ValueError, AttributeError):
        pass


class UltronUserPicker:
    """Selector de cuentas que abre el inicio de sesión o el registro."""

    def __init__(self, root, active_username=""):
        self.action = None
        self.username = None
        self.active_username = active_username.casefold()
        self.deleted_active_user = False
        self.win = tk.Toplevel(root)
        self.win.title("ULTRON // USUARIOS")
        self.win.configure(bg=BG)
        self.win.resizable(False, False)
        self.win.transient(root)

        width, height = 470, 510
        screen_w = self.win.winfo_screenwidth()
        screen_h = self.win.winfo_screenheight()
        x = max(0, (screen_w - width) // 2)
        y = max(0, (screen_h - height) // 2)
        self.win.geometry(f"{width}x{height}+{x}+{y}")

        content = tk.Frame(self.win, bg=BG)
        content.pack(fill=tk.BOTH, expand=True, padx=22, pady=20)
        tk.Label(
            content,
            text="¿QUIÉN VA A USAR ULTRON?",
            fg=ORANGE,
            bg=BG,
            font=("Segoe UI", 15, "bold"),
        ).pack(anchor="w", pady=(0, 12))

        list_shell = tk.Frame(
            content, bg=BG_PANEL, highlightthickness=1,
            highlightbackground=GRAY2,
        )
        list_shell.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(
            list_shell, bg=BG_PANEL, highlightthickness=0,
        )
        scrollbar = tk.Scrollbar(
            list_shell, orient=tk.VERTICAL, command=canvas.yview,
        )
        users_frame = tk.Frame(canvas, bg=BG_PANEL)
        self.users_frame = users_frame
        self.user_rows = {}
        self.empty_users_label = None
        users_frame.bind(
            "<Configure>",
            lambda _event: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=users_frame, anchor="nw", tags="users")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0), pady=8)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5), pady=8)
        canvas.bind(
            "<Configure>",
            lambda event: canvas.itemconfigure("users", width=event.width),
        )

        users = _list_registered_users()
        if not users:
            self.empty_users_label = tk.Label(
                users_frame,
                text="Todavía no hay usuarios. Crea una cuenta para empezar.",
                fg=TEXT_DIM,
                bg=BG_PANEL,
                font=("Segoe UI", 10),
                wraplength=365,
                justify="left",
            )
            self.empty_users_label.pack(anchor="w", padx=12, pady=14)

        for username in users:
            row = tk.Frame(
                users_frame, bg=BG_PANEL2, cursor="hand2",
                highlightthickness=1, highlightbackground=GRAY,
            )
            row.pack(fill=tk.X, padx=6, pady=4)
            self.user_rows[username.casefold()] = row
            avatar = tk.Canvas(
                row, width=40, height=40, bg=BG_PANEL2,
                highlightthickness=0, cursor="hand2",
            )
            avatar.pack(side=tk.LEFT, padx=(10, 8), pady=6)
            avatar.create_oval(3, 3, 37, 37, fill=ORANGE_DIM, outline=ORANGE_D)
            avatar.create_oval(15, 9, 25, 19, fill=ORANGE, outline=ORANGE)
            avatar.create_arc(
                10, 17, 30, 34, start=0, extent=180,
                style=tk.PIESLICE, fill=ORANGE, outline=ORANGE,
            )
            label = tk.Label(
                row, text=username, fg=TEXT, bg=BG_PANEL2,
                font=("Segoe UI", 11, "bold"), anchor="w", cursor="hand2",
            )
            label.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=10)
            arrow = tk.Label(
                row, text="›", fg=TURQUOISE, bg=BG_PANEL2,
                font=("Segoe UI", 20), cursor="hand2",
            )
            arrow.pack(side=tk.RIGHT, padx=12)

            remove_btn = tk.Button(
                row,
                text="×",
                command=lambda name=username: self._confirm_delete(name),
                fg=RED,
                bg=BG_PANEL2,
                activeforeground=BG,
                activebackground=RED,
                relief=tk.FLAT,
                font=("Segoe UI", 15, "bold"),
                width=3,
                cursor="hand2",
            )
            remove_btn.pack(side=tk.RIGHT, padx=(0, 8), pady=5)

            def choose(_event=None, selected=username):
                self.username = selected
                self.action = "login"
                self.win.destroy()

            for widget in (row, avatar, label, arrow):
                widget.bind("<Button-1>", choose)
                widget.bind(
                    "<Enter>",
                    lambda _event, frame=row: frame.configure(bg=GRAY),
                )
                widget.bind(
                    "<Leave>",
                    lambda _event, frame=row: frame.configure(bg=BG_PANEL2),
                )

        buttons = tk.Frame(content, bg=BG)
        buttons.pack(fill=tk.X, pady=(14, 0))

        def choose_action(action):
            self.action = action
            self.win.destroy()

        tk.Button(
            buttons,
            text="INICIAR SESIÓN",
            command=lambda: choose_action("login"),
            fg=BG,
            bg=TURQUOISE,
            activebackground=TURQUOISE_D,
            relief=tk.FLAT,
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=9,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        tk.Button(
            buttons,
            text="CREAR USUARIO",
            command=lambda: choose_action("register"),
            fg=BG,
            bg=ORANGE,
            activebackground=ORANGE_L,
            relief=tk.FLAT,
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=9,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        self.win.protocol("WM_DELETE_WINDOW", self.win.destroy)
        self.win.grab_set()
        self.win.focus_force()

    def _confirm_delete(self, username):
        from tkinter import messagebox

        confirmed = messagebox.askyesno(
            "ULTRON // ELIMINAR USUARIO",
            (
                f"¿Eliminar completamente el usuario «{username}»?\n\n"
                "Se borrarán su cuenta local, su API key de Groq y su sesión "
                "recordada. Esta acción no se puede deshacer."
                + (
                    "\n\nEs la cuenta activa. ULTRON se cerrará al eliminarla."
                    if username.casefold() == self.active_username else ""
                )
            ),
            icon="warning",
            parent=self.win,
        )
        if not confirmed:
            return

        try:
            _delete_registered_user(username)
        except Exception as exc:
            messagebox.showerror(
                "ULTRON // ERROR",
                f"No se pudo eliminar el usuario:\n{exc}",
                parent=self.win,
            )
            return

        if username.casefold() == self.active_username:
            self.deleted_active_user = True
            # No permitir que el panel siga abierto con una cuenta ya borrada.
            self.win.destroy()
            return

        row = self.user_rows.pop(username.casefold(), None)
        if row is not None:
            row.destroy()
        if not self.user_rows:
            if self.empty_users_label is None:
                self.empty_users_label = tk.Label(
                    self.users_frame,
                    text="Todavía no hay usuarios. Crea una cuenta para empezar.",
                    fg=TEXT_DIM,
                    bg=BG_PANEL,
                    font=("Segoe UI", 10),
                    wraplength=365,
                    justify="left",
                )
                self.empty_users_label.pack(anchor="w", padx=12, pady=14)


class UltronAuth:
    def __init__(self, root, initial_mode="login", initial_username=""):
        self.root = root
        self.system = create_bridge()
        self.authenticated = False
        self.username = None
        self.failed_attempts = 0
        self.remember_var = tk.BooleanVar(value=True)

        os.makedirs(AUTH_DIR, exist_ok=True)
        try:
            os.chmod(AUTH_DIR, 0o700)
        except Exception:
            pass

        self.db = sqlite3.connect(AUTH_DB)
        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                salt BLOB NOT NULL,
                password_hash BLOB NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.db.commit()

        # Migración suave para sesiones persistentes.
        columns = {
            row[1] for row in self.db.execute("PRAGMA table_info(users)").fetchall()
        }
        if "session_hash" not in columns:
            self.db.execute("ALTER TABLE users ADD COLUMN session_hash BLOB")
            self.db.commit()
            columns.add("session_hash")
        if "recovery_salt" not in columns:
            self.db.execute("ALTER TABLE users ADD COLUMN recovery_salt BLOB")
        if "recovery_hash" not in columns:
            self.db.execute("ALTER TABLE users ADD COLUMN recovery_hash BLOB")
        self.db.commit()

        self.win = tk.Toplevel(root)
        self.win.title("ULTRON // ACCESS")
        self.win.configure(bg=BG)
        # Ventana compacta, centrada y siempre dentro de la pantalla.
        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()

        win_w = min(500, max(420, sw - 80))
        win_h = min(500, max(420, sh - 100))

        x = max(0, (sw - win_w) // 2)
        y = max(0, (sh - win_h) // 2)

        self.win.geometry(f"{win_w}x{win_h}+{x}+{y}")
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self._cancel)

        self.mode = tk.StringVar(value=initial_mode)
        self.registered_username = None
        self.user_var = tk.StringVar()
        self.pass_var = tk.StringVar()
        self.pass2_var = tk.StringVar()
        self.status_var = tk.StringVar(value="")
        self.user_var.set(initial_username)

        self._build()

        self.win.grab_set()
        self.win.focus_force()

    def _build(self):
        top = tk.Frame(self.win, bg=BG_PANEL2, height=54)
        top.pack(fill=tk.X)
        top.pack_propagate(False)

        tk.Label(
            top,
            text="ULTRON // ACCESS CONTROL",
            font=("Segoe UI", 13, "bold"),
            fg=ORANGE,
            bg=BG_PANEL2
        ).pack(side=tk.LEFT, padx=16, pady=14)

        body = tk.Frame(self.win, bg=BG)
        body.pack(fill=tk.BOTH, expand=True, padx=24, pady=18)

        # Selector de modo.
        mode_row = tk.Frame(body, bg=BG)
        mode_row.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))

        self.login_mode_btn = tk.Button(
            mode_row,
            text="INICIAR SESIÓN",
            command=lambda: self._set_mode("login"),
            fg=TURQUOISE,
            bg=BG_PANEL2,
            activeforeground=BG,
            activebackground=TURQUOISE,
            relief=tk.FLAT,
            font=("Segoe UI", 9, "bold"),
            padx=11,
            pady=7
        )
        self.login_mode_btn.pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True)

        self.register_mode_btn = tk.Button(
            mode_row,
            text="CREAR USUARIO",
            command=lambda: self._set_mode("register"),
            fg=ORANGE,
            bg=BG_PANEL2,
            activeforeground=BG,
            activebackground=ORANGE,
            relief=tk.FLAT,
            font=("Segoe UI", 9, "bold"),
            padx=11,
            pady=7
        )
        self.register_mode_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Usuario.
        tk.Label(
            body,
            text="USUARIO",
            fg=TEXT_DIM,
            bg=BG,
            font=("Segoe UI", 9)
        ).grid(row=1, column=0, columnspan=2, sticky="w")

        self.user_entry = tk.Entry(
            body,
            textvariable=self.user_var,
            bg=BG_PANEL2,
            fg=TEXT,
            insertbackground=ORANGE,
            relief=tk.FLAT,
            font=("Consolas", 11)
        )
        self.user_entry.grid(
            row=2, column=0, columnspan=2,
            sticky="ew", ipady=7, pady=(3, 11)
        )

        # Contraseña.
        tk.Label(
            body,
            text="CONTRASEÑA",
            fg=TEXT_DIM,
            bg=BG,
            font=("Segoe UI", 9)
        ).grid(row=3, column=0, columnspan=2, sticky="w")

        self.pass_entry = tk.Entry(
            body,
            textvariable=self.pass_var,
            show="",
            bg=BG_PANEL2,
            fg=TEXT,
            insertbackground=ORANGE,
            relief=tk.FLAT,
            font=("Consolas", 11)
        )
        self.pass_entry.grid(
            row=4, column=0, columnspan=2,
            sticky="ew", ipady=7, pady=(3, 11)
        )

        # Confirmación: justo debajo de contraseña.
        self.confirm_label = tk.Label(
            body,
            text="CONFIRMAR CONTRASEÑA",
            fg=TEXT_DIM,
            bg=BG,
            font=("Segoe UI", 9)
        )

        self.confirm_entry = tk.Entry(
            body,
            textvariable=self.pass2_var,
            show="",
            bg=BG_PANEL2,
            fg=TEXT,
            insertbackground=ORANGE,
            relief=tk.FLAT,
            font=("Consolas", 11)
        )

        self.confirm_label.grid(
            row=5, column=0, columnspan=2,
            sticky="w"
        )
        self.confirm_entry.grid(
            row=6, column=0, columnspan=2,
            sticky="ew", ipady=7, pady=(3, 11)
        )

        # "Recordarme" personalizado: texto y casilla más grandes,
        # con marca naranja para mantener el estilo ULTRON.
        self.remember_row = tk.Frame(body, bg=BG)
        self.remember_row.grid(
            row=7, column=0, columnspan=2,
            sticky="w", pady=(3, 9)
        )

        self.remember_box = tk.Canvas(
            self.remember_row,
            width=25,
            height=25,
            bg=BG,
            highlightthickness=0,
            cursor="hand2"
        )
        self.remember_box.pack(side=tk.LEFT, padx=(0, 9))

        self.remember_text = tk.Label(
            self.remember_row,
            text="Recordarme en este equipo",
            fg=TEXT,
            bg=BG,
            font=("Segoe UI", 11),
            cursor="hand2"
        )
        self.remember_text.pack(side=tk.LEFT)

        def toggle_remember(_event=None):
            self.remember_var.set(not self.remember_var.get())
            draw_remember_box()

        def draw_remember_box(*_args):
            self.remember_box.delete("all")
            self.remember_box.create_rectangle(
                3, 3, 22, 22,
                outline=ORANGE,
                width=2,
                fill=BG_PANEL2
            )

            if self.remember_var.get():
                # Marca/flechita naranja, más grande y visible.
                self.remember_box.create_line(
                    7, 13,
                    11, 17,
                    19, 8,
                    fill=ORANGE,
                    width=3,
                    capstyle=tk.ROUND,
                    joinstyle=tk.ROUND
                )

        self.remember_box.bind("<Button-1>", toggle_remember)
        self.remember_text.bind("<Button-1>", toggle_remember)
        self.remember_var.trace_add("write", draw_remember_box)
        draw_remember_box()

        # Botón SIEMPRE al final.
        self.action_btn = tk.Button(
            body,
            text="[ ENTRAR ]",
            command=self._submit,
            fg=ORANGE,
            bg=BG_PANEL2,
            activeforeground=ORANGE_L,
            activebackground=GRAY,
            relief=tk.FLAT,
            font=("Segoe UI", 10, "bold"),
            padx=14,
            pady=9
        )
        self.action_btn.grid(
            row=8, column=0,
            sticky="ew", pady=(5, 8)
        )

        self.recovery_btn = tk.Button(
            body,
            text="RECUPERAR ACCESO",
            command=self._open_password_recovery,
            fg=TURQUOISE,
            bg=BG_PANEL2,
            activebackground=GRAY,
            relief=tk.FLAT,
            font=("Segoe UI", 8, "bold"),
            padx=8,
            pady=9,
        )
        self.recovery_btn.grid(row=8, column=1, sticky="ew", pady=(5, 8))

        self.show_recovery_btn = tk.Button(
            body,
            text="VER CÓDIGO GUARDADO",
            command=self._show_saved_recovery_code,
            fg=ORANGE,
            bg=BG_PANEL2,
            activebackground=GRAY,
            relief=tk.FLAT,
            font=("Segoe UI", 8, "bold"),
            padx=8,
            pady=7,
        )
        self.show_recovery_btn.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(0, 5))

        self.status_label = tk.Label(
            body,
            textvariable=self.status_var,
            fg=RED,
            bg=BG,
            font=("Segoe UI", 9),
            wraplength=420,
            justify="left"
        )
        self.status_label.grid(
            row=10, column=0, columnspan=2,
            sticky="w", pady=(3, 0)
        )

        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)

        self.user_entry.bind("<Return>", lambda _e: self._submit())
        self.pass_entry.bind("<Return>", lambda _e: self._submit())
        self.confirm_entry.bind("<Return>", lambda _e: self._submit())

        self._set_mode(self.mode.get())
        self.user_entry.focus_set()

    def _set_mode(self, mode):
        self.mode.set(mode)
        self.status_var.set("")
        self.pass_var.set("")
        self.pass2_var.set("")

        if mode == "register":
            self.login_mode_btn.configure(
                fg=TURQUOISE,
                bg=BG_PANEL2,
                relief=tk.FLAT,
                highlightthickness=0,
            )
            self.register_mode_btn.configure(
                fg=BG,
                bg=ORANGE,
                relief=tk.SOLID,
                highlightbackground=ORANGE_L,
                highlightcolor=ORANGE_L,
                highlightthickness=1,
            )
        else:
            self.login_mode_btn.configure(
                fg=BG,
                bg=TURQUOISE,
                relief=tk.SOLID,
                highlightbackground=TURQUOISE,
                highlightcolor=TURQUOISE,
                highlightthickness=1,
            )
            self.register_mode_btn.configure(
                fg=ORANGE,
                bg=BG_PANEL2,
                relief=tk.FLAT,
                highlightthickness=0,
            )

        if mode == "register":
            self.action_btn.grid_configure(column=0, columnspan=2)
            self.recovery_btn.grid_remove()
            self.show_recovery_btn.grid_remove()
            self.confirm_label.grid()
            self.confirm_entry.grid()
            self.action_btn.configure(text="[ CREAR USUARIO ]")
        else:
            self.action_btn.grid_configure(column=0, columnspan=1)
            self.recovery_btn.grid()
            self.show_recovery_btn.grid()
            self.confirm_label.grid_remove()
            self.confirm_entry.grid_remove()
            self.action_btn.configure(text="[ ENTRAR ]")

    def _hash_password(self, password, salt):
        return hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=2**14,
            r=8,
            p=1,
            dklen=32
        )

    def _show_saved_recovery_code(self):
        username = self.user_var.get().strip()
        row = self.db.execute(
            "SELECT recovery_salt, recovery_hash FROM users "
            "WHERE username = ? COLLATE NOCASE",
            (username,),
        ).fetchone()
        if not row:
            self.status_var.set("Escribe el nombre de una cuenta existente.")
            return
        if not row[0] or not row[1]:
            self.status_var.set(
                "Esta cuenta no tiene código. Inicia sesión para generar uno nuevo."
            )
            return

        confirm = tk.Toplevel(self.win)
        confirm.title("ULTRON // VERIFICAR IDENTIDAD")
        confirm.configure(bg=BG)
        confirm.resizable(False, False)
        confirm.transient(self.win)
        confirm.grab_set()
        confirm.geometry("410x190")
        body = tk.Frame(confirm, bg=BG)
        body.pack(fill=tk.BOTH, expand=True, padx=20, pady=18)
        tk.Label(
            body, text=(
                "El código original no se puede recuperar porque se guarda de "
                "forma protegida. Confirma tu contraseña para generar uno nuevo; "
                "el anterior dejará de funcionar."
            ),
            fg=TEXT, bg=BG, font=("Segoe UI", 10), wraplength=370,
        ).pack(anchor="w", pady=(0, 10))
        password_var = tk.StringVar()
        password_entry = tk.Entry(
            body, textvariable=password_var, show="•", bg=BG_PANEL2,
            fg=TEXT, insertbackground=ORANGE, relief=tk.FLAT,
        )
        password_entry.pack(fill=tk.X, ipady=7)
        status = tk.Label(body, text="", fg=RED, bg=BG, font=("Segoe UI", 9))
        status.pack(anchor="w", pady=5)

        def verify():
            row = self.db.execute(
                "SELECT salt, password_hash FROM users "
                "WHERE username = ? COLLATE NOCASE",
                (username,),
            ).fetchone()
            if not row or not secrets.compare_digest(
                self._hash_password(password_var.get(), row[0]), row[1]
            ):
                status.configure(text="Contraseña incorrecta.")
                return
            new_code = secrets.token_hex(16).upper()
            new_salt = secrets.token_bytes(16)
            new_hash = self._hash_password(new_code, new_salt)
            self.db.execute(
                "UPDATE users SET recovery_salt = ?, recovery_hash = ? "
                "WHERE username = ? COLLATE NOCASE",
                (new_salt, new_hash, username),
            )
            self.db.commit()
            confirm.grab_release()
            confirm.destroy()
            _show_recovery_code(self.win, username, new_code)

        tk.Button(
            body, text="CERRAR", command=confirm.destroy,
            fg=TEXT, bg=BG_PANEL2, relief=tk.FLAT, padx=12, pady=7,
        ).pack(side=tk.LEFT, pady=(8, 0))
        tk.Button(
            body, text="GENERAR NUEVO CÓDIGO", command=verify,
            fg=BG, bg=ORANGE, relief=tk.FLAT, padx=12, pady=7,
        ).pack(side=tk.RIGHT, pady=(8, 0))
        password_entry.focus_set()

    def _open_password_recovery(self):
        dialog = tk.Toplevel(self.win)
        dialog.title("ULTRON // RECUPERAR ACCESO")
        dialog.configure(bg=BG)
        dialog.resizable(False, False)
        dialog.transient(self.win)
        dialog.geometry("470x400")

        body = tk.Frame(dialog, bg=BG)
        body.pack(fill=tk.BOTH, expand=True, padx=22, pady=20)
        tk.Label(
            body, text="RESTABLECER CONTRASEÑA", fg=ORANGE, bg=BG,
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        username_var = tk.StringVar(value=self.user_var.get().strip())
        code_var = tk.StringVar()
        password_var = tk.StringVar()
        confirm_var = tk.StringVar()
        fields = (
            ("USUARIO", username_var, ""),
            ("CÓDIGO DE RECUPERACIÓN", code_var, ""),
            ("NUEVA CONTRASEÑA", password_var, "•"),
            ("CONFIRMAR CONTRASEÑA", confirm_var, "•"),
        )
        for label_text, variable, mask in fields:
            tk.Label(
                body, text=label_text, fg=TEXT_DIM, bg=BG,
                font=("Segoe UI", 8, "bold"),
            ).pack(anchor="w", pady=(7, 2))
            tk.Entry(
                body, textvariable=variable, show=mask, bg=BG_PANEL2,
                fg=TEXT, insertbackground=ORANGE, relief=tk.FLAT,
                font=("Consolas", 10),
            ).pack(fill=tk.X, ipady=6)

        status = tk.Label(
            body, text="", fg=RED, bg=BG, font=("Segoe UI", 9),
            wraplength=420, justify="left",
        )
        status.pack(anchor="w", pady=(8, 0))

        def reset_password():
            username = username_var.get().strip()
            recovery_code = (
                code_var.get().strip().replace(" ", "").replace("-", "").upper()
            )
            password = password_var.get()
            if len(password) < 6:
                status.configure(text="La contraseña debe tener al menos 6 caracteres.")
                return
            if password != confirm_var.get():
                status.configure(text="Las contraseñas no coinciden.")
                return

            row = self.db.execute(
                "SELECT recovery_salt, recovery_hash FROM users "
                "WHERE username = ? COLLATE NOCASE",
                (username,),
            ).fetchone()
            if not row or not row[0] or not row[1]:
                status.configure(
                    text=(
                        "Esta cuenta aún no tiene código de recuperación. "
                        "Si olvidaste la contraseña, elimina la cuenta y créala "
                        "de nuevo desde este equipo."
                    )
                )
                return

            actual_code_hash = self._hash_password(recovery_code, row[0])
            if not secrets.compare_digest(actual_code_hash, row[1]):
                status.configure(text="Usuario o código de recuperación incorrectos.")
                return

            salt = secrets.token_bytes(16)
            password_hash = self._hash_password(password, salt)
            self.db.execute(
                "UPDATE users SET salt = ?, password_hash = ?, session_hash = NULL "
                "WHERE username = ? COLLATE NOCASE",
                (salt, password_hash, username),
            )
            self.db.commit()
            self._clear_saved_session_for(username)
            self.user_var.set(username)
            self.pass_var.set("")
            self.pass2_var.set("")
            self.status_var.set("Contraseña restablecida. Inicia sesión con la nueva.")
            status.configure(text="Contraseña actualizada. Ya puedes iniciar sesión.", fg=TURQUOISE)
            dialog.after(900, dialog.destroy)

        tk.Button(
            body, text="RESTABLECER CONTRASEÑA", command=reset_password,
            fg=BG, bg=ORANGE, activebackground=ORANGE_L, relief=tk.FLAT,
            font=("Segoe UI", 9, "bold"), padx=12, pady=8,
        ).pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))

        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
        dialog.grab_set()
        dialog.focus_force()

    @staticmethod
    def _clear_saved_session_for(username):
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as session_file:
                session = json.load(session_file)
            if session.get("username", "").casefold() == username.casefold():
                os.remove(SESSION_FILE)
        except (OSError, ValueError, AttributeError):
            pass

    def _username_exists(self, username):
        row = self.db.execute(
            "SELECT 1 FROM users WHERE username = ? COLLATE NOCASE",
            (username,)
        ).fetchone()
        return row is not None

    def _suggest_username(self, base):
        clean = "".join(ch for ch in base if ch.isalnum() or ch in "_-").strip("_-")
        clean = clean or "usuario"

        for i in range(1, 1000):
            candidate = f"{clean}{i:02d}"
            if not self._username_exists(candidate):
                return candidate

        return f"{clean}_{secrets.randbelow(9999):04d}"

    def _save_session(self, username):
        """Guarda un token local aleatorio; nunca guarda la contraseña."""
        token = secrets.token_hex(32)
        token_hash = hashlib.sha256(token.encode("utf-8")).digest()

        self.db.execute(
            "UPDATE users SET session_hash = ? WHERE username = ? COLLATE NOCASE",
            (token_hash, username)
        )
        self.db.commit()

        data = {
            "username": username,
            "token": token
        }

        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)

        try:
            os.chmod(SESSION_FILE, 0o600)
        except Exception:
            pass

    def _clear_session(self):
        try:
            if os.path.exists(SESSION_FILE):
                os.remove(SESSION_FILE)
        except Exception:
            pass

    @classmethod
    def try_saved_session(cls):
        """Valida una sesión recordada sin abrir todavía la ventana de login."""
        if not os.path.exists(SESSION_FILE) or not os.path.exists(AUTH_DB):
            return None

        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            username = data.get("username", "").strip()
            token = data.get("token", "").strip()

            if not username or not token:
                return None

            db = sqlite3.connect(AUTH_DB)
            row = db.execute(
                "SELECT session_hash FROM users WHERE username = ? COLLATE NOCASE",
                (username,)
            ).fetchone()
            db.close()

            if not row or not row[0]:
                return None

            actual = hashlib.sha256(token.encode("utf-8")).digest()

            if secrets.compare_digest(actual, row[0]):
                return username

        except Exception:
            return None

        return None

    def _register(self):
        username = self.user_var.get().strip()
        password = self.pass_var.get()
        password2 = self.pass2_var.get()

        if len(username) < 3:
            self.status_var.set("El usuario debe tener al menos 3 caracteres.")
            return

        if not all(ch.isalnum() or ch in "_-" for ch in username):
            self.status_var.set(
                "Usa solo letras, números, guion o guion bajo en el nombre."
            )
            return

        if self._username_exists(username):
            suggestion = self._suggest_username(username)
            self.status_var.set(
                f"El usuario '{username}' ya existe. Sugerencia: {suggestion}"
            )
            return

        if len(password) < 6:
            self.status_var.set("La contraseña debe tener al menos 6 caracteres.")
            return

        if password != password2:
            self.status_var.set("Las contraseñas no coinciden.")
            return

        salt = secrets.token_bytes(16)
        digest = self._hash_password(password, salt)
        recovery_code = secrets.token_hex(16).upper()
        recovery_salt = secrets.token_bytes(16)
        recovery_hash = self._hash_password(recovery_code, recovery_salt)

        try:
            self.db.execute(
                "INSERT INTO users "
                "(username, salt, password_hash, recovery_salt, recovery_hash) "
                "VALUES (?, ?, ?, ?, ?)",
                (username, salt, digest, recovery_salt, recovery_hash)
            )
            self.db.commit()
        except sqlite3.IntegrityError:
            suggestion = self._suggest_username(username)
            self.status_var.set(
                f"Ese usuario ya existe. Prueba: {suggestion}"
            )
            return

        self.status_var.set("Usuario creado. Ya puedes iniciar sesión.")
        self.registered_username = username
        self._set_mode("login")
        self.user_var.set(username)
        _show_recovery_code(self.win, username, recovery_code)
        self._show_groq_key_setup(self.win, username)

    @staticmethod
    def _show_groq_key_setup(parent, username):
        dialog = tk.Toplevel(parent)
        dialog.title("ULTRON // CONFIGURAR GROQ")
        dialog.configure(bg=BG)
        dialog.resizable(False, False)
        dialog.transient(parent)
        dialog.grab_set()

        width, height = 510, 340
        screen_w = dialog.winfo_screenwidth()
        screen_h = dialog.winfo_screenheight()
        x = max(0, (screen_w - width) // 2)
        y = max(0, (screen_h - height) // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")

        content = tk.Frame(dialog, bg=BG)
        content.pack(fill=tk.BOTH, expand=True, padx=24, pady=20)

        tk.Label(
            content,
            text="CONFIGURA TU API KEY DE GROQ",
            fg=ORANGE,
            bg=BG,
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w")
        tk.Label(
            content,
            text=(
                f"La clave será para la cuenta {username} y se guardará "
                "en el almacén de credenciales del sistema cuando esté "
                "disponible. Puedes configurarla ahora o "
                "hacerlo después."
            ),
            fg=TEXT,
            bg=BG,
            font=("Segoe UI", 10),
            wraplength=450,
            justify="left",
        ).pack(anchor="w", pady=(10, 14))

        def open_groq():
            import webbrowser
            webbrowser.open(GROQ_KEY_URL)

        tk.Button(
            content,
            text="ABRIR GROQ PARA CREAR MI API KEY",
            command=open_groq,
            fg=BG,
            bg=TURQUOISE,
            activeforeground=BG,
            activebackground=TURQUOISE_D,
            relief=tk.FLAT,
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=8,
        ).pack(anchor="w", pady=(0, 14))

        tk.Label(
            content,
            text="API KEY DE GROQ",
            fg=TEXT_DIM,
            bg=BG,
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w")
        key_var = tk.StringVar()
        key_entry = tk.Entry(
            content,
            textvariable=key_var,
            show="•",
            bg=BG_PANEL2,
            fg=TEXT,
            insertbackground=ORANGE,
            relief=tk.FLAT,
            font=("Consolas", 10),
        )
        key_entry.pack(fill=tk.X, pady=(5, 8), ipady=8)

        status = tk.Label(
            content, text="", fg=RED, bg=BG,
            font=("Segoe UI", 9), wraplength=450, justify="left",
        )
        status.pack(anchor="w")

        buttons = tk.Frame(content, bg=BG)
        buttons.pack(fill=tk.X, side=tk.BOTTOM, pady=(12, 0))

        saved = {"value": False}
        storage_info = {"value": ""}

        def finish():
            try:
                dialog.grab_release()
            except tk.TclError:
                pass
            dialog.destroy()

        def save_key():
            api_key = _normalize_groq_api_key(key_var.get())
            if not api_key:
                status.configure(text="Pega tu API key de Groq para guardarla.")
                key_entry.focus_set()
                return
            key_var.set(api_key)

            save_button.configure(state=tk.DISABLED)
            status.configure(text="Comprobando la clave con Groq...", fg=TEXT_DIM)

            def validate_and_save():
                result, message = _validate_groq_api_key(api_key)
                error = None
                if result in ("valid", "unverified"):
                    try:
                        storage_info["value"] = _save_groq_key(username, api_key)
                    except Exception as exc:
                        error = f"No se pudo guardar la clave: {exc}"

                def finish_validation():
                    if not dialog.winfo_exists():
                        return
                    if result == "invalid":
                        status.configure(text=message, fg=RED)
                        save_button.configure(state=tk.NORMAL)
                        return
                    if error:
                        status.configure(text=error, fg=RED)
                        save_button.configure(state=tk.NORMAL)
                        return
                    saved["value"] = True
                    if result == "valid":
                        confirmation = (
                            message + " Clave guardada en "
                            + storage_info["value"] + "."
                        )
                    else:
                        confirmation = (
                            message + " Guardé la clave en "
                            + storage_info["value"]
                            + "; ULTRON volverá a comprobarla al usar Conciencia."
                        )
                    status.configure(text=confirmation, fg=TURQUOISE)
                    dialog.after(800, finish)

                try:
                    dialog.after(0, finish_validation)
                except tk.TclError:
                    pass

            threading.Thread(target=validate_and_save, daemon=True).start()

        tk.Button(
            buttons,
            text="AHORA NO",
            command=finish,
            fg=TEXT,
            bg=BG_PANEL2,
            activebackground=GRAY,
            relief=tk.FLAT,
            padx=14,
            pady=8,
        ).pack(side=tk.LEFT)
        save_button = tk.Button(
            buttons,
            text="GUARDAR API KEY",
            command=save_key,
            fg=BG,
            bg=ORANGE,
            activebackground=ORANGE_L,
            relief=tk.FLAT,
            font=("Segoe UI", 9, "bold"),
            padx=14,
            pady=8,
        )
        save_button.pack(side=tk.RIGHT)

        dialog.protocol("WM_DELETE_WINDOW", finish)
        dialog.wait_window()
        return saved["value"]

    def _login(self):
        username = self.user_var.get().strip()
        password = self.pass_var.get()

        row = self.db.execute(
            "SELECT username, salt, password_hash, recovery_salt, recovery_hash "
            "FROM users "
            "WHERE username = ? COLLATE NOCASE",
            (username,)
        ).fetchone()

        if not row:
            self.failed_attempts += 1
            self.status_var.set("Usuario o contraseña incorrectos.")
            return

        saved_username, salt, expected, recovery_salt, recovery_hash = row
        actual = self._hash_password(password, salt)

        if not secrets.compare_digest(actual, expected):
            self.failed_attempts += 1
            self.status_var.set("Usuario o contraseña incorrectos.")
            return

        new_recovery_code = None
        if not recovery_salt or not recovery_hash:
            new_recovery_code = secrets.token_hex(16).upper()
            recovery_salt = secrets.token_bytes(16)
            recovery_hash = self._hash_password(new_recovery_code, recovery_salt)
            self.db.execute(
                "UPDATE users SET recovery_salt = ?, recovery_hash = ? "
                "WHERE username = ? COLLATE NOCASE",
                (recovery_salt, recovery_hash, saved_username),
            )
            self.db.commit()

        self.authenticated = True
        self.username = saved_username

        if new_recovery_code:
            _show_recovery_code(self.win, saved_username, new_recovery_code)

        if self.remember_var.get():
            self._save_session(saved_username)
        else:
            self._clear_session()

        self.win.grab_release()
        self.win.destroy()

    def _submit(self):
        if self.mode.get() == "register":
            self._register()
        else:
            self._login()

    def _cancel(self):
        self.authenticated = False
        try:
            self.win.grab_release()
        except Exception:
            pass
        self.win.destroy()


class UltronGUI:
    def __init__(self, root, current_user=""):
        self.current_user = current_user
        self.groq_api_key = _load_groq_key(current_user) if current_user else ""
        self.root = root
        self.system = create_bridge()
        self.feature_config = _load_feature_config()
        self._latest_health_metrics = {}
        self._active_alerts = {}
        self._cpu_high_since = None
        self._last_network_snapshot = None
        self._network_no_reply_count = 0
        self.root.title(f"ULTRON // CORE — {self.system.os_name()}")
        self.root.configure(bg=BG)

        # Ajuste automático al tamaño real de la pantalla.
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        self.root.geometry(f"{screen_w}x{screen_h}+0+0")
        self.root.minsize(
            min(900, screen_w),
            min(620, screen_h)
        )

        # Pantalla completa automática.
        # Escape permite salir de fullscreen si alguna vez lo necesitas.
        try:
            self.root.attributes("-fullscreen", True)
        except Exception:
            pass

        self.root.bind(
            "<Escape>",
            lambda _e: self.root.attributes("-fullscreen", False)
        )
        self.root.bind("<F8>", self._on_mic_hotkey)

        self.font_title = tkfont.Font(family="Segoe UI", size=14, weight="bold")
        self.font_label = tkfont.Font(family="Segoe UI", size=10)
        self.font_small = tkfont.Font(family="Segoe UI", size=9)
        self.font_mono  = tkfont.Font(family="Consolas", size=9)

        # CONCIENCIA / IA
        self.ai_history = [
            {
                "role": "system",
                "content": (
                    "Eres ULTRON, la conciencia integrada de un panel Windows llamado "
                    "ULTRON CORE. Habla en español de forma natural, clara y concisa. "
                    "No digas que eres Groq ni que eres otro asistente. "
                    "Si no sabes algo, dilo. No inventes resultados del sistema. "
                    "Tienes herramientas locales de ULTRON. Cuando el usuario pida información "
                    "del equipo o una acción, responde SOLO con una orden TOOL en una línea. "
                    "Formatos permitidos: TOOL:get_local_ip, TOOL:get_public_ip, "
                    "TOOL:get_wifi_name, TOOL:get_system_info, TOOL:get_memory, "
                    "TOOL:get_disk, TOOL:get_battery, TOOL:open_url:<url>, "
                    "TOOL:open_app:<nombre>. Para YouTube usa TOOL:open_url:https://www.youtube.com "
                    "y para WhatsApp Web TOOL:open_url:https://web.whatsapp.com. "
                    "Nunca inventes otras herramientas ni comandos de shell."
                )
            }
        ]
        self.ai_busy = False
        self.consciousness_active = False
        self.consciousness_generation = 0

        # PRIVACY GATE:
        # El micrófono empieza BLOQUEADO y solo se arma mediante
        # un clic real del usuario sobre el CORE.
        self.mic_authorized = False
        self.mic_process = None

        self.tts_process = None
        self.voice_record_seconds = 12
        self.voice_silence_seconds = 0.55
        self.live_transcript_var = tk.StringVar(value="")
        self.audio_input_device = None
        self.audio_output_device = None
        self.ultron_volume = 70

        self._build_ui()
        self._start_animation()
        self._update_metrics()

    def _switch_user(self):
        """Abre el selector/login para cambiar de usuario sin cerrar ULTRON."""
        # Privacidad primero: nunca dejar micrófono o voz activos durante cambio.
        self.consciousness_active = False
        self.mic_authorized = False
        self.consciousness_generation += 1
        self.ai_busy = False
        self._set_mic_indicator(False)

        try:
            self._stop_microphone_capture()
        except Exception:
            pass

        try:
            self._stop_speaking()
        except Exception:
            pass

        self._set_live_text("")
        self._set_consciousness_state(
            "IDLE",
            "● SYSTEM ONLINE",
            TURQUOISE
        )

        previous_user = self.current_user

        picker = UltronUserPicker(self.root, active_username=self.current_user)
        self.root.wait_window(picker.win)

        if picker.action is None:
            if picker.deleted_active_user:
                self.root.destroy()
                return
            self.root.lift()
            self.root.focus_force()
            return

        auth = UltronAuth(
            self.root,
            initial_mode=picker.action,
            initial_username=picker.username or "",
        )
        self.root.wait_window(auth.win)

        if not auth.authenticated:
            # Si cancela, vuelve al usuario anterior.
            if picker.deleted_active_user:
                self.root.destroy()
                return
            self.root.lift()
            self.root.focus_force()
            return

        self.current_user = auth.username
        self.groq_api_key = _load_groq_key(self.current_user)

        if hasattr(self, "user_label"):
            self.user_label.configure(
                text=f"USER: {self.current_user}"
            )

        # Nueva conversación privada por usuario.
        self.ai_history = [
            {
                "role": "system",
                "content": (
                    "Eres ULTRON, la conciencia integrada de un panel Windows llamado "
                    "ULTRON CORE. Habla en español de forma natural, clara y concisa. "
                    "No digas que eres Groq ni que eres otro asistente. "
                    "Si no sabes algo, dilo. No inventes resultados del sistema. "
                    "Tienes herramientas locales de ULTRON. Cuando el usuario pida información "
                    "del equipo o una acción, responde SOLO con una orden TOOL en una línea. "
                    "Formatos permitidos: TOOL:get_local_ip, TOOL:get_public_ip, "
                    "TOOL:get_wifi_name, TOOL:get_system_info, TOOL:get_memory, "
                    "TOOL:get_disk, TOOL:get_battery, TOOL:open_url:<url>, "
                    "TOOL:open_app:<nombre>. Para YouTube usa TOOL:open_url:https://www.youtube.com "
                    "y para WhatsApp Web TOOL:open_url:https://web.whatsapp.com. "
                    "Nunca inventes otras herramientas ni comandos de shell."
                )
            }
        ]

        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

        self._add_log(
            f"SESSION: usuario cambiado de {previous_user} a {self.current_user}"
        )

    def _build_ui(self):
        main = tk.Frame(self.root, bg=BG)
        main.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        top = tk.Frame(main, bg=BG, height=42)
        top.pack(fill=tk.X, pady=(0, 8))
        top.pack_propagate(False)

        tk.Label(top, text="ULTRON // CORE", font=self.font_title,
                 fg=ORANGE, bg=BG).pack(side=tk.LEFT, padx=8)

        self.mic_button = tk.Button(
            top,
            text="MIC · F8",
            command=self._activate_consciousness,
            font=self.font_small,
            fg=TEXT_DIM,
            bg=BG_PANEL2,
            activeforeground=BG,
            activebackground=TURQUOISE,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            padx=10,
            pady=5,
        )
        self.mic_button.pack(side=tk.LEFT, padx=(6, 0))

        self.status_label = tk.Label(
            top, text="● SYSTEM ONLINE",
            font=self.font_small, fg=TURQUOISE, bg=BG
        )
        self.status_label.pack(side=tk.RIGHT, padx=12)

        if self.current_user:
            self.user_icon = tk.Canvas(
                top,
                width=30,
                height=30,
                bg=BG,
                highlightthickness=0,
                cursor="hand2"
            )
            self.user_icon.pack(side=tk.RIGHT, padx=(0, 7))

            def draw_user_icon(active=False):
                self.user_icon.delete("all")
                color = ORANGE_L if active else ORANGE

                # Cabeza sólida
                self.user_icon.create_oval(
                    10, 3, 20, 13,
                    fill=color,
                    outline=color
                )

                # Cuerpo/hombros sólidos
                self.user_icon.create_polygon(
                    5, 27,
                    6, 21,
                    9, 17,
                    13, 15,
                    17, 15,
                    21, 17,
                    24, 21,
                    25, 27,
                    fill=color,
                    outline=color,
                    smooth=True
                )

            draw_user_icon(False)

            self.user_icon.bind(
                "<Button-1>",
                lambda _e: self._switch_user()
            )
            self.user_icon.bind(
                "<Enter>",
                lambda _e: draw_user_icon(True)
            )
            self.user_icon.bind(
                "<Leave>",
                lambda _e: draw_user_icon(False)
            )

            self.user_label = tk.Label(
                top,
                text=f"USER: {self.current_user}",
                font=self.font_small,
                fg=TEXT_DIM,
                bg=BG
            )
            self.user_label.pack(side=tk.RIGHT, padx=(8, 4))

        mid = tk.Frame(main, bg=BG)
        mid.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(mid, bg=BG_PANEL, width=280)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left.pack_propagate(False)
        self._build_left_panel(left)

        center = tk.Frame(mid, bg=BG)
        center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.core_canvas = tk.Canvas(center, bg=BG, highlightthickness=0)
        self.core_canvas.pack(fill=tk.BOTH, expand=True)

        self.live_transcript_label = tk.Label(
            center,
            textvariable=self.live_transcript_var,
            font=self.font_mono,
            fg=TEXT,
            bg=BG,
            wraplength=520,
            justify="center"
        )
        self.live_transcript_label.pack(fill=tk.X, padx=10, pady=(2, 4))

        right = tk.Frame(mid, bg=BG_PANEL, width=320)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right.pack_propagate(False)
        self._build_right_panel(right)

        bottom = tk.Frame(main, bg=BG, height=155)
        bottom.pack(fill=tk.X, pady=(10, 0))
        bottom.pack_propagate(False)
        self._build_bottom(bottom)

        self.root.after(80, self._init_core)

    def _build_left_panel(self, parent):
        header = tk.Frame(parent, bg=BG_PANEL2, height=36)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="SYSTEM STATUS", font=self.font_small,
                 fg=ORANGE, bg=BG_PANEL2).pack(side=tk.LEFT, padx=12, pady=8)

        items = [
            ("Security Level", "HIGH", GREEN),
            ("External Access", "MONITORED", TURQUOISE),
            ("Network Status", "RESTRICTED", ORANGE_L),
            ("User Privileges", "STANDARD", TEXT_DIM),
            ("System Shield", "ACTIVE", GREEN),
            ("Kernel", self._get_hostname(), TEXT),
            ("Arch", platform.machine(), TEXT),
        ]

        for label, value, color in items:
            row = tk.Frame(parent, bg=BG_PANEL, height=30)
            row.pack(fill=tk.X, padx=8, pady=1)
            row.pack_propagate(False)
            tk.Label(row, text=label, font=self.font_small,
                     fg=TEXT_DIM, bg=BG_PANEL, anchor="w").pack(side=tk.LEFT, padx=6)
            tk.Label(row, text=value, font=self.font_small,
                     fg=color, bg=BG_PANEL, anchor="e").pack(side=tk.RIGHT, padx=6)

        tk.Frame(parent, bg=GRAY2, height=1).pack(fill=tk.X, padx=10, pady=6)

        tk.Frame(parent, bg=GRAY2, height=1).pack(fill=tk.X, padx=10, pady=5)

        # MODULES con scroll (para que quepan los 8)

        tk.Label(parent, text="MODULES", font=self.font_small,
                 fg=ORANGE, bg=BG_PANEL).pack(anchor="w", padx=14, pady=(0, 4))

        modules_container = tk.Frame(
            parent,
            bg=BG_PANEL,
            height=190
        )
        modules_container.pack(
            fill=tk.BOTH,
            expand=True,
            padx=4,
            pady=(2, 6)
        )
        modules_container.pack_propagate(False)

        canvas = tk.Canvas(modules_container, bg=BG_PANEL, highlightthickness=0)
        scrollbar = tk.Scrollbar(
            modules_container, orient="vertical", command=canvas.yview,
            bg=BG_PANEL2, troughcolor=BG_PANEL, activebackground=ORANGE_D
        )
        scroll_frame = tk.Frame(canvas, bg=BG_PANEL)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        module_window = canvas.create_window(
            (0, 0),
            window=scroll_frame,
            anchor="nw"
        )

        def _sync_module_width(event):
            canvas.itemconfigure(
                module_window,
                width=max(1, event.width)
            )

        canvas.bind("<Configure>", _sync_module_width)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def _on_mousewheel(event):
            # Scroll solo cuando el cursor está sobre el panel de módulos.
            if getattr(event, "delta", 0):
                canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")
            elif getattr(event, "num", None) == 4:
                canvas.yview_scroll(-1, "units")
            elif getattr(event, "num", None) == 5:
                canvas.yview_scroll(1, "units")

        def _bind_module_scroll(_event=None):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            canvas.bind_all("<Button-4>", _on_mousewheel)
            canvas.bind_all("<Button-5>", _on_mousewheel)

        def _unbind_module_scroll(_event=None):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")

        # El scroll se activa únicamente mientras el mouse está encima.
        canvas.bind("<Enter>", _bind_module_scroll)
        canvas.bind("<Leave>", _unbind_module_scroll)
        scroll_frame.bind("<Enter>", _bind_module_scroll)
        scroll_frame.bind("<Leave>", _unbind_module_scroll)

        modules = [
            ("01  CONCIENCIA", self._on_ai),
            ("02  SISTEMA", self._on_system),
            ("03  PREFERENCIAS", self._on_appearance),
            ("04  RED", self._on_network),
            ("05  SEGURIDAD", self._on_security),
            ("06  ARCHIVOS", self._on_files),
            ("07  HERRAMIENTAS", self._on_tools),
            ("08  DIAGNOSTICO", self._on_diagnostics),
            ("09  PAQUETES", self._on_packages),
            ("10  CHAT WIFI", self._on_chat),
        ]

        for name, cmd in modules:
            frame = tk.Frame(
                scroll_frame, bg=BG_PANEL,
                highlightbackground=ORANGE_D, highlightthickness=1
            )
            frame.pack(fill=tk.X, padx=6, pady=3)

            btn = tk.Button(
                frame, text=name, font=self.font_small,
                fg=ORANGE, bg=BG_PANEL2,
                activeforeground=ORANGE_L, activebackground=GRAY,
                relief=tk.FLAT, bd=0, cursor="hand2",
                command=cmd, padx=12, pady=6, anchor="w"
            )
            btn.pack(fill=tk.X)
            btn.bind("<Enter>", lambda e, b=btn: (b.configure(bg=GRAY, fg=ORANGE_L), _bind_module_scroll()))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=BG_PANEL2, fg=ORANGE))

    def _build_right_panel(self, parent):
        header = tk.Frame(parent, bg=BG_PANEL2, height=36)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="THREAT LEVEL", font=self.font_small,
                 fg=ORANGE, bg=BG_PANEL2).pack(side=tk.LEFT, padx=12, pady=8)
        self.network_status_var = tk.StringVar(value="CONSULTANDO")
        self.threat_status_var = tk.StringVar(value="CONTROLLED")
        self.threat_status_label = tk.Label(
            header, textvariable=self.threat_status_var,
            font=self.font_small, fg=TURQUOISE, bg=BG_PANEL2
        )
        self.threat_status_label.pack(side=tk.RIGHT, padx=12, pady=8)

        self.map_canvas = tk.Canvas(
            parent, bg="#080808", highlightthickness=0, height=210
        )
        self.map_canvas.pack(fill=tk.X, padx=8, pady=8)
        self._world_map_png = None
        self._world_map_source = None
        self._world_map_photo = None
        self._world_map_color = None
        self.map_canvas.bind("<Configure>", self._draw_map)
        self.network_interfaces = []
        self._network_refresh_inflight = False
        self.root.after(100, self._refresh_network_radar)

        live = tk.Frame(parent, bg=BG_PANEL)
        live.pack(fill=tk.X, padx=10, pady=(2, 4))
        tk.Label(
            live, text="LIVE MONITORING", font=self.font_small,
            fg=TURQUOISE, bg=BG_PANEL
        ).pack(anchor="w")

        proto = tk.Frame(parent, bg=BG_PANEL)
        proto.pack(fill=tk.X, padx=10, pady=(0, 4))
        tk.Label(
            proto, text="PROTOCOL STATUS", font=self.font_small,
            fg=TEXT_DIM, bg=BG_PANEL
        ).pack(anchor="w")
        status_row = tk.Frame(proto, bg=BG_PANEL)
        status_row.pack(fill=tk.X, pady=(5, 4))
        for name, color in (
            ("SHIELD", GREEN),
            ("LOCK", TURQUOISE),
            ("LINK", ORANGE),
            ("AUTH", GREEN),
            ("KEY", TURQUOISE),
        ):
            tk.Label(
                status_row, text=name, font=self.font_small,
                fg=color, bg=BG_PANEL2, padx=8, pady=3
            ).pack(side=tk.LEFT, padx=(0, 4))

        self.network_details_var = tk.StringVar(value="")
        tk.Label(
            parent, textvariable=self.network_details_var,
            font=self.font_mono, fg=TEXT, bg=BG_PANEL,
            justify="left", anchor="w", wraplength=280
        ).pack(fill=tk.X, padx=10, pady=(0, 8))

        sensors = tk.Frame(parent, bg=BG_PANEL2)
        sensors.pack(fill=tk.X, padx=10, pady=(0, 8))
        self.battery_status_var = tk.StringVar(value="BATERÍA: consultando…")
        self.cpu_temperature_var = tk.StringVar(value="CPU: N/A")
        tk.Label(
            sensors, textvariable=self.battery_status_var,
            font=self.font_small, fg=GREEN, bg=BG_PANEL2,
            anchor="w", justify="left", wraplength=280
        ).pack(fill=tk.X, padx=8, pady=(6, 2))
        tk.Label(
            sensors, textvariable=self.cpu_temperature_var,
            font=self.font_small, fg=TEXT, bg=BG_PANEL2,
            anchor="w"
        ).pack(fill=tk.X, padx=8, pady=(0, 6))

    def _draw_map(self, _event=None):
        c = self.map_canvas
        c.delete("all")
        if self._world_map_png is None:
            map_path = Path(__file__).resolve().parent.parent / "assets" / "maps" / "worldmap_outline.png"
            try:
                self._world_map_png = map_path.read_bytes()
            except OSError:
                c.create_text(
                    max(c.winfo_width(), 250) / 2,
                    max(c.winfo_height(), 240) / 2,
                    text="MAPA MUNDIAL NO DISPONIBLE",
                    fill=TEXT_DIM,
                    font=self.font_small,
                )
                return
        if self._world_map_source is None or self._world_map_color != TURQUOISE:
            try:
                self._world_map_source = tk.PhotoImage(
                    data=_tint_outline_png(self._world_map_png, TURQUOISE),
                    format="png",
                )
                self._world_map_color = TURQUOISE
            except tk.TclError:
                c.create_text(
                    max(c.winfo_width(), 250) / 2,
                    max(c.winfo_height(), 240) / 2,
                    text="NO SE PUDO MOSTRAR EL MAPA",
                    fill=TEXT_DIM,
                    font=self.font_small,
                )
                return

        width = max(c.winfo_width(), 250)
        height = max(c.winfo_height(), 240)
        target_width = max(width - 4, 1)
        target_height = max(height - 20, 1)
        factor = max(
            1,
            math.ceil(self._world_map_source.width() / target_width),
            math.ceil(self._world_map_source.height() / target_height),
        )
        self._world_map_photo = self._world_map_source.subsample(factor, factor)
        c.create_image(
            width / 2,
            height / 2,
            image=self._world_map_photo,
            anchor=tk.CENTER,
        )
        map_left = (width - self._world_map_photo.width()) / 2
        map_top = (height - self._world_map_photo.height()) / 2
        for border in MAJOR_COUNTRY_BORDERS:
            coords = []
            for longitude, latitude in border:
                coords.extend((
                    map_left + (longitude + 180) / 360 * self._world_map_photo.width(),
                    map_top + (90 - latitude) / 180 * self._world_map_photo.height(),
                ))
            c.create_line(
                *coords,
                fill=TURQUOISE_D,
                width=1.2,
                dash=(3, 2),
                smooth=True,
            )

    def _refresh_network_radar(self):
        """Refresca IP, red Wi-Fi y ping sin bloquear la interfaz."""
        if self._network_refresh_inflight:
            return
        self._network_refresh_inflight = True

        def worker():
            try:
                snapshot = self.system.network_snapshot()
            except Exception:
                snapshot = {"interfaces": [], "wifi_name": "", "ping": "Sin respuesta"}

            def show():
                self._network_refresh_inflight = False
                if not self.root.winfo_exists():
                    return
                interfaces = snapshot.get("interfaces", [])
                self.network_interfaces = interfaces
                self._last_network_snapshot = snapshot
                ping_text = str(snapshot.get("ping") or "Sin respuesta")
                if not interfaces or "sin respuesta" in ping_text.casefold():
                    self._network_no_reply_count += 1
                else:
                    self._network_no_reply_count = 0
                self.network_status_var.set("ACTIVE" if interfaces else "OFFLINE")
                lines = [
                    f"{item['type']}  ·  {item['ip']}"
                    for item in interfaces[:4]
                ]
                if len(interfaces) > 4:
                    lines.append(f"+ {len(interfaces) - 4} interfaces más")

                wifi_name = snapshot.get("wifi_name", "").strip()
                if wifi_name:
                    lines.append(f"Red Wi-Fi: {wifi_name}")
                elif any(item["type"] == "Cable" for item in interfaces):
                    lines.append("Red Wi-Fi: No aplica (conexión por cable)")
                else:
                    lines.append("Red Wi-Fi: No disponible")
                lines.append(f"Ping a internet: {snapshot.get('ping') or 'Sin respuesta'}")
                self.network_details_var.set("\n".join(lines))
                self._evaluate_health_alerts()
                self.root.after(8000, self._refresh_network_radar)

            try:
                self.root.after(0, show)
            except tk.TclError:
                self._network_refresh_inflight = False

        threading.Thread(target=worker, daemon=True).start()

    def _build_bottom(self, parent):
        metrics = tk.Frame(parent, bg=BG)
        metrics.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        tk.Label(metrics, text="SYSTEM METRICS", font=self.font_small,
                 fg=ORANGE, bg=BG).pack(anchor="w", padx=4, pady=(0, 4))

        cards = tk.Frame(metrics, bg=BG)
        cards.pack(fill=tk.X)

        self.metric_vars = {}
        for key, label in [
            ("cpu", "CPU"), ("ram", "MEMORY"),
            ("disk", "DISK"), ("net", "NETWORK")
        ]:
            card = tk.Frame(cards, bg=BG_PANEL, width=120, height=58)
            card.pack(side=tk.LEFT, padx=4, pady=2)
            card.pack_propagate(False)
            tk.Label(card, text=label, font=self.font_small,
                     fg=TEXT_DIM, bg=BG_PANEL).pack(pady=(5, 0))
            var = tk.StringVar(value="-- %")
            self.metric_vars[key] = var
            tk.Label(card, textvariable=var, font=self.font_title,
                     fg=ORANGE, bg=BG_PANEL).pack()

        logs_frame = tk.Frame(parent, bg=BG_PANEL, width=520)
        logs_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(8, 0))
        logs_frame.pack_propagate(False)

        log_header = tk.Frame(logs_frame, bg=BG_PANEL2, height=25)
        log_header.pack(fill=tk.X)
        log_header.pack_propagate(False)
        tk.Label(log_header, text="SYSTEM LOGS", font=self.font_small,
                 fg=ORANGE, bg=BG_PANEL2).pack(side=tk.LEFT, padx=10, pady=4)
        tk.Label(log_header, text="● LIVE", font=self.font_small,
                 fg=GREEN, bg=BG_PANEL2).pack(side=tk.RIGHT, padx=10, pady=4)

        self.log_text = tk.Text(
            logs_frame, bg="#080808", fg=TEXT_DIM, font=self.font_mono,
            relief=tk.FLAT, height=5, state=tk.DISABLED,
            insertbackground=ORANGE, selectbackground=ORANGE_D
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self._add_log("ULTRON CORE initialized")
        self._add_log("Loading system modules...")
        self._add_log("Network interfaces scanned")
        self._add_log("Security shield active")
        self._add_log("All systems nominal")

    def _init_core(self):
        self.core_canvas.update_idletasks()
        w = self.core_canvas.winfo_width()
        h = self.core_canvas.winfo_height()
        cx, cy = w // 2, h // 2
        self.core = UltronCore(
            self.core_canvas, cx, cy,
            base_radius=min(w, h) // 3.2,
            on_activate=self._activate_consciousness
        )

    def _set_consciousness_state(self, state, top_text=None, color=None):
        """Actualiza el Core desde el hilo principal de Tkinter."""
        if hasattr(self, "core"):
            self.core.set_state(state)

        if top_text:
            self.status_label.configure(
                text=top_text,
                fg=color or TURQUOISE
            )

    def _on_mic_hotkey(self, _event=None):
        self._activate_consciousness()
        return "break"

    def _set_mic_indicator(self, active):
        if not hasattr(self, "mic_button"):
            return
        if active:
            self.mic_button.configure(
                text="MIC · ESCUCHANDO · F8",
                fg=BG,
                bg=TURQUOISE,
                activebackground=TURQUOISE,
            )
        else:
            self.mic_button.configure(
                text="MIC · F8",
                fg=TEXT_DIM,
                bg=BG_PANEL2,
                activebackground=TURQUOISE,
            )

    def _activate_consciousness(self):
        """
        PRIVACY GATE.

        Únicamente un clic del usuario sobre el CORE puede:
          - autorizar el micrófono
          - iniciar CONCIENCIA

        Un segundo clic:
          - revoca autorización
          - detiene grabación
          - detiene voz
          - invalida callbacks anteriores
        """
        if not hasattr(self, "core"):
            return

        if self.consciousness_active or self.mic_authorized:
            # HARD OFF
            self.consciousness_active = False
            self.mic_authorized = False
            self.consciousness_generation += 1

            self._stop_microphone_capture()
            self._stop_speaking()

            self.ai_busy = False
            self._set_live_text("")
            self._set_consciousness_state(
                "IDLE",
                "● SYSTEM ONLINE",
                TURQUOISE
            )
            self._set_mic_indicator(False)
            self._add_log("PRIVACY: micrófono BLOQUEADO")
            return

        # Ask for Groq credentials before authorizing the microphone. Without
        # a key the voice loop fails before it can transcribe or speak.
        api_key = self.groq_api_key or _load_groq_key(self.current_user)
        if not api_key:
            if not UltronAuth._show_groq_key_setup(self.root, self.current_user):
                self._set_live_text("Configura tu API key de Groq para usar la voz.")
                return
            api_key = _load_groq_key(self.current_user)
            if not api_key:
                self._set_live_text("No se guardó la API key de Groq.")
                return
        self.groq_api_key = api_key

        # HARD ON: only reached from the Core click callback.
        self.mic_authorized = True
        self.consciousness_active = True
        self._set_mic_indicator(True)
        self.consciousness_generation += 1

        generation = self.consciousness_generation

        self._add_log("VOZ: micrófono activado; di un comando en español (F8 para detener)")
        self._begin_continuous_listening(generation)

    def _begin_continuous_listening(self, generation=None):
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
        self._set_mic_indicator(True)
        self._set_live_text("")
        self._set_consciousness_state(
            "LISTENING",
            "MICRÓFONO ESCUCHANDO",
            TURQUOISE
        )

        threading.Thread(
            target=self._voice_cycle,
            args=(generation,),
            daemon=True
        ).start()

    def _set_live_text(self, text):
        self.root.after(0, lambda t=text: self.live_transcript_var.set(t))

    def _stop_microphone_capture(self):
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

    def _record_until_silence(self, wav_path, input_device=None):
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
                threshold=700,
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

    def _animate_response_text(self, text):
        """Muestra la respuesta palabra por palabra."""
        words = text.split()
        shown = []

        def step(i=0):
            if i >= len(words):
                return
            shown.append(words[i])
            self.live_transcript_var.set("ULTRON: " + " ".join(shown))
            self.root.after(115, lambda: step(i + 1))

        self.root.after(0, step)

    def _voice_cycle(self, generation):
        """Grabación -> Groq STT -> Groq chat -> voz local."""
        wav_path = None

        if (
            generation != self.consciousness_generation
            or not self.mic_authorized
            or not self.consciousness_active
        ):
            self.ai_busy = False
            return

        try:
            api_key = self.groq_api_key
            if not api_key:
                raise RuntimeError(
                    "No hay una API key de Groq configurada para este usuario. "
                    "Abre Conciencia y guarda tu clave para continuar."
                )

            if not self.system.audio_ready():
                raise RuntimeError(
                    "No hay un micrófono disponible para ULTRON. "
                    "Revisa el dispositivo de entrada en Preferencias."
                )

            # Archivo temporal para la voz del usuario.
            tmp = tempfile.NamedTemporaryFile(
                prefix="ultron_voice_",
                suffix=".wav",
                delete=False
            )
            wav_path = tmp.name
            tmp.close()

            # Se detiene automáticamente al detectar silencio.
            self._set_live_text("ESCUCHANDO...")
            heard_voice = self._record_until_silence(
                wav_path,
                input_device=self._resolve_input_device(),
            )
            if not heard_voice:
                self._set_live_text("")
                return

            self.root.after(
                0,
                lambda: self._set_consciousness_state(
                    "THINKING",
                    "CONCIENCIA PENSANDO",
                    ORANGE_L
                )
            )
            self._safe_log("CONCIENCIA: audio capturado")

            user_text = self._groq_transcribe(wav_path, api_key).strip()

            if not user_text:
                self._set_live_text("")
                return

            normalized_text = user_text.strip().lower().strip(" .,!¡¿?")
            silence_hallucinations = {"gracias", "gracias.", "thank you", "thanks", "subtitulos", "subtítulos", "suscríbete al canal", "suscribete al canal", "suscríbete", "suscribete", "like y suscríbete", "like y suscribete"}
            if normalized_text in silence_hallucinations or ("suscr" in normalized_text and "canal" in normalized_text):
                self._safe_log("CONCIENCIA: ruido/grito ignorado")
                self._set_live_text("")
                return

            self._safe_log(f"TU: {user_text}")
            self._set_live_text(f"TU: {user_text}")

            self.ai_history.append({
                "role": "user",
                "content": user_text
            })

            # Evitar mandar una conversación enorme en cada petición.
            system_message = self.ai_history[0]
            recent = self.ai_history[1:][-12:]
            payload_history = [system_message] + recent

            voice_result = self._run_voice_command(user_text)
            routed_tool = None if voice_result is not None else self._route_local_request(user_text)

            if voice_result is not None:
                response_text = voice_result
            elif routed_tool:
                self._safe_log(f"TOOL: {routed_tool}")
                tool_result = self._execute_ai_tool(routed_tool)
                response_text = tool_result or "No pude obtener ese dato."
            else:
                response_text = self._groq_chat(payload_history, api_key).strip()

                if not response_text:
                    raise RuntimeError("Groq devolvió una respuesta vacía.")

                tool_result = self._execute_ai_tool(response_text)
                if tool_result is not None:
                    self._safe_log(f"TOOL RESULT: {tool_result}")
                    response_text = tool_result

            self.ai_history.append({
                "role": "assistant",
                "content": response_text
            })

            self._safe_log(f"ULTRON: {response_text}")

            # Primero prepara la voz. En cuanto está lista, texto y audio
            # comienzan prácticamente al mismo tiempo.
            speech_path = None
            if self.system.is_windows:
                # Windows usa SAPI directamente; no genera MP3 ni usa ffplay.
                pass
            else:
                speech_path = self._prepare_speech(response_text)

            if (
                generation != self.consciousness_generation
                or not self.consciousness_active
                or not self.mic_authorized
            ):
                try:
                    os.remove(speech_path)
                except Exception:
                    pass
                return

            self.root.after(
                0,
                lambda: self._set_consciousness_state(
                    "SPEAKING",
                    "CONCIENCIA HABLANDO",
                    GREEN
                )
            )
            # Queue the transcript BEFORE blocking TTS playback so Tk can
            # render it shortly after speech starts instead of after speech ends.
            self.root.after(700, lambda text=response_text: self._animate_response_text(text))
            if self.system.is_windows:
                self.system.speak(response_text)
            else:
                self._play_prepared_speech(speech_path)

        except Exception as exc:
            message = str(exc)
            self._safe_log(f"CONCIENCIA ERROR: {message}")
            self.root.after(
                0,
                lambda m=message: self._voice_error(m)
            )

        finally:
            if wav_path:
                try:
                    os.remove(wav_path)
                except Exception:
                    pass

            self.ai_busy = False

            if (
                self.consciousness_active
                and self.mic_authorized
                and generation == self.consciousness_generation
            ):
                # Pequeño cooldown para que el micrófono no capture
                # el final de la propia voz de ULTRON y se auto-dispare.
                self.root.after(
                    850,
                    lambda g=generation: self._begin_continuous_listening(g)
                )
            else:
                self.root.after(
                    0,
                    lambda: self._set_consciousness_state(
                        "IDLE",
                        "● SYSTEM ONLINE",
                        TURQUOISE
                    )
                )

    def _safe_log(self, text):
        try:
            self.root.after(0, lambda t=text: self._add_log(t))
        except tk.TclError:
            pass

    def _voice_error(self, message):
        def show_error():
            self.consciousness_active = False
            self.mic_authorized = False
            self.consciousness_generation += 1
            self.ai_busy = False
            self._set_mic_indicator(False)
            self._set_consciousness_state(
                "IDLE",
                "ERROR DE CONCIENCIA",
                RED
            )
            self._set_live_text(f"Error de voz: {message}")

        try:
            self.root.after(0, show_error)
        except tk.TclError:
            pass

    def _groq_transcribe(self, wav_path, api_key):
        """
        Envía el WAV a Groq Speech-to-Text usando Whisper Large V3 Turbo.
        Implementado con urllib para no obligar a instalar el SDK de Groq.
        """
        boundary = "----UltronBoundary" + uuid.uuid4().hex

        with open(wav_path, "rb") as f:
            audio = f.read()

        parts = []

        def add_field(name, value):
            parts.append(
                (
                    f"--{boundary}\r\n"
                    f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
                    f"{value}\r\n"
                ).encode("utf-8")
            )

        add_field("model", "whisper-large-v3-turbo")
        add_field("language", "es")
        add_field("response_format", "json")

        parts.append(
            (
                f"--{boundary}\r\n"
                'Content-Disposition: form-data; name="file"; filename="voice.wav"\r\n'
                "Content-Type: audio/wav\r\n\r\n"
            ).encode("utf-8")
        )
        parts.append(audio)
        parts.append(b"\r\n")
        parts.append(f"--{boundary}--\r\n".encode("utf-8"))

        body = b"".join(parts)

        request = urllib.request.Request(
            "https://api.groq.com/openai/v1/audio/transcriptions",
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "User-Agent": "ULTRON-Core/3.0",
            }
        )

        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Groq STT respondió HTTP {exc.code}: {detail[:350]}"
            )
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"No pude conectar con Groq para transcribir: {exc.reason}"
            )

        return data.get("text", "")

    def _run_voice_command(self, user_text):
        """Ejecuta solo comandos de voz explícitos y permitidos en el JSON."""
        normalized = _normalize_voice_text(user_text)
        result = None

        if "bateria" in normalized and any(
            word in normalized for word in ("cuanta", "queda", "porcentaje", "carga")
        ):
            battery = self.system.battery_status()
            if battery is None:
                result = "No se detectó una batería en este equipo."
            else:
                if battery.get("charging"):
                    state = "está cargando"
                    remaining = "El tiempo para descargarse no aplica mientras carga."
                elif battery.get("plugged"):
                    state = "está conectada a corriente"
                    remaining = (
                        "Tiempo restante estimado: "
                        f"{self._format_remaining_time(battery.get('seconds_left'))}."
                    )
                else:
                    state = "no está cargando"
                    remaining = (
                        "Tiempo restante estimado: "
                        f"{self._format_remaining_time(battery.get('seconds_left'))}."
                    )
                result = (
                    f"La batería está al {battery['percent']:.0f}% y {state}. "
                    f"{remaining}"
                )

        elif (
            ("disco" in normalized or "espacio" in normalized)
            and any(word in normalized for word in ("cuanto", "queda", "libre"))
        ):
            try:
                disk_root = Path.home().anchor or os.path.abspath(os.sep)
                usage = psutil.disk_usage(disk_root) if HAS_PSUTIL else shutil.disk_usage(disk_root)
                result = (
                    f"Quedan {usage.free / (1024 ** 3):.1f} GB libres "
                    f"de {usage.total / (1024 ** 3):.1f} GB en {disk_root}."
                )
            except Exception as exc:
                result = f"No pude consultar el espacio del disco: {exc}"

        elif normalized.startswith(("abre ", "abrir ")):
            target = normalized.split(" ", 1)[1].strip()
            target = re.sub(
                r"^(?:la aplicacion|la app|el programa|la pagina web|el sitio web|"
                r"pagina web|sitio web|la web de|web de|la pagina(?: de)?|"
                r"el sitio(?: de)?|la|el)\s+",
                "",
                target,
            ).strip()
            candidates = [target]
            if target.startswith("www "):
                candidates.append(target[4:])
            domain_without_suffix = re.sub(
                r"\s+(?:com|org|net|edu|gov|mx|es)$", "", target
            )
            if domain_without_suffix != target:
                candidates.append(domain_without_suffix)

            websites = self.feature_config["voice"]["websites"]
            site_lookup = {
                _normalize_voice_text(alias): (alias, url)
                for alias, url in websites.items()
            }
            site = next(
                (site_lookup[candidate] for candidate in candidates if candidate in site_lookup),
                None,
            )
            if site:
                alias, url = site
                result = (
                    f"Abrí el sitio permitido: {alias}."
                    if self.system.open_url(url)
                    else f"No pude abrir el sitio permitido: {alias}."
                )
            else:
                apps = self.feature_config["voice"]["apps"]
                app_lookup = {
                    _normalize_voice_text(alias): (alias, command)
                    for alias, command in apps.items()
                }
                app = next(
                    (app_lookup[candidate] for candidate in candidates if candidate in app_lookup),
                    None,
                )
                if app:
                    alias, command = app
                    try:
                        launch_target = command[0]
                        if re.match(r"^[a-z][a-z0-9+.-]*:", launch_target, re.IGNORECASE):
                            opened = self.system.open_url(launch_target)
                            if not opened:
                                raise RuntimeError(
                                    "Windows no encontró una aplicación asociada a este enlace."
                                )
                        elif self.system.is_windows and launch_target.casefold() in {
                            "chrome", "msedge", "firefox", "winword", "excel",
                            "powerpnt", "code", "vlc",
                        }:
                            executable = shutil.which(launch_target)
                            if not executable:
                                raise FileNotFoundError(
                                    f"No encontré {launch_target}.exe en PATH; "
                                    "ajusta la ruta en config/ultron_features.json."
                                )
                            subprocess.Popen([executable, *command[1:]], shell=False)
                        else:
                            subprocess.Popen(command, shell=False)
                        result = f"Abrí la aplicación permitida: {alias}."
                    except Exception as exc:
                        result = f"No pude abrir {alias}: {exc}"
                else:
                    result = (
                        f"No abrí «{target}»: no está en la lista permitida "
                        "de config/ultron_features.json."
                    )

        if result is not None:
            self._safe_log(f"COMANDO DE VOZ: {user_text} | RESULTADO: {result}")
        return result

    def _route_local_request(self, user_text):
        """Resuelve peticiones comunes localmente antes de llamar al modelo."""
        t = user_text.lower().strip()

        if any(x in t for x in [
            "mi ip pública", "mi ip publica", "ip pública", "ip publica",
            "ip de internet", "dirección ip pública", "direccion ip publica"
        ]):
            return "TOOL:get_public_ip"

        if any(x in t for x in [
            "qué ip tengo", "que ip tengo", "cuál es mi ip", "cual es mi ip",
            "mi ip local", "ip local"
        ]):
            return "TOOL:get_local_ip"

        if any(x in t for x in [
            "qué red", "que red", "mi red wifi", "mi wifi",
            "a qué wifi", "a que wifi", "nombre de mi red", "ssid"
        ]):
            return "TOOL:get_wifi_name"

        if "batería" in t or "bateria" in t:
            return "TOOL:get_battery"
        if "ram" in t or "memoria" in t:
            return "TOOL:get_memory"

        if any(x in t for x in [
            "temperatura",
            "temperatura del cpu",
            "temperatura de cpu",
            "temperatura del procesador",
            "qué temperatura", "que temperatura",
            "a qué temperatura", "a que temperatura",
            "cuántos grados", "cuantos grados",
            "qué tan caliente", "que tan caliente",
            "caliente está", "caliente esta"
        ]):
            return "TOOL:get_temperature"

        if any(x in t for x in [
            "cpu",
            "procesador",
            "uso del procesador",
            "uso de cpu",
            "carga del procesador",
            "carga de cpu",
            "cuánto cpu", "cuanto cpu",
            "qué uso tiene el procesador", "que uso tiene el procesador",
            "cómo está el cpu", "como está el cpu"
        ]):
            return "TOOL:get_cpu"

        if "disco" in t or "espacio libre" in t or "almacenamiento" in t:
            return "TOOL:get_disk"

        if any(x in t for x in [
            "procesos",
            "procesos activos",
            "qué procesos", "que procesos",
            "qué está corriendo", "que está corriendo",
            "qué está ejecutándose", "que está ejecutandose",
            "qué consume cpu", "que consume cpu",
            "qué consume procesador", "que consume procesador",
            "programas activos"
        ]):
            return "TOOL:get_processes"
        # Sistema operativo / información del equipo.
        # Incluye variantes imperfectas producidas por STT.
        if any(x in t for x in [
            "información del sistema", "informacion del sistema",
            "qué sistema", "que sistema",
            "sistema operativo",
            "qué operativo", "que operativo",
            "operativo estoy usando",
            "operativo uso",
            "qué sistema operativo", "que sistema operativo",
            "cuál sistema operativo", "cual sistema operativo",
            "qué sistema estoy usando", "que sistema estoy usando",
            "qué sistema uso", "que sistema uso"
        ]):
            return "TOOL:get_system_info"

        if "youtube" in t and any(x in t for x in ["abre", "abrir", "inicia", "pon"]):
            return "TOOL:open_url:https://www.youtube.com"
        if ("whatsapp" in t or "whats" in t) and any(x in t for x in ["abre", "abrir", "inicia"]):
            return "TOOL:open_url:https://web.whatsapp.com"

        return None

    def _execute_ai_tool(self, response_text):
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
                return self.system.system_module()

            if tool == "get_cpu":
                try:
                    import psutil
                    usage = psutil.cpu_percent(interval=0.35)
                    cores = psutil.cpu_count(logical=True) or "?"
                    physical = psutil.cpu_count(logical=False) or "?"
                    return (
                        f"CPU en uso: {usage:.0f}%. "
                        f"Núcleos físicos: {physical}. "
                        f"Núcleos lógicos: {cores}."
                    )
                except Exception as exc:
                    return f"No pude leer el uso del CPU: {exc}"

            if tool == "get_disk":
                return self.system.files_module()

            if tool == "get_temperature":
                return self.system.temperature_module()

            if tool == "get_processes":
                return self.system.processes_module()

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

    def _tool_result_to_ai(self, user_request, tool_result, api_key):
        """Hace que ULTRON convierta el resultado técnico en una respuesta natural."""
        messages = [
            self.ai_history[0],
            {
                "role": "user",
                "content": (
                    f"El usuario pidió: {user_request}\n"
                    f"Resultado real de la herramienta: {tool_result}\n"
                    "Responde al usuario usando ese resultado. No pidas otra herramienta."
                )
            }
        ]
        return self._groq_chat(messages, api_key)

    def _groq_chat(self, history, api_key):
        """Obtiene la respuesta conversacional de ULTRON mediante Groq."""
        payload = json.dumps({
            "model": "openai/gpt-oss-20b",
            "messages": history,
            "temperature": 0.55,
            "max_completion_tokens": 500
        }).encode("utf-8")

        request = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=payload,
            method="POST",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "ULTRON-Core/3.0",
            }
        )

        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Groq Chat respondió HTTP {exc.code}: {detail[:350]}"
            )
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"No pude conectar con Groq Chat: {exc.reason}"
            )

        try:
            return data["choices"][0]["message"]["content"]
        except Exception:
            raise RuntimeError(
                "La respuesta de Groq no tenía el formato esperado."
            )

    def _stop_speaking(self):
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

    def _prepare_speech(self, text):
        # ULTRON V3: edge-tts gestionado por TTSAdapter.
        return self.system.prepare_speech(text)

    def _play_prepared_speech(self, speech_path):
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

    def _speak_text(self, text):
        # Compatibilidad con llamadas existentes.
        speech_path = self._prepare_speech(text)
        self._play_prepared_speech(speech_path)

    def _start_animation(self):
        def tick():
            if hasattr(self, "core"):
                self.core.animate()
            self.root.after(40, tick)
        self.root.after(100, tick)

    @staticmethod
    def _format_remaining_time(seconds):
        if seconds is None:
            return "N/A"
        hours, remainder = divmod(max(0, int(seconds)), 3600)
        minutes = remainder // 60
        if hours:
            return f"{hours} h {minutes} min"
        return f"{minutes} min"

    def _battery_display_text(self, battery):
        if not battery:
            return "BATERÍA: N/A"
        if battery.get("charging"):
            state = "CARGANDO"
            remaining = "N/A"
        elif battery.get("plugged"):
            state = "CONECTADA"
            remaining = self._format_remaining_time(battery.get("seconds_left"))
        else:
            state = "DESCARGANDO"
            remaining = self._format_remaining_time(battery.get("seconds_left"))
        return (
            f"BATERÍA: {battery['percent']:.0f}% · {state} · "
            f"RESTANTE: {remaining}"
        )

    def _play_alert_beep(self):
        if not self.feature_config["alerts"].get("beep_enabled", True):
            return

        def beep():
            try:
                import winsound
                winsound.Beep(740, 90)
            except Exception:
                try:
                    self.root.after(0, self.root.bell)
                except tk.TclError:
                    pass

        threading.Thread(target=beep, daemon=True).start()

    def _evaluate_health_alerts(self):
        metrics = self._latest_health_metrics
        thresholds = self.feature_config["alerts"]
        current = {}

        cpu = metrics.get("cpu")
        cpu_limit = float(thresholds.get("cpu_percent", 85))
        sustained_for = float(thresholds.get("cpu_sustained_seconds", 30))
        if cpu is not None and cpu >= cpu_limit:
            if self._cpu_high_since is None:
                self._cpu_high_since = time.monotonic()
            elif time.monotonic() - self._cpu_high_since >= sustained_for:
                current["cpu"] = f"CPU alta sostenida: {cpu:.0f}% (umbral {cpu_limit:.0f}%)."
        else:
            self._cpu_high_since = None

        memory = metrics.get("memory")
        memory_limit = float(thresholds.get("memory_percent", 90))
        if memory is not None and memory >= memory_limit:
            current["memory"] = (
                f"Memoria alta: {memory:.0f}% (umbral {memory_limit:.0f}%)."
            )

        disk = metrics.get("disk")
        disk_limit = float(thresholds.get("disk_percent", 90))
        if disk is not None and disk >= disk_limit:
            current["disk"] = f"Disco casi lleno: {disk:.0f}% usado."

        battery = metrics.get("battery")
        battery_limit = float(thresholds.get("battery_percent", 15))
        if (
            battery
            and not battery.get("plugged")
            and battery.get("percent", 100) <= battery_limit
        ):
            current["battery"] = (
                f"Batería baja: {battery['percent']:.0f}% "
                f"(umbral {battery_limit:.0f}%)."
            )

        temperature = metrics.get("temperature")
        temperature_limit = float(thresholds.get("temperature_c", 85))
        if temperature is not None and temperature >= temperature_limit:
            current["temperature"] = (
                f"Temperatura de CPU alta: {temperature:.1f} °C "
                f"(umbral {temperature_limit:.0f} °C)."
            )
        elif temperature is None and "temperature" in self._active_alerts:
            current["temperature"] = self._active_alerts["temperature"]

        snapshot = self._last_network_snapshot
        if snapshot is not None:
            interfaces = snapshot.get("interfaces", [])
            failed_pings = max(
                1, int(thresholds.get("network_loss_after_failures", 3))
            )
            if not interfaces or self._network_no_reply_count >= failed_pings:
                current["network"] = "Conexión de red perdida o sin respuesta sostenida."
            else:
                ping_text = str(snapshot.get("ping") or "")
                ping_match = re.search(
                    r"[<>]?\s*(\d+(?:[.,]\d+)?)\s*ms",
                    ping_text,
                    re.IGNORECASE,
                )
                if ping_match:
                    ping_ms = float(ping_match.group(1).replace(",", "."))
                    ping_limit = float(thresholds.get("ping_ms", 180))
                    if ping_ms > ping_limit:
                        current["ping"] = (
                            f"Ping alto: {ping_ms:.0f} ms "
                            f"(umbral {ping_limit:.0f} ms)."
                        )
        elif "network" in self._active_alerts:
            current["network"] = self._active_alerts["network"]
        elif "ping" in self._active_alerts:
            current["ping"] = self._active_alerts["ping"]

        for key, message in current.items():
            if key not in self._active_alerts:
                self._add_log(f"ALERTA REAL: {message}")
                self._play_alert_beep()
        for key, message in self._active_alerts.items():
            if key not in current:
                self._add_log(f"ALERTA RESUELTA: {message}")

        self._active_alerts = current
        if not current:
            self.threat_status_var.set("CONTROLLED")
            self.threat_status_label.configure(fg=TURQUOISE)
        elif len(current) == 1:
            self.threat_status_var.set("ELEVATED")
            self.threat_status_label.configure(fg=ORANGE_L)
        else:
            self.threat_status_var.set("HIGH")
            self.threat_status_label.configure(fg=RED)

    def _update_metrics(self):
        cpu = memory = disk = None
        battery = None
        temperature = None
        if HAS_PSUTIL:
            try:
                cpu = float(psutil.cpu_percent(interval=None))
                memory = float(psutil.virtual_memory().percent)
                disk_root = Path.home().anchor or os.path.abspath(os.sep)
                disk = float(psutil.disk_usage(disk_root).percent)
            except Exception:
                pass
        try:
            battery = self.system.battery_status()
        except Exception:
            pass
        try:
            temperature = self.system.cpu_temperature()
        except Exception:
            pass

        self._latest_health_metrics = {
            "cpu": cpu,
            "memory": memory,
            "disk": disk,
            "battery": battery,
            "temperature": temperature,
        }
        if hasattr(self, "metric_vars"):
            self.metric_vars["cpu"].set(f"{cpu:.0f} %" if cpu is not None else "N/A")
            self.metric_vars["ram"].set(
                f"{memory:.0f} %" if memory is not None else "N/A"
            )
            self.metric_vars["disk"].set(
                f"{disk:.0f} %" if disk is not None else "N/A"
            )
            self.metric_vars["net"].set(
                "online" if self.network_interfaces else "offline"
            )
        if hasattr(self, "battery_status_var"):
            self.battery_status_var.set(self._battery_display_text(battery))
            self.cpu_temperature_var.set(
                f"CPU: {temperature:.1f} °C" if temperature is not None else "CPU: N/A"
            )

        self._evaluate_health_alerts()
        interval = max(1.0, float(self.feature_config["alerts"].get("sample_seconds", 5)))
        self.root.after(int(interval * 1000), self._update_metrics)

    def _add_log(self, msg):
        self.log_text.configure(state=tk.NORMAL)
        ts = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{ts}]  > {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _get_hostname(self):
        try:
            return socket.gethostname()[:18]
        except Exception:
            return "Linux"

    def _uptime_str(self):
        if not HAS_PSUTIL:
            return "N/A"
        seconds = int(time.time() - psutil.boot_time())
        d = seconds // 86400
        h = (seconds % 86400) // 3600
        m = (seconds % 3600) // 60
        return f"{d}d {h}h {m}m"

    def _on_ai(self):
        self._add_log("Module CONCIENCIA selected")
        self._close_active_module()

        # Revisa la clave guardada y comprueba que Groq aún la acepte.
        api_key = self.groq_api_key or _load_groq_key(self.current_user)
        if not api_key:
            if not UltronAuth._show_groq_key_setup(self.root, self.current_user):
                return
            api_key = _load_groq_key(self.current_user)
            if not api_key:
                return
            self.groq_api_key = api_key

        startup_notice = ""
        validation, validation_message = _validate_groq_api_key(api_key, timeout=4)
        if validation == "invalid":
            from tkinter import messagebox

            replace_key = messagebox.askyesno(
                "ULTRON // API KEY RECHAZADA",
                validation_message + "\n\n¿Quieres configurar otra clave?",
                parent=self.root,
            )
            if not replace_key:
                self.groq_api_key = ""
                return
            if not UltronAuth._show_groq_key_setup(self.root, self.current_user):
                return
            api_key = _load_groq_key(self.current_user)
            if not api_key:
                return
            self.groq_api_key = api_key
        elif validation == "unverified":
            startup_notice = validation_message

        self.groq_api_key = api_key

        win = tk.Toplevel(self.root)
        self._active_module_window = win
        win.title("ULTRON - CONCIENCIA")
        win.configure(bg=BG)
        win.geometry("780x590")
        win.minsize(620, 460)
        win.transient(self.root)

        header = tk.Frame(win, bg=BG_PANEL2, height=48)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="// CONCIENCIA / CHAT",
            font=self.font_title,
            fg=ORANGE,
            bg=BG_PANEL2
        ).pack(side=tk.LEFT, padx=18, pady=10)

        status_var = tk.StringVar(
            value="IA LISTA" if not startup_notice else "SIN VERIFICAR"
        )
        tk.Label(
            header,
            textvariable=status_var,
            font=self.font_small,
            fg=TURQUOISE,
            bg=BG_PANEL2
        ).pack(side=tk.RIGHT, padx=18)

        body = tk.Frame(win, bg=BG)
        body.pack(fill=tk.BOTH, expand=True, padx=14, pady=(14, 8))

        chat = tk.Text(
            body,
            bg="#080808",
            fg=TEXT,
            font=self.font_mono,
            relief=tk.FLAT,
            padx=14,
            pady=12,
            wrap=tk.WORD,
            insertbackground=ORANGE,
            selectbackground=ORANGE_D,
            state=tk.DISABLED
        )
        scroll = tk.Scrollbar(
            body,
            orient="vertical",
            command=chat.yview,
            bg=BG_PANEL2,
            troughcolor=BG,
            activebackground=ORANGE_D
        )
        chat.configure(yscrollcommand=scroll.set)
        chat.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        bottom = tk.Frame(win, bg=BG)
        bottom.pack(fill=tk.X, padx=14, pady=(0, 14))

        entry = tk.Entry(
            bottom,
            bg=BG_PANEL2,
            fg=TEXT,
            insertbackground=ORANGE,
            relief=tk.FLAT,
            font=self.font_mono
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10)

        send_btn = tk.Button(
            bottom,
            text="ENVIAR",
            font=self.font_small,
            fg=ORANGE,
            bg=BG_PANEL2,
            activeforeground=ORANGE_L,
            activebackground=GRAY,
            relief=tk.FLAT,
            padx=18,
            pady=9
        )
        send_btn.pack(side=tk.RIGHT, padx=(8, 0))

        def append(role, text):
            if not win.winfo_exists():
                return
            chat.configure(state=tk.NORMAL)
            chat.insert(tk.END, f"{role}: {text}\n\n")
            chat.see(tk.END)
            chat.configure(state=tk.DISABLED)

        # Mostrar el historial compartido con la voz, sin repetir el mensaje de sistema.
        history_items = self.ai_history[1:][-12:]
        if history_items:
            for item in history_items:
                role = "TU" if item.get("role") == "user" else "ULTRON"
                append(role, item.get("content", ""))
        else:
            append("ULTRON", "Chat de texto listo. Escribe un mensaje.")
        if startup_notice:
            append("SYSTEM", startup_notice)

        def finish_response(user_text, response_text):
            if not win.winfo_exists():
                return
            self.ai_history.append({"role": "assistant", "content": response_text})
            append("ULTRON", response_text)
            status_var.set("IA LISTA")
            send_btn.configure(state=tk.NORMAL)
            entry.configure(state=tk.NORMAL)
            entry.focus_set()
            self._safe_log(f"ULTRON/TEXTO: {response_text}")

        def fail_response(exc):
            if not win.winfo_exists():
                return
            append("SYSTEM", f"Error de IA: {exc}")
            status_var.set("ERROR")
            send_btn.configure(state=tk.NORMAL)
            entry.configure(state=tk.NORMAL)
            entry.focus_set()
            self._safe_log(f"CONCIENCIA TEXTO ERROR: {exc}")

        def worker(user_text):
            try:
                api_key = self.groq_api_key
                if not api_key:
                    raise RuntimeError(
                        "No hay una API key de Groq configurada para este usuario. "
                        "Abre Conciencia y guarda tu clave para continuar."
                    )

                routed_tool = self._route_local_request(user_text)
                if routed_tool:
                    tool_result = self._execute_ai_tool(routed_tool)
                    response_text = tool_result or "No pude obtener ese dato."
                else:
                    system_message = self.ai_history[0]
                    recent = self.ai_history[1:][-12:]
                    response_text = self._groq_chat(
                        [system_message] + recent,
                        api_key
                    ).strip()
                    if not response_text:
                        raise RuntimeError("Groq devolvio una respuesta vacia.")

                    tool_result = self._execute_ai_tool(response_text)
                    if tool_result is not None:
                        response_text = tool_result

                self.root.after(
                    0,
                    lambda: finish_response(user_text, str(response_text))
                )
            except Exception as exc:
                self.root.after(0, lambda exc=exc: fail_response(exc))

        def send(_event=None):
            user_text = entry.get().strip()
            if not user_text:
                return "break"

            entry.delete(0, tk.END)
            append("TU", user_text)
            self.ai_history.append({"role": "user", "content": user_text})
            self._safe_log(f"TU/TEXTO: {user_text}")

            status_var.set("PENSANDO...")
            send_btn.configure(state=tk.DISABLED)
            entry.configure(state=tk.DISABLED)
            threading.Thread(
                target=worker,
                args=(user_text,),
                daemon=True
            ).start()
            return "break"

        send_btn.configure(command=send)
        entry.bind("<Return>", send)
        win.protocol("WM_DELETE_WINDOW", self._close_active_module)
        entry.focus_set()

    def _on_system(self):
        self._add_log(f"Module SISTEMA selected [{self.system.os_name()}]")
        self._show_module("SISTEMA", self.system.system_module())

    def _on_network(self):
        self._add_log(f"Module RED selected [{self.system.os_name()}]")
        self._show_module("RED", self.system.network_module())

    def _on_security(self):
        self._add_log(f"Module SEGURIDAD selected [{self.system.os_name()}]")
        self._show_module("SEGURIDAD", self.system.security_module())

    def _on_files(self):
        self._add_log(f"Module ARCHIVOS selected [{self.system.os_name()}]")
        self._show_module("ALMACENAMIENTO", self.system.files_module())

    def _run_command_async(
        self, command, output_widget, title="COMANDO", action_label=None
    ):
        """Ejecuta comandos sin congelar la interfaz."""
        if not callable(command):
            if isinstance(command, str):
                command = shlex.split(command, posix=not self.system.is_windows)
            else:
                command = [str(part) for part in command]
            if not command:
                return
        output_widget.configure(state=tk.NORMAL)
        output_widget.delete("1.0", tk.END)
        output_widget.insert(
            tk.END,
            f"{action_label or 'ULTRON'}\n\nConsultando información...\n",
        )
        output_widget.configure(state=tk.DISABLED)

        def worker():
            try:
                if callable(command):
                    text = command()
                else:
                    result = subprocess.run(
                        command,
                        shell=False,
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        timeout=120
                    )
                    text = result.stdout.strip() or "(Sin salida)"
            except subprocess.TimeoutExpired:
                text = (
                    "El comando tardó demasiado.\n\n"
                    "Si es un comando con sudo, ULTRON no puede responder "
                    "una contraseña desde esta ventana. Usa el botón TERMINAL "
                    "para los comandos administrativos."
                )
            except Exception as exc:
                text = f"Error:\n{exc}"

            def show():
                if not output_widget.winfo_exists():
                    return
                output_widget.configure(state=tk.NORMAL)
                output_widget.delete("1.0", tk.END)
                output_widget.insert(tk.END, text)
                output_widget.configure(state=tk.DISABLED)
                self._add_log(f"{title}: comando finalizado")

            self.root.after(0, show)

        threading.Thread(target=worker, daemon=True).start()

    def _run_admin_terminal(self, command):
        """Abre una terminal apropiada al sistema para el comando indicado."""
        try:
            if isinstance(command, (tuple, list)):
                command = (
                    subprocess.list2cmdline([str(part) for part in command])
                    if self.system.is_windows
                    else shlex.join(str(part) for part in command)
                )
            if self.system.is_windows:
                ps_command = (
                    "Start-Process powershell.exe -Verb RunAs "
                    "-ArgumentList @('-NoExit','-Command'," + repr(command) + ")"
                )
                subprocess.Popen(
                    ["powershell.exe", "-NoProfile", "-Command", ps_command],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
            elif self.system.is_linux:
                if command.strip() in {"x-terminal-emulator", "terminal"}:
                    if self.system.open_terminal():
                        return
                    raise RuntimeError("No encontré una terminal compatible.")

                script = (
                    f"{command}; result=$?; printf '\\n\\nCódigo de salida: %s\\n' \"$result\"; "
                    "read -r -p 'Presiona Enter para cerrar...'"
                )
                terminal_commands = [
                    ["x-terminal-emulator", "-e", "bash", "-lc", script],
                    ["gnome-terminal", "--", "bash", "-lc", script],
                    ["konsole", "-e", "bash", "-lc", script],
                    ["xfce4-terminal", "--command", f"bash -lc {shlex.quote(script)}"],
                    ["kitty", "bash", "-lc", script],
                    ["alacritty", "-e", "bash", "-lc", script],
                ]
                for terminal_command in terminal_commands:
                    if shutil.which(terminal_command[0]):
                        subprocess.Popen(
                            terminal_command,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                        break
                else:
                    raise RuntimeError("No encontré una terminal compatible.")
            else:
                raise RuntimeError(f"Sistema no compatible: {self.system.os_name()}")

            self._add_log(f"Terminal administrativa: {command}")
        except Exception as exc:
            self._show_module(
                "TERMINAL ADMINISTRATIVA",
                f"No pude abrir una terminal.\n\n{exc}\n\nComando:\n{command}"
            )

    def _hud_panel(self, parent, bg=None, border=None, pad=13):
        """
        Panel angular inspirado en HUDs sci-fi.
        Devuelve (canvas, inner_frame).
        """
        bg = bg or BG_PANEL
        border = border or TURQUOISE

        canvas = tk.Canvas(
            parent,
            bg=BG,
            highlightthickness=0,
            bd=0
        )

        inner = tk.Frame(canvas, bg=bg)
        window_id = canvas.create_window(
            (pad, pad),
            window=inner,
            anchor="nw"
        )

        def redraw(event=None):
            w = max(canvas.winfo_width(), 80)
            h = max(canvas.winfo_height(), 60)

            notch = 22
            cut = 36

            pts = [
                2, notch,
                notch, 2,
                w-cut, 2,
                w-2, cut,
                w-2, h-notch,
                w-notch, h-2,
                cut, h-2,
                2, h-cut,
            ]

            canvas.delete("hud_border")
            canvas.create_polygon(
                pts,
                fill=bg,
                outline=border,
                width=2,
                tags=("hud_border",)
            )

            # Acentos tipo referencia.
            canvas.create_line(
                18, 2, min(w*0.38, 210), 2,
                fill=ORANGE,
                width=3,
                tags=("hud_border",)
            )
            canvas.create_line(
                max(20, w*0.62), h-2, w-36, h-2,
                fill=TURQUOISE,
                width=3,
                tags=("hud_border",)
            )

            canvas.itemconfigure(
                window_id,
                width=max(20, w-pad*2),
                height=max(20, h-pad*2)
            )

        canvas.bind("<Configure>", redraw)
        return canvas, inner

    def _module_action_window(self, title, actions, search_action=None):
        self._close_active_module()
        """Ventana reutilizable para módulos de comandos."""
        win = tk.Toplevel(self.root)
        win.title(f"ULTRON — {title}")
        win.configure(bg=BG)
        win.geometry("780x560")
        win.minsize(650, 480)
        win.transient(self.root)

        header = tk.Frame(win, bg=BG_PANEL2, height=44)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header, text=f"// {title}",
            font=self.font_title, fg=ORANGE, bg=BG_PANEL2
        ).pack(side=tk.LEFT, padx=16, pady=8)

        main = tk.Frame(win, bg=BG)
        main.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        controls = tk.Frame(main, bg=BG_PANEL2, width=235, highlightbackground=ORANGE_D, highlightthickness=1)
        controls.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        controls.pack_propagate(False)

        output_shell = tk.Frame(main, bg=BG)
        output_shell.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        output_hud, output_frame = self._hud_panel(
            output_shell,
            bg="#080808",
            border=TURQUOISE
        )
        output_hud.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            controls, text="ACCIONES",
            font=self.font_small, fg=ORANGE, bg=BG_PANEL
        ).pack(anchor="w", padx=10, pady=(10, 6))

        search_var = tk.StringVar()

        if search_action:
            tk.Label(
                controls, text="Paquete / búsqueda",
                font=self.font_small, fg=TEXT_DIM, bg=BG_PANEL
            ).pack(anchor="w", padx=10, pady=(4, 2))

            search_entry = tk.Entry(
                controls, textvariable=search_var,
                font=self.font_mono,
                bg=BG_PANEL2, fg=TEXT,
                insertbackground=ORANGE,
                relief=tk.FLAT
            )
            search_entry.pack(fill=tk.X, padx=10, pady=(0, 6))

        output = tk.Text(
            output_frame,
            bg="#080808",
            fg=TEXT,
            font=self.font_mono,
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=12,
            pady=10,
            state=tk.DISABLED
        )
        output_scroll = tk.Scrollbar(
            output_frame,
            orient="vertical",
            command=output.yview
        )
        output.configure(yscrollcommand=output_scroll.set)
        output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        output_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        def run_normal(label, command):
            self._add_log(f"{title}: {label}")
            self._run_command_async(
                command, output, title, action_label=label
            )

        def run_search():
            value = search_var.get().strip()
            if not value:
                output.configure(state=tk.NORMAL)
                output.delete("1.0", tk.END)
                output.insert(tk.END, "Escribe primero el nombre del paquete.")
                output.configure(state=tk.DISABLED)
                return
            # These queries are interpolated into shell commands. Windows
            # list2cmdline quoting is not cmd.exe escaping, so reject shell
            # metacharacters before constructing the command on either OS.
            if len(value) > 100 or not re.fullmatch(r"[A-Za-z0-9_.+@ -]+", value):
                output.configure(state=tk.NORMAL)
                output.delete("1.0", tk.END)
                output.insert(
                    tk.END,
                    "La búsqueda solo admite letras, números, espacios y . _ + @ -.",
                )
                output.configure(state=tk.DISABLED)
                return
            command = [*search_action, value]
            run_normal(f"Resultados para «{value}»", command)

        if search_action:
            tk.Button(
                controls,
                text="BUSCAR",
                font=self.font_small,
                fg=TURQUOISE,
                bg=BG_PANEL2,
                activeforeground=TEXT,
                activebackground=GRAY,
                relief=tk.FLAT,
                command=run_search,
                padx=8, pady=7
            ).pack(fill=tk.X, padx=10, pady=(0, 8))

        for item in actions:
            label = item["label"]
            command = item["command"]
            admin = item.get("admin", False)

            if admin:
                callback = lambda c=command: self._run_admin_terminal(c)
            else:
                callback = lambda l=label, c=command: run_normal(l, c)

            tk.Button(
                controls,
                text=label,
                font=self.font_small,
                fg=ORANGE if not admin else ORANGE_L,
                bg=BG_PANEL2,
                activeforeground=ORANGE_L,
                activebackground=GRAY,
                relief=tk.FLAT,
                anchor="w",
                command=callback,
                padx=10,
                pady=8
            ).pack(fill=tk.X, padx=10, pady=3)

        admin_note = (
            "Las acciones administrativas se abren en PowerShell con "
            "confirmación de Windows cuando sea necesario."
            if self.system.is_windows else
            "Las acciones administrativas se abren en una terminal; "
            "sudo puede solicitar tu contraseña."
        )
        tk.Label(
            controls,
            text=admin_note,
            font=self.font_small,
            fg=TEXT_DIM,
            bg=BG_PANEL,
            justify="left"
        ).pack(side=tk.BOTTOM, anchor="w", padx=10, pady=10)

        output.configure(state=tk.NORMAL)
        output.insert(
            tk.END,
            f"{title}\n\nSelecciona una acción en el panel izquierdo."
        )
        output.configure(state=tk.DISABLED)

    def _on_tools(self):
        self._add_log(f"Module HERRAMIENTAS selected [{self.system.os_name()}]")
        data = self.system.summary()
        info = (
            "ULTRON V3 // HERRAMIENTAS MULTIPLATAFORMA\n\n"
            f"Sistema detectado: {data['system']}\n"
            f"Equipo: {data['hostname']}\n"
            f"Arquitectura: {data['architecture']}\n"
            f"Python: {data['python']}\n"
            f"IP local: {data['local_ip']}\n\n"
            "La capa V3 ya dispone de funciones portables para abrir "
            "terminal, archivos, URLs y aplicaciones compatibles."
        )
        self._show_module("HERRAMIENTAS", info)

    def _on_diagnostics(self):
        self._add_log(f"Module DIAGNOSTICO selected [{self.system.os_name()}]")
        info = (
            self.system.diagnostics()
            + "\n\nPROCESOS:\n"
            + self.system.processes_module()
            + "\n\nBATERIA:\n"
            + self.system.battery_module()
        )
        self._show_module("DIAGNOSTICO", info)

    def _on_packages(self):
        self._add_log("Module PAQUETES selected")
        if self.system.is_windows:
            actions = [
                {"label": "Programas instalados", "command": self.system.installed_programs},
                {"label": "Actualizar repositorios", "command": ["winget", "source", "update"]},
                {"label": "Actualizar sistema", "command": ["winget", "upgrade", "--all", "--accept-source-agreements", "--accept-package-agreements"]},
                {"label": "Limpiar paquetes", "command": ["winget", "upgrade", "--accept-source-agreements"]},
            ]
            search_action = ["winget", "search", "--accept-source-agreements"]
        elif shutil.which("apt"):
            actions = [
                {"label": "Programas instalados", "command": self.system.installed_programs},
                {"label": "Actualizar repositorios", "command": ["sudo", "apt", "update"], "admin": True},
                {"label": "Actualizar sistema", "command": ["sudo", "apt", "upgrade"], "admin": True},
                {"label": "Limpiar paquetes", "command": ["sudo", "apt", "autoremove"], "admin": True},
            ]
            search_action = ["apt-cache", "search"]
        elif shutil.which("dnf"):
            actions = [
                {"label": "Programas instalados", "command": self.system.installed_programs},
                {"label": "Actualizar repositorios", "command": ["sudo", "dnf", "makecache"], "admin": True},
                {"label": "Actualizar sistema", "command": ["sudo", "dnf", "upgrade"], "admin": True},
                {"label": "Limpiar paquetes", "command": ["sudo", "dnf", "autoremove"], "admin": True},
            ]
            search_action = ["dnf", "search"]
        elif shutil.which("pacman"):
            actions = [
                {"label": "Programas instalados", "command": self.system.installed_programs},
                {"label": "Actualizar repositorios", "command": ["sudo", "pacman", "-Sy"], "admin": True},
                {"label": "Actualizar sistema", "command": ["sudo", "pacman", "-Syu"], "admin": True},
                {"label": "Limpiar paquetes", "command": ["sudo", "pacman", "-Sc"], "admin": True},
            ]
            search_action = ["pacman", "-Ss"]
        else:
            self._show_module(
                "GESTOR DE PAQUETES",
                "No detecté winget, apt, dnf ni pacman en este sistema.",
            )
            return

        self._module_action_window(
            "GESTOR DE PAQUETES",
            actions=actions,
            search_action=search_action,
        )

    # ============================================================
    # CHAT WIFI - adaptación gráfica del módulo original
    # ============================================================
    def _on_chat(self):
        self._close_active_module()
        self._add_log("Module CHAT WIFI selected")

        win = tk.Toplevel(self.root)
        win.title("ULTRON — CHAT WIFI")
        win.configure(bg=BG)
        win.geometry("880x600")
        win.minsize(720, 500)
        win.transient(self.root)

        state = {
            "server": None,
            "client": None,
            "clients": {},
            "running": False,
            "mode": None,
            "username": "",
            "threads": [],
        }
        chat_lock = threading.Lock()

        header = tk.Frame(win, bg=BG_PANEL2, height=44)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header, text="// ULTRON CHAT / LOCAL WIFI",
            font=self.font_title, fg=ORANGE, bg=BG_PANEL2
        ).pack(side=tk.LEFT, padx=16, pady=8)

        status_var = tk.StringVar(value="● DESCONECTADO")
        status_lbl = tk.Label(
            header, textvariable=status_var,
            font=self.font_small, fg=RED, bg=BG_PANEL2
        )
        status_lbl.pack(side=tk.RIGHT, padx=16)

        body = tk.Frame(win, bg=BG)
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        left = tk.Frame(body, bg=BG_PANEL, width=245)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left.pack_propagate(False)

        center = tk.Frame(body, bg=BG_PANEL)
        center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(
            left, text="CONEXIÓN",
            font=self.font_small, fg=ORANGE, bg=BG_PANEL
        ).pack(anchor="w", padx=10, pady=(10, 8))

        username_var = tk.StringVar(value=socket.gethostname()[:12] or "Usuario")
        host_var = tk.StringVar(value="127.0.0.1")
        port_var = tk.StringVar(value="5050")

        for label, var in (
            ("Nombre de usuario", username_var),
            ("IP del servidor", host_var),
            ("Puerto", port_var),
        ):
            tk.Label(
                left, text=label,
                font=self.font_small, fg=TEXT_DIM, bg=BG_PANEL
            ).pack(anchor="w", padx=10, pady=(5, 2))
            tk.Entry(
                left, textvariable=var,
                font=self.font_mono,
                bg=BG_PANEL2, fg=TEXT,
                insertbackground=ORANGE,
                relief=tk.FLAT
            ).pack(fill=tk.X, padx=10)

        users_var = tk.StringVar(value="Usuarios: 0")
        tk.Label(
            left, textvariable=users_var,
            font=self.font_small, fg=TURQUOISE, bg=BG_PANEL
        ).pack(anchor="w", padx=10, pady=(14, 4))

        users_list = tk.Listbox(
            left,
            bg="#080808",
            fg=TEXT,
            font=self.font_small,
            relief=tk.FLAT,
            height=8,
            selectbackground=ORANGE_D
        )
        users_list.pack(fill=tk.X, padx=10, pady=(0, 10))

        messages = tk.Text(
            center,
            bg="#080808",
            fg=TEXT,
            font=self.font_mono,
            relief=tk.FLAT,
            wrap=tk.WORD,
            state=tk.DISABLED,
            padx=12,
            pady=10
        )
        msg_scroll = tk.Scrollbar(center, orient="vertical", command=messages.yview)
        messages.configure(yscrollcommand=msg_scroll.set)
        messages.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        msg_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        bottom = tk.Frame(win, bg=BG, height=52)
        bottom.pack(fill=tk.X, padx=12, pady=(0, 12))
        bottom.pack_propagate(False)

        message_var = tk.StringVar()
        entry = tk.Entry(
            bottom,
            textvariable=message_var,
            font=self.font_mono,
            bg=BG_PANEL2,
            fg=TEXT,
            insertbackground=ORANGE,
            relief=tk.FLAT
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8), ipady=8)

        def ui_log(text, tag=None):
            def update():
                if not messages.winfo_exists():
                    return
                messages.configure(state=tk.NORMAL)
                messages.insert(tk.END, text + "\n")
                messages.see(tk.END)
                messages.configure(state=tk.DISABLED)
            self.root.after(0, update)

        def ui_status(text, color):
            def update():
                if status_lbl.winfo_exists():
                    status_var.set(text)
                    status_lbl.configure(fg=color)
            self.root.after(0, update)

        def set_users(names):
            def update():
                if not users_list.winfo_exists():
                    return
                users_list.delete(0, tk.END)
                for name in names:
                    users_list.insert(tk.END, f"• {name}")
                users_var.set(f"Usuarios: {len(names)}")
            self.root.after(0, update)

        def send_line(sock, text):
            try:
                sock.sendall((text + "\n").encode("utf-8"))
                return True
            except Exception:
                return False

        def server_user_names():
            with chat_lock:
                names = [state["username"]]
                names.extend(
                    data["username"] for data in state["clients"].values()
                )
            return names

        def server_broadcast(text, exclude=None):
            dead = []
            with chat_lock:
                snapshot = list(state["clients"].items())
            for sock, data in snapshot:
                if sock is exclude:
                    continue
                if not send_line(sock, text):
                    dead.append(sock)
            for sock in dead:
                try:
                    sock.close()
                except Exception:
                    pass
                with chat_lock:
                    state["clients"].pop(sock, None)

        def server_send_users():
            names = server_user_names()
            payload = "USERLIST:" + "|".join(names)
            server_broadcast(payload)
            set_users(names)

        def handle_server_client(client, address, username):
            ui_log(f"• {username} se conectó ({address[0]}).")
            server_broadcast(f"SYS:{username} se conectó.", exclude=client)
            server_send_users()
            buffer = ""

            try:
                while state["running"] and state["mode"] == "server":
                    data = client.recv(4096)
                    if not data:
                        break
                    buffer += data.decode("utf-8", errors="replace")

                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip()
                        if not line:
                            continue
                        if line == "/exit":
                            raise ConnectionError("Cliente salió")
                        formatted = f"{username}: {line}"
                        ui_log(formatted)
                        server_broadcast("MSG:" + formatted, exclude=client)
            except Exception:
                pass
            finally:
                with chat_lock:
                    state["clients"].pop(client, None)
                try:
                    client.close()
                except Exception:
                    pass
                ui_log(f"• {username} se desconectó.")
                server_broadcast(f"SYS:{username} se desconectó.")
                server_send_users()

        def server_accept_loop():
            server = state["server"]
            while state["running"] and state["mode"] == "server":
                try:
                    client, address = server.accept()
                    client.settimeout(None)
                    raw = client.recv(1024)
                    if not raw:
                        client.close()
                        continue
                    username = raw.decode("utf-8", errors="replace").strip() or "Usuario"
                    with chat_lock:
                        state["clients"][client] = {
                            "username": username,
                            "address": address
                        }
                    send_line(client, "READY")
                    threading.Thread(
                        target=handle_server_client,
                        args=(client, address, username),
                        daemon=True
                    ).start()
                except OSError:
                    break
                except Exception as exc:
                    if state["running"]:
                        ui_log(f"Error del servidor: {exc}")

        def start_server():
            if state["running"]:
                ui_log("Ya existe una conexión activa.")
                return

            username = username_var.get().strip() or "Usuario"
            try:
                port = int(port_var.get().strip())
            except ValueError:
                ui_log("Puerto no válido.")
                return

            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            try:
                server.bind(("0.0.0.0", port))
                server.listen(10)
            except Exception as exc:
                ui_log(f"No se pudo iniciar el servidor: {exc}")
                try:
                    server.close()
                except Exception:
                    pass
                return

            state["server"] = server
            state["running"] = True
            state["mode"] = "server"
            state["username"] = username

            ui_status(f"● SERVIDOR :{port}", GREEN)
            ui_log(f"Servidor iniciado en el puerto {port}.")
            ui_log("Los otros equipos deben conectarse a la IP de este equipo.")
            set_users([username])
            self._add_log(f"CHAT servidor iniciado en puerto {port}")

            threading.Thread(
                target=server_accept_loop,
                daemon=True
            ).start()

        def client_receive_loop(client):
            buffer = ""
            try:
                while state["running"] and state["mode"] == "client":
                    data = client.recv(4096)
                    if not data:
                        break
                    buffer += data.decode("utf-8", errors="replace")

                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip()
                        if not line or line == "READY":
                            continue
                        if line.startswith("USERLIST:"):
                            raw = line.split(":", 1)[1]
                            set_users([x for x in raw.split("|") if x])
                        elif line.startswith("MSG:"):
                            ui_log(line[4:])
                        elif line.startswith("SYS:"):
                            ui_log("• " + line[4:])
                        else:
                            ui_log(line)
            except Exception as exc:
                if state["running"]:
                    ui_log(f"Conexión finalizada: {exc}")
            finally:
                if state["running"] and state["mode"] == "client":
                    self.root.after(0, disconnect)

        def connect_client():
            if state["running"]:
                ui_log("Ya existe una conexión activa.")
                return

            host = host_var.get().strip() or "127.0.0.1"
            username = username_var.get().strip() or "Usuario"

            try:
                port = int(port_var.get().strip())
            except ValueError:
                ui_log("Puerto no válido.")
                return

            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(8)

            try:
                client.connect((host, port))
                client.settimeout(None)
                send_line(client, username)
            except Exception as exc:
                ui_log(f"No se pudo conectar: {exc}")
                try:
                    client.close()
                except Exception:
                    pass
                return

            state["client"] = client
            state["running"] = True
            state["mode"] = "client"
            state["username"] = username

            ui_status(f"● CONECTADO {host}:{port}", TURQUOISE)
            ui_log(f"Conectado a {host}:{port}.")
            self._add_log(f"CHAT conectado a {host}:{port}")

            threading.Thread(
                target=client_receive_loop,
                args=(client,),
                daemon=True
            ).start()

        def disconnect():
            if not state["running"]:
                return

            mode = state["mode"]
            state["running"] = False

            if mode == "client":
                client = state.get("client")
                if client:
                    try:
                        send_line(client, "/exit")
                        client.shutdown(socket.SHUT_RDWR)
                    except Exception:
                        pass
                    try:
                        client.close()
                    except Exception:
                        pass
                state["client"] = None

            elif mode == "server":
                with chat_lock:
                    clients = list(state["clients"].keys())
                    state["clients"].clear()

                for client in clients:
                    try:
                        send_line(client, "SYS:Servidor cerrado.")
                        client.shutdown(socket.SHUT_RDWR)
                    except Exception:
                        pass
                    try:
                        client.close()
                    except Exception:
                        pass

                server = state.get("server")
                if server:
                    try:
                        server.close()
                    except Exception:
                        pass
                state["server"] = None

            state["mode"] = None
            ui_status("● DESCONECTADO", RED)
            set_users([])
            ui_log("Chat desconectado.")
            self._add_log("CHAT desconectado")

        def send_message():
            text = message_var.get().strip()
            if not text:
                return
            if not state["running"]:
                ui_log("Primero inicia un servidor o conéctate a uno.")
                return

            username = state["username"]
            if state["mode"] == "client":
                client = state.get("client")
                if client and send_line(client, text):
                    ui_log(f"{username}: {text}")
                else:
                    ui_log("No se pudo enviar el mensaje.")
            else:
                formatted = f"{username}: {text}"
                ui_log(formatted)
                server_broadcast("MSG:" + formatted)

            message_var.set("")

        tk.Button(
            left, text="INICIAR SERVIDOR",
            font=self.font_small,
            fg=GREEN, bg=BG_PANEL2,
            activebackground=GRAY,
            relief=tk.FLAT,
            command=start_server,
            padx=8, pady=8
        ).pack(fill=tk.X, padx=10, pady=(4, 3))

        tk.Button(
            left, text="CONECTAR COMO CLIENTE",
            font=self.font_small,
            fg=TURQUOISE, bg=BG_PANEL2,
            activebackground=GRAY,
            relief=tk.FLAT,
            command=connect_client,
            padx=8, pady=8
        ).pack(fill=tk.X, padx=10, pady=3)

        tk.Button(
            left, text="DESCONECTAR",
            font=self.font_small,
            fg=RED, bg=BG_PANEL2,
            activebackground=GRAY,
            relief=tk.FLAT,
            command=disconnect,
            padx=8, pady=8
        ).pack(fill=tk.X, padx=10, pady=3)

        tk.Button(
            bottom, text="ENVIAR",
            font=self.font_small,
            fg=ORANGE, bg=BG_PANEL2,
            activeforeground=ORANGE_L,
            activebackground=GRAY,
            relief=tk.FLAT,
            command=send_message,
            padx=18, pady=7
        ).pack(side=tk.RIGHT)

        entry.bind("<Return>", lambda _e: send_message())

        def close_chat():
            disconnect()
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", close_chat)
        ui_log("ULTRON CHAT listo.")
        ui_log("Inicia un servidor o escribe la IP de otro equipo y conéctate.")

    def _theme_dict_from_globals(self):
        return {
            "BG": BG,
            "BG_PANEL": BG_PANEL,
            "BG_PANEL2": BG_PANEL2,
            "PRIMARY": ORANGE,
            "PRIMARY_L": ORANGE_L,
            "PRIMARY_D": ORANGE_D,
            "PRIMARY_DIM": ORANGE_DIM,
            "SECONDARY": TURQUOISE,
            "SECONDARY_D": TURQUOISE_D,
            "SECONDARY_DIM": TURQUOISE_DIM,
            "TEXT": TEXT,
            "TEXT_DIM": TEXT_DIM,
            "GOOD": GREEN,
            "DANGER": RED,
        }

    def _pick_color(self, var):
        current = var.get()
        color = colorchooser.askcolor(
            color=current,
            title="ULTRON // Seleccionar color"
        )[1]
        if color:
            var.set(color)

    def _recolor_widget_tree(self, widget, old_theme, new_theme):
        """Recolorea widgets ya existentes sin reconstruir toda la aplicación."""
        color_map = {
            old_theme["BG"]: new_theme["BG"],
            old_theme["BG_PANEL"]: new_theme["BG_PANEL"],
            old_theme["BG_PANEL2"]: new_theme["BG_PANEL2"],
            old_theme["PRIMARY"]: new_theme["PRIMARY"],
            old_theme["PRIMARY_L"]: new_theme["PRIMARY_L"],
            old_theme["PRIMARY_D"]: new_theme["PRIMARY_D"],
            old_theme["PRIMARY_DIM"]: new_theme["PRIMARY_DIM"],
            old_theme["SECONDARY"]: new_theme["SECONDARY"],
            old_theme["SECONDARY_D"]: new_theme["SECONDARY_D"],
            old_theme["SECONDARY_DIM"]: new_theme["SECONDARY_DIM"],
            old_theme["TEXT"]: new_theme["TEXT"],
            old_theme["TEXT_DIM"]: new_theme["TEXT_DIM"],
            old_theme["GOOD"]: new_theme["GOOD"],
            old_theme["DANGER"]: new_theme["DANGER"],
            "#080808": new_theme["BG"],
            "#1a1a1a": new_theme["BG_PANEL2"],
            "#2a2a2a": new_theme["PRIMARY_DIM"],
        }

        options = (
            "background", "foreground",
            "activebackground", "activeforeground",
            "highlightbackground", "highlightcolor",
            "insertbackground", "selectbackground", "selectforeground",
            "troughcolor"
        )

        for option in options:
            try:
                current = widget.cget(option)
                if current in color_map:
                    widget.configure(**{option: color_map[current]})
            except Exception:
                pass

        for child in widget.winfo_children():
            self._recolor_widget_tree(child, old_theme, new_theme)

    def _apply_theme_live(self, theme):
        """Aplica el tema inmediatamente; no requiere reiniciar ULTRON."""
        old_theme = self._theme_dict_from_globals()
        apply_theme_globals(theme)

        # Recolorear todos los widgets, incluidas ventanas secundarias abiertas.
        self._recolor_widget_tree(self.root, old_theme, theme)

        # Los Canvas tienen gráficos propios; se redibujan con el nuevo tema.
        try:
            self.core_canvas.delete("all")
            self.core_canvas.configure(bg=BG)
            self._init_core()
        except Exception:
            pass

        try:
            self.map_canvas.configure(bg=BG_PANEL)
            self._draw_map()
        except Exception:
            pass

        self.root.configure(bg=BG)
        self.root.update_idletasks()

    def _list_audio_sources(self):
        """Devuelve fuentes de audio visibles en el sistema."""
        if self.system.is_windows:
            return self.system.input_devices()
        devices = []
        try:
            out = subprocess.check_output(
                ["pactl", "list", "short", "sources"],
                text=True,
                stderr=subprocess.DEVNULL
            )
            for line in out.splitlines():
                parts = line.split("\t")
                if len(parts) >= 2:
                    name = parts[1].strip()
                    # Ocultar monitores de salida para no confundir.
                    if name.endswith(".monitor"):
                        continue
                    devices.append(name)
        except Exception:
            pass
        return devices

    def _list_audio_sinks(self):
        """Devuelve salidas de audio visibles en PipeWire/PulseAudio."""
        devices = []
        try:
            out = subprocess.check_output(
                ["pactl", "list", "short", "sinks"],
                text=True,
                stderr=subprocess.DEVNULL
            )
            for line in out.splitlines():
                parts = line.split("\t")
                if len(parts) >= 2:
                    devices.append(parts[1].strip())
        except Exception:
            pass
        return devices

    def _resolve_input_device(self):
        if self.audio_input_device and self.audio_input_device != "Automático":
            return self.audio_input_device
        if self.system.is_windows:
            return self.system.default_input()
        try:
            return subprocess.check_output(
                ["pactl", "get-default-source"],
                text=True,
                stderr=subprocess.DEVNULL
            ).strip()
        except Exception:
            return ""

    def _resolve_output_device(self):
        if self.audio_output_device and self.audio_output_device != "Automático":
            return self.audio_output_device
        try:
            return subprocess.check_output(
                ["pactl", "get-default-sink"],
                text=True,
                stderr=subprocess.DEVNULL
            ).strip()
        except Exception:
            return ""

    def _test_microphone(self, parent=None):
        """Graba 3 segundos y muestra si se pudo capturar audio."""
        def worker():
            tmp = tempfile.NamedTemporaryFile(
                prefix="ultron_mic_test_",
                suffix=".wav",
                delete=False
            )
            path = tmp.name
            tmp.close()

            try:
                device = self._resolve_input_device()
                size = self.system.audio.test_microphone(
                    path,
                    input_device=device,
                    seconds=3
                )
                msg = (
                    f"Micrófono detectado.\nDispositivo: {device or 'predeterminado'}\n"
                    f"Se capturaron {size} bytes de audio."
                    if size > 1000
                    else "No se detectó una grabación válida."
                )
            except Exception as exc:
                msg = f"Error probando micrófono:\n{exc}"
            finally:
                try:
                    os.remove(path)
                except Exception:
                    pass

            self.root.after(
                0,
                lambda: self._show_module("PRUEBA DE MICRÓFONO", msg)
            )

        threading.Thread(target=worker, daemon=True).start()

    def _test_voice_output(self, parent=None):
        """Prueba la voz neural mediante el adaptador de audio del sistema."""
        def worker():
            try:
                device = self._resolve_output_device()
                self.system.speak(
                    "Sistema de audio de ULTRON operativo.",
                    output_device=device or None,
                    volume=self.ultron_volume,
                )
                msg = f"Prueba de voz completada.\nSalida: {device or 'predeterminada'}"
            except Exception as exc:
                msg = f"Error probando salida de audio:\n{exc}"

            self.root.after(
                0,
                lambda: self._show_module("PRUEBA DE VOZ", msg)
            )

        threading.Thread(target=worker, daemon=True).start()

    def _on_appearance(self):
        self._add_log("Module PREFERENCIAS selected")

        win = tk.Toplevel(self.root)
        win.title("ULTRON — PREFERENCIAS")
        win.configure(bg=BG)
        win.geometry("900x600")
        win.minsize(760, 520)
        win.transient(self.root)

        header = tk.Frame(win, bg=BG_PANEL2, height=48)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header, text="// PREFERENCIAS / APARIENCIA",
            font=self.font_title, fg=ORANGE, bg=BG_PANEL2
        ).pack(side=tk.LEFT, padx=18, pady=9)

        status = tk.Label(
            header, text="● LIVE THEME ENGINE",
            font=self.font_small, fg=TURQUOISE, bg=BG_PANEL2
        )
        status.pack(side=tk.RIGHT, padx=18)

        # Contenedor con scroll independiente para Preferencias.
        pref_outer = tk.Frame(win, bg=BG)
        pref_outer.pack(fill=tk.BOTH, expand=True)

        pref_canvas = tk.Canvas(
            pref_outer,
            bg=BG,
            highlightthickness=0,
            bd=0
        )
        pref_scrollbar = tk.Scrollbar(
            pref_outer,
            orient="vertical",
            command=pref_canvas.yview,
            bg=BG_PANEL2,
            troughcolor=BG,
            activebackground=ORANGE_D
        )

        body = tk.Frame(pref_canvas, bg=BG)
        body_window = pref_canvas.create_window(
            (0, 0),
            window=body,
            anchor="nw"
        )

        def _sync_pref_scrollregion(_event=None):
            pref_canvas.configure(scrollregion=pref_canvas.bbox("all"))

        def _sync_pref_width(event):
            # Mantiene el contenido al ancho visible del canvas.
            pref_canvas.itemconfigure(body_window, width=event.width)

        body.bind("<Configure>", _sync_pref_scrollregion)
        pref_canvas.bind("<Configure>", _sync_pref_width)
        pref_canvas.configure(yscrollcommand=pref_scrollbar.set)

        pref_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        pref_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def _pref_mousewheel(event):
            if getattr(event, "delta", 0):
                pref_canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")
            elif getattr(event, "num", None) == 4:
                pref_canvas.yview_scroll(-1, "units")
            elif getattr(event, "num", None) == 5:
                pref_canvas.yview_scroll(1, "units")

        def _bind_pref_scroll(_event=None):
            pref_canvas.bind_all("<MouseWheel>", _pref_mousewheel)
            pref_canvas.bind_all("<Button-4>", _pref_mousewheel)
            pref_canvas.bind_all("<Button-5>", _pref_mousewheel)

        def _unbind_pref_scroll(_event=None):
            pref_canvas.unbind_all("<MouseWheel>")
            pref_canvas.unbind_all("<Button-4>")
            pref_canvas.unbind_all("<Button-5>")

        # Toda la ventana de preferencias responde a la rueda.
        pref_canvas.bind("<Enter>", _bind_pref_scroll)
        pref_canvas.bind("<Leave>", _unbind_pref_scroll)
        body.bind("<Enter>", _bind_pref_scroll)
        body.bind("<Leave>", _unbind_pref_scroll)

        content = tk.Frame(body, bg=BG)
        content.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)

        controls = tk.Frame(content, bg=BG, width=470)
        controls.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        controls.pack_propagate(False)

        preview_side = tk.Frame(content, bg=BG_PANEL, width=360, height=500)
        preview_side.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        preview_side.pack_propagate(False)

        tk.Label(
            controls, text="APARIENCIAS PREDEFINIDAS",
            font=self.font_small, fg=TEXT_DIM, bg=BG
        ).pack(anchor="w", pady=(0, 6))

        preset_frame = tk.Frame(controls, bg=BG)
        preset_frame.pack(fill=tk.X)

        current = self._theme_dict_from_globals()
        color_vars = {
            "BG": tk.StringVar(value=current["BG"]),
            "BG_PANEL": tk.StringVar(value=current["BG_PANEL"]),
            "BG_PANEL2": tk.StringVar(value=current["BG_PANEL2"]),
            "PRIMARY": tk.StringVar(value=current["PRIMARY"]),
            "PRIMARY_L": tk.StringVar(value=current["PRIMARY_L"]),
            "SECONDARY": tk.StringVar(value=current["SECONDARY"]),
            "TEXT": tk.StringVar(value=current["TEXT"]),
            "TEXT_DIM": tk.StringVar(value=current["TEXT_DIM"]),
            "GOOD": tk.StringVar(value=current["GOOD"]),
            "DANGER": tk.StringVar(value=current["DANGER"]),
        }

        # Valores internos que no se muestran como selector principal.
        hidden_colors = {
            "PRIMARY_D": current["PRIMARY_D"],
            "PRIMARY_DIM": current["PRIMARY_DIM"],
            "SECONDARY_D": current["SECONDARY_D"],
            "SECONDARY_DIM": current["SECONDARY_DIM"],
        }

        tk.Label(
            preview_side, text="VISUALIZACIÓN PREVIA",
            font=self.font_small, fg=ORANGE, bg=BG_PANEL
        ).pack(anchor="w", padx=12, pady=(12, 4))

        tk.Label(
            preview_side,
            text="Los cambios se muestran aquí antes de guardarlos.",
            font=self.font_small, fg=TEXT_DIM, bg=BG_PANEL
        ).pack(anchor="w", padx=12, pady=(0, 8))

        preview = tk.Canvas(
            preview_side, bg=BG, highlightthickness=0
        )
        preview.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        def safe_color(key, fallback):
            value = color_vars[key].get().strip()
            if re.match(r"^#[0-9a-fA-F]{6}$", value):
                return value
            return fallback

        def refresh_preview(*_):
            preview.delete("all")
            preview.update_idletasks()
            w = max(preview.winfo_width(), 300)
            h = max(preview.winfo_height(), 380)

            bg = safe_color("BG", BG)
            panel = safe_color("BG_PANEL", BG_PANEL)
            panel2 = safe_color("BG_PANEL2", BG_PANEL2)
            pri = safe_color("PRIMARY", ORANGE)
            pril = safe_color("PRIMARY_L", ORANGE_L)
            sec = safe_color("SECONDARY", TURQUOISE)
            text = safe_color("TEXT", TEXT)
            dim = safe_color("TEXT_DIM", TEXT_DIM)
            good = safe_color("GOOD", GREEN)

            preview.configure(bg=bg)

            # Marco general.
            preview.create_rectangle(8, 8, w-8, h-8, fill=bg, outline=pri, width=1)

            # Top bar.
            preview.create_rectangle(18, 18, w-18, 58, fill=panel2, outline="")
            preview.create_text(
                30, 38, text="ULTRON // CORE",
                anchor="w", fill=pri, font=self.font_small
            )
            preview.create_text(
                w-30, 38, text="● ONLINE",
                anchor="e", fill=sec, font=self.font_small
            )

            # Panel de módulos.
            left_w = int(w * 0.34)
            preview.create_rectangle(
                18, 70, left_w, h-85,
                fill=panel, outline=hidden_colors["PRIMARY_DIM"], width=1
            )
            preview.create_text(
                30, 90, text="MODULES",
                anchor="w", fill=pri, font=self.font_small
            )

            module_names = [
                "01  CONCIENCIA",
                "02  SISTEMA",
                "03  PREFERENCIAS",
                "04  RED",
                "05  SEGURIDAD",
                "06  ARCHIVOS",
            ]
            yy = 112
            for i, name in enumerate(module_names):
                preview.create_rectangle(
                    28, yy, left_w-10, yy+34,
                    fill=panel2,
                    outline=pri if i == 2 else hidden_colors["PRIMARY_DIM"],
                    width=1
                )
                preview.create_text(
                    39, yy+17, text=name,
                    anchor="w",
                    fill=pril if i == 2 else pri,
                    font=self.font_small
                )
                yy += 42

            # Centro / core.
            center_x = int((left_w + (w-18)) / 2)
            center_y = int(h * 0.43)
            r = min(int((w-left_w)*0.23), 82)

            for rr, width in [(r+28, 1), (r+14, 2), (r, 2), (r-16, 2)]:
                preview.create_oval(
                    center_x-rr, center_y-rr,
                    center_x+rr, center_y+rr,
                    outline=pri, width=width
                )

            preview.create_oval(
                center_x-r//2, center_y-r//2,
                center_x+r//2, center_y+r//2,
                fill=panel2, outline=pril, width=2
            )
            preview.create_oval(
                center_x-16, center_y-16,
                center_x+16, center_y+16,
                fill=pril, outline=""
            )

            # Métricas inferiores.
            metric_y = h - 70
            metric_w = max(58, int((w-56)/4))
            for i, label in enumerate(("CPU", "RAM", "DISK", "NET")):
                x1 = 18 + i*(metric_w+6)
                x2 = x1 + metric_w
                preview.create_rectangle(
                    x1, metric_y, x2, h-20,
                    fill=panel, outline=""
                )
                preview.create_text(
                    (x1+x2)/2, metric_y+14,
                    text=label, fill=dim, font=self.font_small
                )
                preview.create_text(
                    (x1+x2)/2, metric_y+34,
                    text="OK" if label == "NET" else "42%",
                    fill=good if label == "NET" else pri,
                    font=self.font_small
                )

            preview.create_text(
                center_x, center_y + r + 48,
                text="LIVE THEME PREVIEW",
                fill=text, font=self.font_small
            )

        def build_theme_from_vars():
            return {
                "BG": safe_color("BG", BG),
                "BG_PANEL": safe_color("BG_PANEL", BG_PANEL),
                "BG_PANEL2": safe_color("BG_PANEL2", BG_PANEL2),
                "PRIMARY": safe_color("PRIMARY", ORANGE),
                "PRIMARY_L": safe_color("PRIMARY_L", ORANGE_L),
                "PRIMARY_D": hidden_colors["PRIMARY_D"],
                "PRIMARY_DIM": hidden_colors["PRIMARY_DIM"],
                "SECONDARY": safe_color("SECONDARY", TURQUOISE),
                "SECONDARY_D": hidden_colors["SECONDARY_D"],
                "SECONDARY_DIM": hidden_colors["SECONDARY_DIM"],
                "TEXT": safe_color("TEXT", TEXT),
                "TEXT_DIM": safe_color("TEXT_DIM", TEXT_DIM),
                "GOOD": safe_color("GOOD", GREEN),
                "DANGER": safe_color("DANGER", RED),
            }

        def load_vars_from_theme(theme):
            visible_keys = (
                "BG", "BG_PANEL", "BG_PANEL2", "PRIMARY", "PRIMARY_L",
                "SECONDARY", "TEXT", "TEXT_DIM", "GOOD", "DANGER"
            )
            for key in visible_keys:
                color_vars[key].set(theme[key])

            for key in hidden_colors:
                hidden_colors[key] = theme[key]

            refresh_preview()

        def apply_preset(name):
            theme = THEMES[name].copy()
            load_vars_from_theme(theme)
            self._apply_theme_live(theme)
            save_theme_config({"theme": name})
            self._add_log(f"Apariencia aplicada en vivo: {name}")
            status.configure(text=f"● {name} APLICADO", fg=TURQUOISE)

        for column in range(3):
            preset_frame.columnconfigure(column, weight=1)

        for index, name in enumerate(THEMES):
            btn = tk.Button(
                preset_frame,
                text=name,
                font=self.font_small,
                fg=ORANGE,
                bg=BG_PANEL2,
                activeforeground=ORANGE_L,
                activebackground=GRAY,
                relief=tk.FLAT,
                cursor="hand2",
                padx=5,
                pady=7,
                command=lambda n=name: apply_preset(n)
            )
            btn.grid(
                row=index // 3,
                column=index % 3,
                sticky="ew",
                padx=3,
                pady=4,
            )

        tk.Frame(controls, bg=GRAY2, height=1).pack(fill=tk.X, pady=14)

        tk.Label(
            controls, text="CREAR APARIENCIA PERSONALIZADA",
            font=self.font_small, fg=ORANGE, bg=BG
        ).pack(anchor="w", pady=(0, 6))

        tk.Label(
            controls,
            text=(
                "Cambia los colores y observa el resultado en la vista previa. "
                "Al aplicar, toda la interfaz cambia inmediatamente."
            ),
            font=self.font_small,
            fg=TEXT_DIM,
            bg=BG,
            justify="left",
            wraplength=530
        ).pack(anchor="w", pady=(0, 10))

        grid = tk.Frame(controls, bg=BG)
        grid.pack(fill=tk.X)

        labels = [
            ("Fondo principal", "BG"),
            ("Panel", "BG_PANEL"),
            ("Panel secundario", "BG_PANEL2"),
            ("Color primario", "PRIMARY"),
            ("Brillo primario", "PRIMARY_L"),
            ("Color secundario", "SECONDARY"),
            ("Texto", "TEXT"),
            ("Texto tenue", "TEXT_DIM"),
            ("Estado OK", "GOOD"),
            ("Alerta", "DANGER"),
        ]

        for i, (label, key) in enumerate(labels):
            row = i
            tk.Label(
                grid, text=label, font=self.font_small,
                fg=TEXT_DIM, bg=BG, width=18, anchor="w"
            ).grid(row=row, column=0, sticky="w", padx=(0, 6), pady=4)

            entry = tk.Entry(
                grid,
                textvariable=color_vars[key],
                width=12,
                font=self.font_mono,
                bg=BG_PANEL2,
                fg=TEXT,
                insertbackground=ORANGE,
                relief=tk.FLAT
            )
            entry.grid(row=row, column=1, padx=4, pady=4)

            tk.Button(
                grid,
                text="ELEGIR",
                font=self.font_small,
                fg=ORANGE,
                bg=BG_PANEL2,
                activeforeground=ORANGE_L,
                activebackground=GRAY,
                relief=tk.FLAT,
                width=9,
                command=lambda v=color_vars[key]: self._pick_color(v)
            ).grid(row=row, column=2, padx=(6, 0), pady=4)

        # Preview en tiempo real al editar cualquier código hexadecimal.
        for var in color_vars.values():
            var.trace_add("write", refresh_preview)

        tk.Frame(controls, bg=GRAY2, height=1).pack(fill=tk.X, pady=14)

        tk.Label(
            controls, text="AUDIO",
            font=self.font_small, fg=ORANGE, bg=BG
        ).pack(anchor="w", pady=(0, 6))

        tk.Label(
            controls,
            text="Automático usa los dispositivos predeterminados del sistema.",
            font=self.font_small,
            fg=TEXT_DIM,
            bg=BG,
            wraplength=430,
            justify="left"
        ).pack(anchor="w", pady=(0, 8))

        audio_grid = tk.Frame(controls, bg=BG)
        audio_grid.pack(fill=tk.X)

        input_options = ["Automático"] + self._list_audio_sources()
        output_options = ["Automático"] + self._list_audio_sinks()

        input_var = tk.StringVar(
            value=self.audio_input_device or "Automático"
        )
        output_var = tk.StringVar(
            value=self.audio_output_device or "Automático"
        )
        volume_var = tk.IntVar(value=self.ultron_volume)

        tk.Label(
            audio_grid, text="Entrada",
            font=self.font_small, fg=TEXT_DIM, bg=BG, width=14, anchor="w"
        ).grid(row=0, column=0, sticky="w", pady=4)

        input_menu = tk.OptionMenu(audio_grid, input_var, *input_options)
        input_menu.configure(
            bg=BG_PANEL2, fg=TEXT, relief=tk.FLAT,
            activebackground=GRAY, activeforeground=ORANGE_L,
            highlightthickness=0, width=28
        )
        input_menu["menu"].configure(bg=BG_PANEL2, fg=TEXT)
        input_menu.grid(row=0, column=1, sticky="w", pady=4)

        tk.Label(
            audio_grid, text="Salida",
            font=self.font_small, fg=TEXT_DIM, bg=BG, width=14, anchor="w"
        ).grid(row=1, column=0, sticky="w", pady=4)

        output_menu = tk.OptionMenu(audio_grid, output_var, *output_options)
        output_menu.configure(
            bg=BG_PANEL2, fg=TEXT, relief=tk.FLAT,
            activebackground=GRAY, activeforeground=ORANGE_L,
            highlightthickness=0, width=28
        )
        output_menu["menu"].configure(bg=BG_PANEL2, fg=TEXT)
        output_menu.grid(row=1, column=1, sticky="w", pady=4)

        tk.Label(
            audio_grid, text="Volumen ULTRON",
            font=self.font_small, fg=TEXT_DIM, bg=BG, width=14, anchor="w"
        ).grid(row=2, column=0, sticky="w", pady=6)

        volume_scale = tk.Scale(
            audio_grid,
            from_=10, to=100,
            orient=tk.HORIZONTAL,
            variable=volume_var,
            bg=BG,
            fg=TEXT,
            troughcolor=BG_PANEL2,
            activebackground=ORANGE,
            highlightthickness=0,
            length=220
        )
        volume_scale.grid(row=2, column=1, sticky="w", pady=2)

        audio_buttons = tk.Frame(controls, bg=BG)
        audio_buttons.pack(fill=tk.X, pady=(8, 0))

        def apply_audio_preferences():
            self.audio_input_device = input_var.get()
            self.audio_output_device = output_var.get()
            self.ultron_volume = volume_var.get()
            self._add_log(
                f"Audio actualizado: entrada={self.audio_input_device}, "
                f"salida={self.audio_output_device}, volumen={self.ultron_volume}%"
            )

        tk.Button(
            audio_buttons,
            text="[ PROBAR MICRÓFONO ]",
            font=self.font_small,
            fg=TURQUOISE,
            bg=BG_PANEL2,
            relief=tk.FLAT,
            command=lambda: (
                apply_audio_preferences(),
                self._test_microphone(win)
            ),
            padx=10, pady=7
        ).pack(side=tk.LEFT, padx=(0, 6))

        tk.Button(
            audio_buttons,
            text="[ PROBAR VOZ ]",
            font=self.font_small,
            fg=ORANGE,
            bg=BG_PANEL2,
            relief=tk.FLAT,
            command=lambda: (
                apply_audio_preferences(),
                self._test_voice_output(win)
            ),
            padx=10, pady=7
        ).pack(side=tk.LEFT)

        actions = tk.Frame(controls, bg=BG)
        actions.pack(fill=tk.X, pady=(16, 0))

        def preview_on_real_ui():
            theme = build_theme_from_vars()
            self._apply_theme_live(theme)
            self._add_log("Vista previa aplicada temporalmente")
            status.configure(text="● PREVIEW ACTIVO", fg=TURQUOISE)

        def save_custom():
            custom = build_theme_from_vars()
            save_theme_config({
                "theme": "CUSTOM",
                "custom_theme": custom
            })
            self._apply_theme_live(custom)
            self._add_log("Apariencia personalizada guardada y aplicada")
            status.configure(text="● PERSONALIZADO GUARDADO", fg=GREEN)

        tk.Button(
            actions,
            text="[ PROBAR EN ULTRON ]",
            font=self.font_small,
            fg=TURQUOISE,
            bg=BG_PANEL2,
            activeforeground=TEXT,
            activebackground=GRAY,
            relief=tk.FLAT,
            padx=13,
            pady=8,
            command=preview_on_real_ui
        ).pack(side=tk.LEFT, padx=(0, 6))

        tk.Button(
            actions,
            text="[ GUARDAR Y APLICAR ]",
            font=self.font_small,
            fg=ORANGE,
            bg=BG_PANEL2,
            activeforeground=ORANGE_L,
            activebackground=GRAY,
            relief=tk.FLAT,
            padx=13,
            pady=8,
            command=save_custom
        ).pack(side=tk.RIGHT)

        preview.bind("<Configure>", refresh_preview)
        refresh_preview()

    def _close_active_module(self):
        win = getattr(self, "_active_module_window", None)
        if win is not None:
            try:
                if win.winfo_exists():
                    win.destroy()
            except Exception:
                pass
        self._active_module_window = None

    def _show_module(self, title, content):
        self._close_active_module()
        win = tk.Toplevel(self.root)
        win.title(f"ULTRON — {title}")
        win.configure(bg=BG)
        win.geometry("700x500")
        win.minsize(560, 400)
        win.transient(self.root)

        header = tk.Frame(
            win,
            bg=BG_PANEL2,
            height=46
        )
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text=f"// {title.upper()}",
            font=self.font_title,
            fg=ORANGE,
            bg=BG_PANEL2
        ).pack(side=tk.LEFT, padx=18, pady=9)

        tk.Label(
            header,
            text="HUD MODULE",
            font=self.font_small,
            fg=TURQUOISE,
            bg=BG_PANEL2
        ).pack(side=tk.RIGHT, padx=18)

        shell = tk.Frame(win, bg=BG)
        shell.pack(
            fill=tk.BOTH,
            expand=True,
            padx=14,
            pady=14
        )

        hud, panel = self._hud_panel(
            shell,
            bg="#080808",
            border=TURQUOISE
        )
        hud.pack(fill=tk.BOTH, expand=True)

        # Barra decorativa interna.
        title_row = tk.Frame(
            panel,
            bg="#080808",
            height=30
        )
        title_row.pack(fill=tk.X, padx=8, pady=(5, 3))
        title_row.pack_propagate(False)

        tk.Label(
            title_row,
            text="DATA STREAM",
            font=self.font_small,
            fg=TEXT_DIM,
            bg="#080808"
        ).pack(side=tk.LEFT)

        tk.Label(
            title_row,
            text="● ONLINE",
            font=self.font_small,
            fg=TURQUOISE,
            bg="#080808"
        ).pack(side=tk.RIGHT)

        text_wrap = tk.Frame(
            panel,
            bg="#080808"
        )
        text_wrap.pack(
            fill=tk.BOTH,
            expand=True,
            padx=8,
            pady=(0, 7)
        )

        txt = tk.Text(
            text_wrap,
            bg="#080808",
            fg=TEXT,
            font=self.font_mono,
            relief=tk.FLAT,
            padx=14,
            pady=12,
            wrap=tk.WORD,
            insertbackground=ORANGE,
            selectbackground=ORANGE_D
        )

        txt_scroll = tk.Scrollbar(
            text_wrap,
            orient="vertical",
            command=txt.yview,
            bg=BG_PANEL2,
            troughcolor=BG,
            activebackground=ORANGE_D
        )

        txt.configure(
            yscrollcommand=txt_scroll.set
        )

        txt.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True
        )
        txt_scroll.pack(
            side=tk.RIGHT,
            fill=tk.Y
        )

        txt.insert(tk.END, content)
        txt.configure(state=tk.DISABLED)

        btn_frame = tk.Frame(
            win,
            bg=BG
        )
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Button(
            btn_frame,
            text="[ CERRAR ]",
            font=self.font_small,
            fg=ORANGE,
            bg=BG_PANEL2,
            activeforeground=ORANGE_L,
            activebackground=GRAY,
            relief=tk.FLAT,
            command=win.destroy,
            padx=18,
            pady=6
        ).pack()



def _bring_main_window_to_front(root):
    """Raise the GUI portably; briefly use topmost only on Windows."""
    try:
        if not root.winfo_exists():
            return
        root.deiconify()
        if os.name == "nt":
            root.attributes("-topmost", True)
        root.lift()
        root.focus_force()
        if os.name == "nt":
            root.after(
                700,
                lambda: root.attributes("-topmost", False)
                if root.winfo_exists() else None,
            )
    except tk.TclError:
        pass


def main():
    # Do not propagate a legacy/shared API key into child processes.
    os.environ.pop("GROQ_API_KEY", None)
    root = tk.Tk()
    root.withdraw()

    saved_user = UltronAuth.try_saved_session()

    if saved_user:
        root.deiconify()
        app = UltronGUI(root, current_user=saved_user)
        root.after(120, lambda: _bring_main_window_to_front(root))
        root.mainloop()
        return

    auth = UltronAuth(root)
    root.wait_window(auth.win)

    if not auth.authenticated:
        root.destroy()
        return

    root.deiconify()
    app = UltronGUI(root, current_user=auth.username)
    root.after(120, lambda: _bring_main_window_to_front(root))
    root.mainloop()


if __name__ == "__main__":
    main()
                     

