#!/usr/bin/env python3
"""
ULTRON // CORE  -  GUI V2
Centro de operaciones futurista para Linux
Estética: negro + naranja | Core con anillos orbitando | Mapa plano
"""

import tkinter as tk
try:
    import customtkinter as ctk
    HAS_CTK = True
except Exception:
    ctk = None
    HAS_CTK = False
from tkinter import font as tkfont, colorchooser
import math
import time
import socket
import platform
import subprocess
import json
import os
import re
import threading
import asyncio
import shlex
import tempfile
import shutil
import urllib.request
import urllib.error
import urllib.parse
import uuid
import wave
import io
from pathlib import Path

# Load private ULTRON secrets from the user's config directory.
# The file is outside the project/Git repository and should be chmod 600.
_ultron_secret_file=Path.home()/".config"/"ultron"/"secrets.env"
try:
    if _ultron_secret_file.exists():
        for _line in _ultron_secret_file.read_text().splitlines():
            _line=_line.strip()
            if not _line or _line.startswith("#") or "=" not in _line:
                continue
            _k,_v=_line.split("=",1)
            if _k and _v:
                os.environ.setdefault(_k.strip(),_v.strip())
except Exception:
    pass

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


def run_cmd(cmd):
    try:
        return subprocess.check_output(
            cmd, shell=True, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return "No disponible"


class UltronCore:
    def __init__(self, canvas, cx, cy, base_radius=110, on_activate=None):
        self.canvas = canvas
        self.cx = cx
        self.cy = cy
        self.base_r = base_radius
        self.on_activate = on_activate
        self.angle = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.base_speed = [0.35, -0.22, 0.48, -0.15, 0.28]
        self.speed = list(self.base_speed)
        self.state = "IDLE"
        self.pulse_phase = 0.0
        self.rings = []
        self.items = []
        self._build()

    def _build(self):
        c = self.canvas
        cx, cy, r = self.cx, self.cy, self.base_r
        for scale in [1.55, 1.42, 1.30]:
            self.items.append(c.create_oval(cx-r*scale, cy-r*scale, cx+r*scale, cy+r*scale, outline=ORANGE_DIM, width=1, tags=("ultron_core",)))
        ring_specs = [(1.22,2,ORANGE),(1.08,3,ORANGE_L),(0.94,2,ORANGE),(0.80,3,ORANGE_L),(0.66,2,ORANGE_D)]
        for rel, width, color in ring_specs:
            self.rings.append(c.create_arc(cx-r*rel, cy-r*rel, cx+r*rel, cy+r*rel, start=0, extent=300, style=tk.ARC, outline=color, width=width, tags=("ultron_core",)))
            self.rings.append(c.create_arc(cx-r*rel, cy-r*rel, cx+r*rel, cy+r*rel, start=180, extent=120, style=tk.ARC, outline=ORANGE_D, width=max(1,width-1), tags=("ultron_core",)))
        self.outer_core = c.create_oval(cx-r*0.48, cy-r*0.48, cx+r*0.48, cy+r*0.48, fill="#1a0a00", outline=ORANGE_D, width=2, tags=("ultron_core","core_click"))
        self.mid_core = c.create_oval(cx-r*0.38, cy-r*0.38, cx+r*0.38, cy+r*0.38, fill="#2a1200", outline=ORANGE, width=1, tags=("ultron_core","core_click"))
        self.inner_core = c.create_oval(cx-r*0.18, cy-r*0.18, cx+r*0.18, cy+r*0.18, fill=ORANGE, outline=ORANGE_L, width=1, tags=("ultron_core","core_click"))
        self.center_core = c.create_oval(cx-r*0.08, cy-r*0.08, cx+r*0.08, cy+r*0.08, fill=ORANGE_L, outline="", tags=("ultron_core","core_click"))
        for deg in range(0,360,30):
            rad=math.radians(deg)
            x1=cx+math.cos(rad)*r*0.52; y1=cy+math.sin(rad)*r*0.52
            x2=cx+math.cos(rad)*r*0.58; y2=cy+math.sin(rad)*r*0.58
            c.create_line(x1,y1,x2,y2,fill=ORANGE_D,width=1,tags=("ultron_core",))
        self.state_text=c.create_text(cx,cy+r*0.72,text="● IDLE  /  CLICK CORE",fill=TEXT_DIM,font=("Consolas",9),tags=("ultron_core",))
        c.create_oval(cx-r*0.52, cy-r*0.52, cx+r*0.52, cy+r*0.52, fill="", outline="", tags=("core_click",))
        c.tag_bind("core_click","<Button-1>",self._handle_click)
        c.tag_bind("core_click","<Enter>",self._handle_enter)
        c.tag_bind("core_click","<Leave>",self._handle_leave)
        self._apply_state_style()

    def _handle_click(self, _event=None):
        if callable(self.on_activate): self.on_activate()
    def _handle_enter(self, _event=None):
        self.canvas.configure(cursor="hand2")
        if self.state=="IDLE":
            self.canvas.itemconfig(self.inner_core, outline=TURQUOISE, width=2)
            self.canvas.itemconfig(self.state_text, fill=TURQUOISE)
    def _handle_leave(self, _event=None):
        self.canvas.configure(cursor="")
        self._apply_state_style()
    def set_state(self,state):
        state=str(state).upper().strip()
        if state not in {"IDLE","LISTENING","THINKING","SPEAKING"}: state="IDLE"
        self.state=state
        self.speed={
            "IDLE":list(self.base_speed),
            "LISTENING":[0.55,-0.36,0.66,-0.25,0.42],
            "THINKING":[1.20,-0.90,1.45,-0.72,1.00],
            "SPEAKING":[0.70,-0.45,0.82,-0.32,0.55],
        }[state]
        self._apply_state_style()
    def _apply_state_style(self):
        styles={
            "IDLE":(ORANGE,ORANGE_L,ORANGE_D,"● IDLE  /  CLICK CORE"),
            "LISTENING":(TURQUOISE,"#75fff7",TURQUOISE_D,"● LISTENING"),
            "THINKING":(ORANGE_L,"#ffd166",ORANGE,"● THINKING"),
            "SPEAKING":(GREEN,"#8cffbd",TURQUOISE,"● SPEAKING"),
        }
        primary,bright,dim,label=styles[self.state]
        self.canvas.itemconfig(self.outer_core,outline=dim)
        self.canvas.itemconfig(self.mid_core,outline=primary,fill=BG_PANEL2)
        self.canvas.itemconfig(self.inner_core,fill=primary,outline=bright,width=2 if self.state!="IDLE" else 1)
        self.canvas.itemconfig(self.center_core,fill=bright)
        self.canvas.itemconfig(self.state_text,text=label,fill=primary if self.state!="IDLE" else TEXT_DIM)
    def _animate_pulse(self):
        self.pulse_phase+=0.14
        amount={"IDLE":0.012,"LISTENING":0.055,"THINKING":0.025,"SPEAKING":0.075}[self.state]
        pulse=1.0+math.sin(self.pulse_phase)*amount
        cx,cy,r=self.cx,self.cy,self.base_r
        inner_r=r*0.18*pulse
        center_r=r*0.08*(1.0+math.sin(self.pulse_phase*1.35)*amount*1.6)
        self.canvas.coords(self.inner_core,cx-inner_r,cy-inner_r,cx+inner_r,cy+inner_r)
        self.canvas.coords(self.center_core,cx-center_r,cy-center_r,cx+center_r,cy+center_r)
    def animate(self):
        for i,ring_id in enumerate(self.rings):
            idx=i//2
            self.angle[idx]=(self.angle[idx]+self.speed[idx])%360
            start=self.angle[idx] if i%2==0 else (self.angle[idx]+180)%360
            extent=280 if i%2==0 else 90
            self.canvas.itemconfig(ring_id,start=start,extent=extent)
        self._animate_pulse()


class UltronGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ULTRON // CORE")
        self.root.configure(bg=BG)
        self.root.geometry("1400x900")
        self.root.minsize(1100, 720)

        self.font_title = tkfont.Font(family="Segoe UI", size=14, weight="bold")
        self.font_label = tkfont.Font(family="Segoe UI", size=10)
        self.font_small = tkfont.Font(family="Segoe UI", size=9)
        self.font_mono  = tkfont.Font(family="Consolas", size=9)

        # CONCIENCIA / IA
        self.ai_history = [
            {
                "role": "system",
                "content": (
                    "Eres ULTRON, la conciencia integrada de un panel Linux llamado "
                    "ULTRON CORE. Habla en español de forma natural, clara y concisa. "
                    "No digas que eres Groq ni que eres otro asistente. "
                    "Si no sabes algo, dilo. No inventes resultados del sistema."
                )
            }
        ]
        self.ai_busy = False
        self.consciousness_active = False
        self.tts_process = None
        self.voice_record_seconds = 12
        self.voice_silence_seconds = 0.9
        self.live_transcript_var = tk.StringVar(value="")
        self.audio_input_device = None
        self.audio_output_device = None
        self.ultron_volume = 70
        self.active_module_window = None
        self.active_module_key = None

        self._build_ui()
        self._start_animation()
        self._update_metrics()

    def _build_ui(self):
        main = tk.Frame(self.root, bg=BG)
        main.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        top = tk.Frame(main, bg=BG, height=42)
        top.pack(fill=tk.X, pady=(0, 8))
        top.pack_propagate(False)

        tk.Label(top, text="ULTRON // CORE", font=self.font_title,
                 fg=ORANGE, bg=BG).pack(side=tk.LEFT, padx=8)

        self.status_label = tk.Label(
            top, text="● SYSTEM ONLINE",
            font=self.font_small, fg=TURQUOISE, bg=BG
        )
        self.status_label.pack(side=tk.RIGHT, padx=12)

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

        bottom = tk.Frame(main, bg=BG, height=210)
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
            row = tk.Frame(parent, bg=BG_PANEL, height=36)
            row.pack(fill=tk.X, padx=8, pady=2)
            row.pack_propagate(False)
            tk.Label(row, text=label, font=self.font_small,
                     fg=TEXT_DIM, bg=BG_PANEL, anchor="w").pack(side=tk.LEFT, padx=6)
            tk.Label(row, text=value, font=self.font_small,
                     fg=color, bg=BG_PANEL, anchor="e").pack(side=tk.RIGHT, padx=6)

        tk.Frame(parent, bg=GRAY2, height=1).pack(fill=tk.X, padx=10, pady=10)

        tk.Frame(parent, bg=GRAY2, height=1).pack(fill=tk.X, padx=10, pady=8)

        # MODULES con scroll (para que quepan los 8)

        tk.Label(parent, text="MODULES", font=self.font_small,
                 fg=ORANGE, bg=BG_PANEL).pack(anchor="w", padx=14, pady=(0, 4))

        modules_container = tk.Frame(parent, bg=BG_PANEL, height=108)
        modules_container.pack(fill=tk.X, padx=4, pady=2)
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
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def _on_mousewheel(event):
            # Scroll solo cuando el cursor está sobre el panel de módulos.
            if getattr(event, "delta", 0):
                canvas.yview_scroll(int(-2 * (event.delta / 120)), "units")
            elif getattr(event, "num", None) == 4:
                canvas.yview_scroll(-2, "units")
            elif getattr(event, "num", None) == 5:
                canvas.yview_scroll(2, "units")

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
            ("04  RED // SEGURIDAD", self._on_network),
            ("05  ALMACENAMIENTO", self._on_files),
            ("06  HERRAMIENTAS", self._on_tools),
            ("07  DIAGNOSTICO", self._on_diagnostics),
            ("08  PAQUETES", self._on_packages),
            ("09  CHAT WIFI", self._on_chat),
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
                command=cmd, padx=12, pady=7, anchor="w"
            )
            btn.pack(fill=tk.X)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=GRAY, fg=ORANGE_L))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=BG_PANEL2, fg=ORANGE))

    def _build_right_panel(self, parent):
        header = tk.Frame(parent, bg=BG_PANEL2, height=36)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="THREAT LEVEL", font=self.font_small,
                 fg=ORANGE, bg=BG_PANEL2).pack(side=tk.LEFT, padx=12, pady=8)
        tk.Label(header, text="CONTROLLED", font=self.font_small,
                 fg=TURQUOISE, bg=BG_PANEL2).pack(side=tk.RIGHT, padx=12, pady=8)

        self.map_canvas = tk.Canvas(
            parent, bg="#080808", highlightthickness=0, height=280
        )
        self.map_canvas.pack(fill=tk.X, padx=8, pady=8)
        self.map_canvas.configure(cursor="hand2")
        self.map_canvas.bind("<Button-1>", lambda _e: self._on_ultron_eye())
        self.root.after(100, self._draw_map)

        live = tk.Frame(parent, bg=BG_PANEL)
        live.pack(fill=tk.X, padx=10, pady=4)
        tk.Label(live, text="● LIVE MONITORING", font=self.font_small,
                 fg=TURQUOISE, bg=BG_PANEL).pack(side=tk.LEFT)

        proto = tk.Frame(parent, bg=BG_PANEL)
        proto.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(proto, text="PROTOCOL STATUS", font=self.font_small,
                 fg=TEXT_DIM, bg=BG_PANEL).pack(anchor="w")

        status_row = tk.Frame(proto, bg=BG_PANEL)
        status_row.pack(fill=tk.X, pady=6)

        for name, color in [
            ("SHIELD", GREEN), ("LOCK", TURQUOISE),
            ("LINK", ORANGE), ("AUTH", GREEN), ("KEY", TURQUOISE)
        ]:
            lbl = tk.Label(
                status_row, text=name, font=self.font_small,
                fg=color, bg=BG_PANEL2, padx=8, pady=3
            )
            lbl.pack(side=tk.LEFT, padx=3)

    def _draw_map(self):
        c=self.map_canvas; c.delete("all"); c.update_idletasks()
        w=max(c.winfo_width(),300); h=max(c.winfo_height(),220)
        try:
            from PIL import Image, ImageTk, ImageColor, ImageDraw
            src=Image.open(os.path.join(os.path.dirname(os.path.dirname(__file__)),"assets","maps","worldmap.png")).convert("RGBA")
            # Recolor every visible map pixel to the current ULTRON secondary color.
            rgb=ImageColor.getrgb(TURQUOISE)
            # Hide political borders and render broad continent silhouettes only.
            alpha=src.getchannel("A")
            preview_w=320
            preview_h=max(1,int(alpha.height*(preview_w/alpha.width)))
            barrier=alpha.resize((preview_w,preview_h),Image.Resampling.LANCZOS)
            barrier=barrier.point(lambda a: 255 if a > 1 else 0)
            outside=barrier.copy()
            ImageDraw.floodfill(outside,(0,0),128,thresh=0)
            land=outside.point(lambda p: 0 if p == 128 else 255)
            fill_alpha=land.point(lambda a: 70 if a else 0)
            src=src.resize((preview_w,preview_h),Image.Resampling.LANCZOS)
            tinted=Image.new("RGBA",src.size,(rgb[0],rgb[1],rgb[2],0)); tinted.putalpha(fill_alpha)
            ratio=min((w-16)/tinted.width,(h-24)/tinted.height); size=(max(1,int(tinted.width*ratio)),max(1,int(tinted.height*ratio)))
            tinted=tinted.resize(size,Image.Resampling.LANCZOS)
            self._worldmap_photo=ImageTk.PhotoImage(tinted)
            c.create_image(w/2,(h-10)/2,image=self._worldmap_photo,anchor="center")
            # Approximate public-IP location marker (never GPS/precise).
            # Its color follows the current secondary theme color from Preferences.
            try:
                import json, urllib.request
                if not hasattr(self, "_map_ip_location"):
                    with urllib.request.urlopen("https://ipwho.is/", timeout=1.5) as r:
                        geo=json.loads(r.read().decode("utf-8"))
                    self._map_ip_location=(float(geo["longitude"]),float(geo["latitude"])) if geo.get("success", True) and geo.get("latitude") is not None else None
                map_w,map_h=size
                map_x=(w-map_w)/2; map_y=((h-10)-map_h)/2
                def map_xy(lon,lat):
                    return (map_x+((lon+180.0)/360.0)*map_w,
                            map_y+((90.0-lat)/180.0)*map_h)

                # Global ULTRON nodes. Thin theme-colored links stay behind markers.
                nodes=[(-74.0,40.71),(2.35,48.85),(37.62,55.75),
                       (139.69,35.68),(151.21,-33.87),(28.04,-26.20)]
                points=[map_xy(lon,lat) for lon,lat in nodes]
                if self._map_ip_location:
                    points.insert(0,map_xy(*self._map_ip_location))
                for a,b in zip(points,points[1:]):
                    c.create_line(a[0],a[1],b[0],b[1],fill=TURQUOISE_D,width=1)
                if len(points)>3:
                    c.create_line(points[0][0],points[0][1],points[3][0],points[3][1],fill=TURQUOISE_D,width=1)
                for nx,ny in points[1:]:
                    c.create_oval(nx-1.5,ny-1.5,nx+1.5,ny+1.5,outline=TURQUOISE,width=1)
                if self._map_ip_location:
                    x,y=points[0]; r=5
                    # Strong theme-colored location beacon: outer ring + solid core.
                    c.create_oval(x-r-2,y-r-2,x+r+2,y+r+2,outline=TURQUOISE,width=2)
                    c.create_oval(x-r,y-r,x+r,y+r,fill=TURQUOISE,outline=TEXT,width=1)
                    c.create_oval(x-1.5,y-1.5,x+1.5,y+1.5,fill=TEXT,outline="")
            except Exception:
                pass
        except Exception as exc:
            c.create_text(w/2,h/2,text=f"MAP OFFLINE\n{exc}",fill=TEXT_DIM,font=self.font_small,justify="center")
        # ULTRON EYE access: compact red HUD eye in the lower-right corner.
        ex,ey=w-30,h-18
        c.create_polygon(ex-23,ey,ex-13,ey-9,ex,ey-12,ex+13,ey-9,ex+23,ey,
                         ex+13,ey+9,ex,ey+12,ex-13,ey+9,
                         outline=ORANGE,fill="",width=1)
        c.create_oval(ex-9,ey-9,ex+9,ey+9,outline=ORANGE,width=1)
        c.create_oval(ex-4,ey-4,ex+4,ey+4,fill=ORANGE,outline=TEXT,width=1)
        c.create_oval(ex-1.5,ey-1.5,ex+1.5,ey+1.5,fill=TEXT,outline="")

    def _on_ultron_eye(self):
        self._add_log("ULTRON EYE selected")
        win=self._open_module_window("ULTRON_EYE","ULTRON EYE","960x660",(800,540))
        if win is None:return
        # ULTRON EYE gets almost the whole screen, but keeps a desktop margin.
        try:
            sw=self.root.winfo_screenwidth(); sh=self.root.winfo_screenheight()
            ww=max(900,min(1180,sw-70)); wh=max(620,min(740,sh-80))
            xx=max(0,(sw-ww)//2); yy=max(0,(sh-wh)//2)
            win.geometry(f"{ww}x{wh}+{xx}+{yy}")
        except Exception:
            pass
        win.configure(bg=BG)
        if not HAS_CTK:return

        shell=ctk.CTkFrame(win,fg_color=BG,corner_radius=0)
        shell.pack(fill="both",expand=True,padx=14,pady=12)

        head=ctk.CTkFrame(shell,fg_color="transparent")
        head.pack(fill="x",padx=6,pady=(0,8))
        ctk.CTkLabel(head,text="ULTRON EYE",text_color=ORANGE,font=("monospace",24,"bold")).pack(side="left")
        ctk.CTkLabel(head,text="TACTICAL GLOBAL VIEW",text_color=TEXT_DIM,font=("monospace",10)).pack(side="left",padx=12)
        status_var=tk.StringVar(value="GLOBAL LINK // INITIALIZING")
        ctk.CTkLabel(head,textvariable=status_var,text_color=TURQUOISE,font=("monospace",10,"bold")).pack(side="right")

        # Compact HUD eye: visual identity only; the tactical map is the main view.
        eye=tk.Canvas(shell,bg=BG,highlightthickness=0,height=72,cursor="hand2")
        eye.pack(fill="x",padx=6,pady=(0,7))
        def draw_eye(_e=None):
            eye.delete("all"); w=max(eye.winfo_width(),500); h=max(eye.winfo_height(),65); cy=h/2
            pts=[(w*.30,cy),(w*.40,cy-24),(w*.50,cy-30),(w*.60,cy-24),(w*.70,cy),
                 (w*.60,cy+24),(w*.50,cy+30),(w*.40,cy+24)]
            eye.create_polygon([v for pt in pts for v in pt],outline=ORANGE,fill="",width=2)
            for r in (21,14): eye.create_oval(w/2-r,cy-r,w/2+r,cy+r,outline=ORANGE,width=1)
            eye.create_oval(w/2-7,cy-7,w/2+7,cy+7,fill=ORANGE,outline=TEXT,width=1)
            eye.create_oval(w/2-2,cy-2,w/2+2,cy+2,fill=TEXT,outline="")
            eye.create_line(w*.18,cy,w*.34,cy,fill=ORANGE_D,width=1)
            eye.create_line(w*.66,cy,w*.82,cy,fill=ORANGE_D,width=1)
        eye.bind("<Configure>",draw_eye)
        # Same toggle behavior as the other modules: click the Eye again to close it.
        eye.bind("<Button-1>",lambda _e: win.destroy())
        win.after(60,draw_eye)

        controls=ctk.CTkFrame(shell,fg_color=BG_PANEL2,corner_radius=16)
        controls.pack(fill="x",padx=6,pady=(0,8))

        # Start with every heavy data layer OFF. Load each one only when requested.
        enabled={"AIR":False,"SEA":False,"CAM":False,"RADIO":False}
        layer_buttons={}
        selected={"kind":None}
        loaded_layers=set()
        loading_layers=set()

        body=ctk.CTkFrame(shell,fg_color="transparent")
        body.pack(fill="both",expand=True,padx=6,pady=(0,4))
        # Give the detail/camera side more breathing room.
        body.grid_columnconfigure(0,weight=5)
        body.grid_columnconfigure(1,weight=4)
        body.grid_rowconfigure(0,weight=1)

        map_card=ctk.CTkFrame(body,fg_color=BG_PANEL2,border_color=ORANGE,border_width=1,corner_radius=20)
        map_card.grid(row=0,column=0,sticky="nsew",padx=(0,6))
        map_head=ctk.CTkFrame(map_card,fg_color="transparent")
        map_head.pack(fill="x",padx=16,pady=(12,4))
        ctk.CTkLabel(map_head,text="GLOBAL GRID",text_color=ORANGE,font=("monospace",13,"bold")).pack(side="left")
        map_info=tk.StringVar(value="AIR 0  |  SEA 0  |  CAM 0  |  RADIO 0")
        ctk.CTkLabel(map_head,textvariable=map_info,text_color=TEXT_DIM,font=("monospace",9)).pack(side="right")
        map_view={"zoom":1.0,"cx":0.5,"cy":0.5,"mode":"select","drag":None}
        map_tools=ctk.CTkFrame(map_head,fg_color="transparent")
        map_tools.pack(side="right",padx=(0,10))
        zoom_btn=ctk.CTkButton(map_tools,text="🔍",width=34,height=28,corner_radius=8,
                               fg_color=BG_PANEL,hover_color=BG_PANEL2,border_color=ORANGE,
                               border_width=1,text_color=ORANGE,font=("sans-serif",13),
                               command=lambda:set_map_mode("zoom"))
        zoom_btn.pack(side="left",padx=3)
        pan_btn=ctk.CTkButton(map_tools,text="✋",width=34,height=28,corner_radius=8,
                              fg_color=BG_PANEL,hover_color=BG_PANEL2,border_color=TURQUOISE,
                              border_width=1,text_color=TURQUOISE,font=("sans-serif",13),
                              command=lambda:set_map_mode("pan"))
        pan_btn.pack(side="left",padx=3)
        globe=tk.Canvas(map_card,bg=BG_PANEL,highlightthickness=0,cursor="crosshair")
        globe.pack(fill="both",expand=True,padx=10,pady=(4,10))

        panel=ctk.CTkFrame(body,fg_color=BG_PANEL2,border_color=ORANGE_D,border_width=1,corner_radius=20)
        panel.grid(row=0,column=1,sticky="nsew",padx=(6,0))
        panel_title=tk.StringVar(value="LAYERS // STANDBY")
        ctk.CTkLabel(panel,textvariable=panel_title,text_color=ORANGE,font=("monospace",13,"bold")).pack(anchor="w",padx=16,pady=(14,5))
        detail=tk.StringVar(value="All layers are OFF to save RAM/CPU. Select AIR, SEA, CAM or RADIO.")
        ctk.CTkLabel(panel,textvariable=detail,text_color=TEXT_DIM,font=("monospace",9),justify="left",wraplength=360).pack(anchor="w",padx=16,pady=(0,8))

        sea_loading=ctk.CTkFrame(panel,fg_color=BG_PANEL,corner_radius=12)
        sea_loading_text=tk.StringVar(value="SEA // SCANNING AIS...")
        ctk.CTkLabel(sea_loading,textvariable=sea_loading_text,text_color="#0b4f9c",
                     font=("monospace",8,"bold")).pack(anchor="w",padx=10,pady=(7,4))
        sea_progress=ctk.CTkProgressBar(sea_loading,mode="indeterminate",height=8,corner_radius=6,
                                        progress_color="#0b4f9c",fg_color=BG_PANEL2)
        sea_progress.pack(fill="x",padx=10,pady=(0,8))

        air_tools=ctk.CTkFrame(panel,fg_color=BG_PANEL,corner_radius=12)
        air_refresh_status=tk.StringVar(value="AUTO REFRESH // 30 S")
        ctk.CTkLabel(air_tools,textvariable=air_refresh_status,text_color="#ff7a00",
                     font=("monospace",8,"bold")).pack(side="left",padx=10,pady=7)
        air_refresh_btn=ctk.CTkButton(air_tools,text="REFRESH",width=82,height=28,
                                      fg_color="#ff7a00",hover_color="#c45f00",
                                      text_color=BG,corner_radius=9,font=("monospace",8,"bold"))
        air_refresh_btn.pack(side="right",padx=8,pady=7)

        # Camera finder: fast local filtering over the global public-camera cache.
        cam_filterbar=ctk.CTkFrame(panel,fg_color=BG_PANEL,corner_radius=12)
        cam_search_var=tk.StringVar(value="")
        cam_country_var=tk.StringVar(value="TODOS")
        cam_search=ctk.CTkEntry(cam_filterbar,textvariable=cam_search_var,
                                placeholder_text="SEARCH // PAÍS · CIUDAD · CÁMARA",
                                height=30,corner_radius=9,border_color="#ff3333",
                                fg_color=BG_PANEL2,text_color=TEXT,font=("monospace",9))
        cam_search.pack(side="left",fill="x",expand=True,padx=(8,5),pady=7)
        cam_country_menu=ctk.CTkOptionMenu(cam_filterbar,variable=cam_country_var,values=["TODOS"],
                                           width=118,height=30,corner_radius=9,
                                           fg_color="#ff3333",button_color="#b51f1f",
                                           button_hover_color="#8f1818",text_color=TEXT,
                                           font=("monospace",8,"bold"))
        cam_country_menu.pack(side="right",padx=(5,8),pady=7)

        cam_preview=ctk.CTkFrame(panel,fg_color=BG_PANEL,border_color="#ff3333",border_width=1,corner_radius=12)
        cam_preview_title=tk.StringVar(value="CAM // PREVIEW")
        ctk.CTkLabel(cam_preview,textvariable=cam_preview_title,text_color="#ff3333",font=("monospace",9,"bold")).pack(anchor="w",padx=10,pady=(8,4))
        cam_image=tk.Label(cam_preview,text="SELECT A CAMERA",fg=TEXT_DIM,bg=BG_PANEL,font=("monospace",9),bd=0)
        cam_image.pack(fill="both",expand=True,padx=10,pady=(2,8))
        cam_actions=ctk.CTkFrame(cam_preview,fg_color="transparent")
        cam_actions.pack(fill="x",padx=10,pady=(0,10))

        list_frame=ctk.CTkScrollableFrame(panel,fg_color=BG_PANEL,corner_radius=12)
        list_frame.pack(fill="both",expand=True,padx=12,pady=(0,12))

        self._eye_data={"AIR":[],"SEA":[],"CAM":[],"RADIO":[]}
        self._eye_marker_hits=[]
        self._eye_radio_process=getattr(self,"_eye_radio_process",None)
        self._eye_cam_filtered=[]
        selected_cam={"item":None,"token":0}
        selected_air={"item":None}
        selected_marker={"AIR":None,"SEA":None,"CAM":None,"RADIO":None}

        def format_air_info(air,route=None):
            callsign=air.get("callsign") or "UNKNOWN"
            alt=air.get("alt")
            speed=air.get("speed")
            heading=air.get("heading")
            vr=air.get("vertical_rate")
            lines=[f"AIR // {callsign}",
                   f"ALT // {alt:.0f} m" if isinstance(alt,(int,float)) else "ALT // N/A",
                   f"SPEED // {speed*3.6:.0f} km/h" if isinstance(speed,(int,float)) else "SPEED // N/A",
                   f"HEADING // {heading:.0f}°" if isinstance(heading,(int,float)) else "HEADING // N/A",
                   f"V/S // {vr:.1f} m/s" if isinstance(vr,(int,float)) else "V/S // N/A"]
            if route:
                origin=route.get("origin") or {}
                dest=route.get("destination") or {}
                ocode=origin.get("iata_code") or origin.get("icao_code") or "?"
                dcode=dest.get("iata_code") or dest.get("icao_code") or "?"
                oname=origin.get("municipality") or origin.get("name") or ""
                dname=dest.get("municipality") or dest.get("name") or ""
                lines += [f"FROM // {ocode} {oname}".strip(),
                          f"TO // {dcode} {dname}".strip()]
                try:
                    lat1=math.radians(float(air.get("lat"))); lon1=math.radians(float(air.get("lon")))
                    lat2=math.radians(float(dest.get("latitude"))); lon2=math.radians(float(dest.get("longitude")))
                    a=math.sin((lat2-lat1)/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
                    km=6371.0*2*math.asin(math.sqrt(a))
                    if isinstance(speed,(int,float)) and speed>30:
                        mins=int((km/(speed*3.6))*60)
                        lines.append(f"ETA EST. // {mins//60}h {mins%60:02d}m")
                        lines.append(f"REMAINING // {km:.0f} km")
                except Exception:
                    pass
            else:
                lines += ["FROM // LOOKING UP...", "TO // LOOKING UP..."]
            return "\n".join(lines)

        def select_aircraft(air):
            selected_air["item"]=air
            selected_marker["AIR"]=air
            detail.set(format_air_info(air))
            draw_tactical()
            callsign=(air.get("callsign") or "").strip()
            if not callsign or callsign=="UNKNOWN":
                return
            def route_worker():
                route=None
                try:
                    url="https://api.adsbdb.com/v0/callsign/"+urllib.parse.quote(callsign,safe="")
                    req=urllib.request.Request(url,headers={"User-Agent":"UltronEye/1.0"})
                    with urllib.request.urlopen(req,timeout=6) as r:
                        data=json.loads(r.read().decode())
                    route=((data.get("response") or {}).get("flightroute"))
                except Exception:
                    route=None
                def show():
                    if selected_air.get("item") is not air:
                        return
                    if route:
                        detail.set(format_air_info(air,route))
                    else:
                        detail.set(format_air_info(air).replace("FROM // LOOKING UP...\nTO // LOOKING UP...",
                                                               "ROUTE // NOT AVAILABLE"))
                win.after(0,show)
            threading.Thread(target=route_worker,daemon=True).start()

        country_names={
            "MX":"MÉXICO","US":"USA","CA":"CANADÁ","GB":"REINO UNIDO","FI":"FINLANDIA",
            "NZ":"NUEVA ZELANDA","EE":"ESTONIA","IS":"ISLANDIA","RS":"SERBIA",
            "PR":"PUERTO RICO","BA":"BOSNIA","BR":"BRASIL",
        }

        def show_camera_preview(cam):
            if not cam or not cam.get("image_url"):
                detail.set("CAM // VIEW UNAVAILABLE")
                return
            selected_cam["item"]=cam
            selected_cam["token"]+=1
            token=selected_cam["token"]
            # CAMERA VIEW mode: give the image the whole right-side content area.
            cam_filterbar.pack_forget()
            list_frame.pack_forget()
            cam_preview.pack_forget()
            cam_preview.pack(fill="both",expand=True,padx=12,pady=(0,12))
            cam_preview_title.set("CAM // "+short_text(cam.get("title") or "PUBLIC CAMERA",34))
            cam_image.configure(image="",text="LOADING PUBLIC CAMERA...",fg=TEXT_DIM)
            def worker():
                try:
                    url=cam.get("image_url")
                    sep="&" if "?" in url else "?"
                    req=urllib.request.Request(url+sep+"_ultron="+str(int(time.time())),headers={"User-Agent":"UltronEye/1.0"})
                    with urllib.request.urlopen(req,timeout=12) as r: raw=r.read()
                    from PIL import Image,ImageTk
                    im=Image.open(io.BytesIO(raw)).convert("RGB")
                    # Fixed viewing stage: panoramas stay visible instead of looking like a thin strip.
                    stage_w,stage_h=460,260
                    im.thumbnail((stage_w-12,stage_h-12),Image.Resampling.LANCZOS)
                    stage=Image.new("RGB",(stage_w,stage_h),(7,7,7))
                    stage.paste(im,((stage_w-im.width)//2,(stage_h-im.height)//2))
                    def done():
                        if token!=selected_cam["token"]: return
                        photo=ImageTk.PhotoImage(stage)
                        self._eye_cam_photo=photo
                        cam_image.configure(image=photo,text="")
                        if cam.get("static_preview"):
                            mode="STATIC PREVIEW // PRESS OPEN LIVE"
                            detail.set(f"CAM // {mode}\n{cam.get('airport') or cam.get('region') or 'PUBLIC SOURCE'}")
                        else:
                            mode="SNAPSHOT // AUTO REFRESH"
                            detail.set(f"CAM // {mode}\n{cam.get('airport') or cam.get('region') or 'PUBLIC SOURCE'}")
                            delay=max(30,int(cam.get("refresh_seconds") or 60))*1000
                            if win.winfo_exists():
                                win.after(delay,lambda: show_camera_preview(cam) if selected_cam.get("item") is cam else None)
                    win.after(0,done)
                except Exception as exc:
                    win.after(0,lambda: cam_image.configure(image="",text="CAMERA OFFLINE / UNAVAILABLE",fg=TEXT_DIM))
            threading.Thread(target=worker,daemon=True).start()

        def open_camera_live_for(cam):
            url=(cam or {}).get("live_url")
            if not url:
                detail.set("CAM // THIS SOURCE PROVIDES SNAPSHOTS, NOT CONTINUOUS VIDEO")
                return
            selected_cam["item"]=cam
            try:
                browser=shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")
                if browser:
                    subprocess.Popen([browser,"--app="+url,"--start-maximized"],
                                     stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                else:
                    import webbrowser; webbrowser.open(url)
                detail.set("CAM // OPENING OFFICIAL LIVE VIDEO")
            except Exception as exc:
                detail.set(f"CAM // LIVE PLAYER ERROR\n{exc}")

        def open_camera_live():
            cam=selected_cam.get("item")
            url=(cam or {}).get("live_url")
            if not url:
                detail.set("CAM // THIS SOURCE PROVIDES SNAPSHOTS, NOT CONTINUOUS VIDEO")
                return
            try:
                browser=shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")
                if browser:
                    subprocess.Popen([browser,"--app="+url,"--start-maximized"],
                                     stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                else:
                    import webbrowser; webbrowser.open(url)
                detail.set("CAM // OPENING OFFICIAL LIVE VIDEO")
            except Exception as exc:
                detail.set(f"CAM // LIVE PLAYER ERROR\n{exc}")

        def close_camera_preview():
            selected_cam["item"]=None
            selected_cam["token"]+=1
            cam_preview.pack_forget()
            cam_filterbar.pack(fill="x",padx=12,pady=(0,8))
            list_frame.pack(fill="both",expand=True,padx=12,pady=(0,12))
            detail.set("CAM // SELECT A PUBLIC CAMERA")

        ctk.CTkButton(cam_actions,text="BACK",height=28,width=72,command=close_camera_preview,
                      fg_color=BG_PANEL2,hover_color=GRAY,border_color="#ff3333",border_width=1,
                      text_color=TEXT,corner_radius=8,font=("monospace",8,"bold")).pack(side="left")
        ctk.CTkButton(cam_actions,text="OPEN LIVE",height=28,width=96,command=open_camera_live,
                      fg_color="#ff3333",hover_color="#b51f1f",text_color=TEXT,corner_radius=8,
                      font=("monospace",8,"bold")).pack(side="left",padx=(7,0))
        ctk.CTkButton(cam_actions,text="REFRESH",height=28,width=82,command=lambda: show_camera_preview(selected_cam.get("item")),
                      fg_color=BG_PANEL2,hover_color=GRAY,border_color="#ff3333",border_width=1,
                      text_color=TEXT,corner_radius=8,font=("monospace",8,"bold")).pack(side="right")

        def stop_radio():
            proc=getattr(self,"_eye_radio_process",None)
            if proc and proc.poll() is None:
                try: proc.terminate()
                except Exception: pass
            self._eye_radio_process=None

        def play_radio(st):
            url=st.get("url_resolved") or st.get("url")
            player=shutil.which("ffplay") or shutil.which("mpv") or shutil.which("vlc")
            if not (url and player):
                detail.set("RADIO // No compatible stream/player available.")
                return
            stop_radio()
            args=[player,"-nodisp","-autoexit","-loglevel","quiet",url] if player.endswith("ffplay") else [player,url]
            self._eye_radio_process=subprocess.Popen(args,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            detail.set(f"RADIO // PLAYING\n{st.get('country') or 'UNKNOWN'} // {st.get('name') or 'UNKNOWN'}")

        def clear_list():
            for child in list_frame.winfo_children(): child.destroy()

        def short_text(text,max_len):
            text=str(text or "").strip()
            return text if len(text)<=max_len else text[:max_len-1]+"…"

        def short_country(country):
            country=(country or "UNKNOWN").strip()
            aliases={
                "The United States Of America":"USA","United States of America":"USA","United States":"USA",
                "United Kingdom":"UK","Russian Federation":"RUSSIA","Czech Republic":"CZECHIA",
                "United Arab Emirates":"UAE","Korea, Republic of":"S. KOREA"
            }
            return aliases.get(country,short_text(country,10))

        def apply_cam_filter(_event=None):
            all_cams=self._eye_data.get("CAM",[])
            q=cam_search_var.get().strip().lower()
            chosen=cam_country_var.get().strip()
            filtered=[]
            for cam in all_cams:
                cname=cam.get("country_name") or country_names.get(cam.get("country_code"),cam.get("country_code") or "")
                if chosen!="TODOS" and cname!=chosen:
                    continue
                hay=" ".join(str(cam.get(k) or "") for k in ("title","country_name","country_code","region","source","airport")).lower()
                # Spanish aliases make searches such as "estados unidos" useful too.
                if q and q not in hay:
                    aliases={"estados unidos":"USA","méxico":"MX","mexico":"MX","reino unido":"GB",
                             "canadá":"CA","canada":"CA","nueva zelanda":"NZ","finlandia":"FI",
                             "islandia":"IS","serbia":"RS","puerto rico":"PR","bosnia":"BA","brasil":"BR"}
                    code=aliases.get(q)
                    if not code or cam.get("country_code")!=code:
                        continue
                filtered.append(cam)
            self._eye_cam_filtered=filtered
            if selected.get("kind")=="CAM":
                render_list("CAM")
                draw_tactical()

        cam_search.bind("<KeyRelease>",apply_cam_filter)
        cam_country_menu.configure(command=lambda _choice:apply_cam_filter())

        def render_list(kind):
            selected["kind"]=kind
            if kind=="AIR":
                cam_filterbar.pack_forget()
                cam_preview.pack_forget()
                if not air_tools.winfo_manager():
                    try: air_tools.pack(fill="x",padx=12,pady=(0,8),before=list_frame)
                    except Exception: air_tools.pack(fill="x",padx=12,pady=(0,8))
                data=self._eye_data.get("AIR",[])
                panel_title.set("AIR // LIVE" if data else "AIR // WAITING")
                if not list_frame.winfo_manager():
                    list_frame.pack(fill="both",expand=True,padx=12,pady=(0,12))
            elif kind=="CAM":
                air_tools.pack_forget()
                data=self._eye_cam_filtered
                panel_title.set(f"CAM // {len(data)} / {len(self._eye_data.get('CAM',[]))}")
                if selected_cam.get("item") is None:
                    cam_preview.pack_forget()
                    if not cam_filterbar.winfo_manager():
                        try: cam_filterbar.pack(fill="x",padx=12,pady=(0,8),before=list_frame)
                        except Exception: cam_filterbar.pack(fill="x",padx=12,pady=(0,8))
                    if not list_frame.winfo_manager():
                        list_frame.pack(fill="both",expand=True,padx=12,pady=(0,12))
            else:
                air_tools.pack_forget()
                cam_filterbar.pack_forget()
                cam_preview.pack_forget()
                data=self._eye_data.get(kind,[])
                panel_title.set(kind+" // "+("LIVE" if data else "WAITING"))
                if not list_frame.winfo_manager():
                    list_frame.pack(fill="both",expand=True,padx=12,pady=(0,12))
            clear_list()
            if not data:
                ctk.CTkLabel(list_frame,text="NO DATA YET",text_color=TEXT_DIM,font=("monospace",10)).pack(pady=18)
                return
            for item in data[:60]:
                row=ctk.CTkFrame(list_frame,fg_color=BG_PANEL2,corner_radius=11)
                row.pack(fill="x",padx=4,pady=4)
                if kind=="RADIO":
                    row.grid_columnconfigure(1,weight=1)
                    ctk.CTkButton(row,text="PLAY",width=50,height=27,command=lambda st=item:play_radio(st),
                                  fg_color=ORANGE,hover_color=ORANGE_D,text_color=BG,corner_radius=9,
                                  font=("monospace",8,"bold")).grid(row=0,column=0,padx=(6,4),pady=5)
                    country=short_country(item.get("country"))
                    station=short_text(item.get("name") or "UNKNOWN",20)
                    name=f"{country} // {station}"
                    ctk.CTkLabel(row,text=name,width=145,text_color=TEXT,font=("monospace",8),
                                 anchor="w").grid(row=0,column=1,sticky="ew",padx=3,pady=5)
                    ctk.CTkButton(row,text="STOP",width=50,height=27,command=stop_radio,fg_color=RED,hover_color="#b51f1f",
                                  text_color=TEXT,corner_radius=9,font=("monospace",8,"bold")).grid(row=0,column=2,padx=(4,6),pady=5)
                else:
                    if kind=="AIR":
                        txt=f"{item.get('callsign') or 'UNKNOWN'}\nALT {item.get('alt','-')} m"
                        air_label=ctk.CTkLabel(row,text=txt,text_color=TEXT,font=("monospace",9),justify="left",
                                               anchor="w",cursor="hand2")
                        air_label.pack(fill="x",padx=9,pady=7)
                        def select_air(_e=None,air=item):
                            select_aircraft(air)
                        row.bind("<Button-1>",select_air)
                        air_label.bind("<Button-1>",select_air)
                    elif kind=="SEA":
                        txt=f"{item.get('name') or 'VESSEL'}\nMMSI {item.get('mmsi','-')}"
                        ctk.CTkLabel(row,text=txt,text_color=TEXT,font=("monospace",9),justify="left",anchor="w").pack(fill="x",padx=9,pady=7)
                    else:
                        # LIVE only when this source is truly continuous/live.
                        is_live=bool(item.get("live_url")) and not item.get("static_preview",False)
                        cam_btn_text="LIVE" if is_live else "VIEW"
                        cam_btn_color="#ff3333" if is_live else "#ff7a00"
                        cam_hover="#b51f1f" if is_live else "#c45f00"
                        cam_cmd=(lambda cam=item: open_camera_live_for(cam)) if is_live else (lambda cam=item: show_camera_preview(cam))
                        ctk.CTkButton(row,text=cam_btn_text,width=52,height=27,command=cam_cmd,
                                      fg_color=cam_btn_color,hover_color=cam_hover,text_color=TEXT,corner_radius=8,
                                      font=("monospace",8,"bold")).pack(side="left",padx=(6,5),pady=5)
                        if item.get("local_city"):
                            txt="IRAPUATO // "+short_text(item.get("title") or "CAMERA",19)
                            txt_color="#ff6666"
                        else:
                            country=item.get("country_name") or item.get("country_code") or "GLOBAL"
                            region=short_text(item.get("region") or "",10)
                            prefix=country+((" · "+region) if region else "")
                            txt=short_text(prefix+" // "+(item.get("title") or "CAMERA"),31)
                            txt_color=TEXT
                        ctk.CTkLabel(row,text=txt,text_color=txt_color,font=("monospace",8,"bold" if item.get("local_city") else "normal"),
                                     anchor="w").pack(side="left",fill="x",expand=True,padx=(2,6),pady=5)

        def normalize_geo(lat,lon):
            """Return validated (lat, lon) floats or None."""
            try:
                lat=float(lat); lon=float(lon)
                if not math.isfinite(lat) or not math.isfinite(lon):
                    return None
                if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
                    return None
                return lat,lon
            except Exception:
                return None

        def is_ocean_geo(lat,lon):
            """True when the equirectangular land mask says this point is water."""
            try:
                from PIL import Image
                if not hasattr(self,"_eye_landmask_img"):
                    mp=os.path.join(os.path.dirname(os.path.dirname(__file__)),"assets","maps","worldmap_equirectangular.png")
                    self._eye_landmask_img=Image.open(mp).convert("RGBA")
                im=self._eye_landmask_img
                x=int(round(((float(lon)+180.0)/360.0)*(im.width-1)))
                y=int(round(((90.0-float(lat))/180.0)*(im.height-1)))
                x=max(0,min(im.width-1,x)); y=max(0,min(im.height-1,y))
                # Anti-alias tolerance: if any nearby pixel is water, keep coastal vessels.
                for dy in (-2,-1,0,1,2):
                    for dx in (-2,-1,0,1,2):
                        xx=max(0,min(im.width-1,x+dx)); yy=max(0,min(im.height-1,y+dy))
                        if im.getpixel((xx,yy))[3] < 40:
                            return True
                return False
            except Exception:
                return True

        def map_rect(w,h):
            pad=12
            aspect=2.0
            avail_w=max(1,w-pad*2); avail_h=max(1,h-pad*2)
            draw_w=min(avail_w,avail_h*aspect)
            draw_h=draw_w/aspect
            if draw_h>avail_h:
                draw_h=avail_h; draw_w=draw_h*aspect
            return (w-draw_w)/2.0,(h-draw_h)/2.0,draw_w,draw_h

        def clamp_map_view():
            z=max(1.0,min(10.0,float(map_view.get("zoom",1.0))))
            map_view["zoom"]=z
            half=0.5/z
            map_view["cx"]=max(half,min(1.0-half,float(map_view.get("cx",0.5))))
            map_view["cy"]=max(half,min(1.0-half,float(map_view.get("cy",0.5))))

        def map_xy(lon,lat,w,h):
            x0,y0,draw_w,draw_h=map_rect(w,h)
            z=map_view["zoom"]; cx=map_view["cx"]; cy=map_view["cy"]
            u=(float(lon)+180.0)/360.0
            v=(90.0-float(lat))/180.0
            return (x0+((u-cx)*z+0.5)*draw_w,
                    y0+((v-cy)*z+0.5)*draw_h)

        def canvas_to_map_uv(x,y,w,h):
            x0,y0,draw_w,draw_h=map_rect(w,h)
            z=map_view["zoom"]; cx=map_view["cx"]; cy=map_view["cy"]
            u=cx+(((x-x0)/draw_w)-0.5)/z
            v=cy+(((y-y0)/draw_h)-0.5)/z
            return u,v

        def set_map_mode(mode):
            current=map_view.get("mode","select")
            map_view["mode"]="select" if current==mode else mode
            active=map_view["mode"]
            zoom_btn.configure(fg_color=ORANGE if active=="zoom" else BG_PANEL,
                               text_color=BG if active=="zoom" else ORANGE)
            pan_btn.configure(fg_color=TURQUOISE if active=="pan" else BG_PANEL,
                              text_color=BG if active=="pan" else TURQUOISE)
            globe.configure(cursor="fleur" if active=="pan" else ("tcross" if active=="zoom" else "crosshair"))

        def zoom_map_at(x,y,factor):
            w=max(globe.winfo_width(),420); h=max(globe.winfo_height(),300)
            u,v=canvas_to_map_uv(x,y,w,h)
            old_z=map_view["zoom"]
            new_z=max(1.0,min(10.0,old_z*factor))
            if abs(new_z-old_z)<1e-6: return
            map_view["cx"]=u
            map_view["cy"]=v
            map_view["zoom"]=new_z
            clamp_map_view()
            draw_tactical()

        def reset_map_view():
            map_view.update({"zoom":1.0,"cx":0.5,"cy":0.5,"drag":None})
            draw_tactical()

        def draw_tactical(_e=None):
            globe.delete("all")
            globe.update_idletasks()
            w=max(globe.winfo_width(),420); h=max(globe.winfo_height(),300)
            # Grid
            for lon in range(-180,181,30):
                x,_=map_xy(lon,0,w,h); globe.create_line(x,10,x,h-10,fill=BG_PANEL2,width=1)
            for lat in range(-60,61,30):
                _,y=map_xy(0,lat,w,h); globe.create_line(10,y,w-10,y,fill=BG_PANEL2,width=1)
            # Continent silhouette using the same approved map asset.
            try:
                from PIL import Image,ImageTk,ImageColor,ImageDraw
                map_dir=os.path.join(os.path.dirname(os.path.dirname(__file__)),"assets","maps")
                eq_path=os.path.join(map_dir,"worldmap_equirectangular.png")
                fallback_path=os.path.join(map_dir,"worldmap.png")
                src_path=eq_path if os.path.exists(eq_path) else fallback_path
                if getattr(self,"_eye_map_src_path",None)!=src_path or not hasattr(self,"_eye_map_src"):
                    self._eye_map_src=Image.open(src_path).convert("RGBA")
                    self._eye_map_src_path=src_path
                src=self._eye_map_src
                rgb=ImageColor.getrgb(TURQUOISE)
                clamp_map_view()
                z=map_view["zoom"]; cx=map_view["cx"]; cy=map_view["cy"]
                half=0.5/z
                left=int(max(0,(cx-half)*src.width)); right=int(min(src.width,(cx+half)*src.width))
                top=int(max(0,(cy-half)*src.height)); bottom=int(min(src.height,(cy+half)*src.height))
                crop=src.crop((left,top,right,bottom))
                x0,y0,draw_w,draw_h=map_rect(w,h)
                sz=(max(1,int(draw_w)),max(1,int(draw_h)))
                alpha=crop.getchannel("A").resize(sz,Image.Resampling.LANCZOS)
                fill=alpha.point(lambda a:min(58,a) if a>6 else 0)
                tinted=Image.new("RGBA",sz,(rgb[0],rgb[1],rgb[2],0)); tinted.putalpha(fill)
                self._eye_world_photo=ImageTk.PhotoImage(tinted)
                globe.create_image(x0+draw_w/2,y0+draw_h/2,image=self._eye_world_photo,anchor="center")
            except Exception: pass

            self._eye_marker_hits=[]
            # Permanent ULTRON EYE layer colors (do not follow theme preferences).
            specs={
                "AIR":("#ff7a00","A"),      # normal orange
                "SEA":("#0b4f9c","S"),      # normal marine blue
                "CAM":("#ff3333","C"),      # normal red
                "RADIO":("#00d66b","R"),    # normal green
            }
            selected_colors={
                "AIR":"#ffd400",             # selected yellow
                "SEA":"#1688ff",             # selected strong blue
                "CAM":"#ff1010",             # selected strong red
                "RADIO":"#00ff66",           # selected strong green
            }
            counts={}
            for kind in ("AIR","SEA","CAM","RADIO"):
                data=self._eye_cam_filtered if kind=="CAM" else self._eye_data.get(kind,[])
                counts[kind]=len(data)
                if not enabled.get(kind): continue
                color,letter=specs[kind]
                if kind=="CAM" and len(data)>420:
                    step=max(1,len(data)//420)
                    plot_data=data[::step][:420]
                else:
                    plot_data=data[:220]
                for item in plot_data:
                    pos=normalize_geo(item.get("lat"),item.get("lon"))
                    if not pos: continue
                    lat,lon=pos
                    try: x,y=map_xy(lon,lat,w,h)
                    except Exception: continue

                    is_selected=(selected_marker.get(kind) is item)
                    marker_color=selected_colors[kind] if is_selected else color
                    # Only the selected marker gets a targeting circle.
                    if is_selected:
                        ring_r=11
                        globe.create_oval(x-ring_r,y-ring_r,x+ring_r,y+ring_r,
                                          outline=marker_color,width=2)
                        globe.create_oval(x-ring_r-3,y-ring_r-3,x+ring_r+3,y+ring_r+3,
                                          outline="#ffffff",width=1)

                    if kind=="AIR":
                        # Directional aircraft marker.
                        scale=1.0 if not is_selected else 1.35
                        ang=math.radians(float(item.get("heading") or 0)-90)
                        ux,uy=math.cos(ang),math.sin(ang)
                        px,py=-uy,ux
                        tip=(x+ux*5.5*scale,y+uy*5.5*scale)
                        left=(x-ux*2.5*scale+px*2.5*scale,y-uy*2.5*scale+py*2.5*scale)
                        tail=(x-ux*1.0*scale,y-uy*1.0*scale)
                        right=(x-ux*2.5*scale-px*2.5*scale,y-uy*2.5*scale-py*2.5*scale)
                        fill=marker_color
                        globe.create_polygon(tip,left,tail,right,fill=fill,
                                             outline="#ffffff" if is_selected else "",width=1)

                    elif kind=="SEA":
                        # Tiny vessel silhouette.
                        scale=1.25 if is_selected else 1.0
                        globe.create_polygon(x-4*scale,y+2*scale,x+4*scale,y+2*scale,
                                             x+2.5*scale,y-2*scale,x-2.5*scale,y-2*scale,
                                             fill=marker_color,outline="#ffffff" if is_selected else "")
                        globe.create_line(x,y-2*scale,x,y-4.5*scale,fill=marker_color,width=2 if is_selected else 1)

                    elif kind=="CAM":
                        r=3.0 if is_selected else 2.2
                        globe.create_oval(x-r,y-r,x+r,y+r,fill=marker_color,
                                          outline="#ffffff" if is_selected else "",width=1)

                    else:
                        # Radio link/hotspot glyph.
                        scale=1.25 if is_selected else 1.0
                        globe.create_oval(x-5*scale,y-3*scale,x+1*scale,y+3*scale,outline=marker_color,width=2 if is_selected else 1)
                        globe.create_oval(x-1*scale,y-3*scale,x+5*scale,y+3*scale,outline=marker_color,width=2 if is_selected else 1)
                        globe.create_line(x-1.5*scale,y,x+1.5*scale,y,fill=marker_color,width=2 if is_selected else 1)

                    self._eye_marker_hits.append((x,y,kind,item))

            map_info.set(f"AIR {counts.get('AIR',0)}  |  SEA {counts.get('SEA',0)}  |  CAM {counts.get('CAM',0)}  |  RADIO {counts.get('RADIO',0)}")
            globe.create_text(12,h-10,text="LIGHTWEIGHT GLOBAL // GPU SAFE",anchor="sw",fill=TEXT_DIM,font=("monospace",8))
            globe.create_text(w-12,h-10,text="CLICK MARKER FOR DETAILS",anchor="se",fill=TEXT_DIM,font=("monospace",8))

        self._eye_redraw_theme=lambda: (draw_eye(),draw_tactical())

        def marker_click(event):
            best=None; dist=999
            for x,y,kind,item in self._eye_marker_hits:
                d=(x-event.x)**2+(y-event.y)**2
                if d<dist and d<100: best=(kind,item); dist=d
            if not best:return
            kind,item=best
            selected_marker[kind]=item
            if kind=="AIR":
                selected_air["item"]=item
                select_aircraft(item)
            elif kind=="SEA":
                detail.set(f"SEA // {item.get('name') or 'VESSEL'}\nMMSI {item.get('mmsi','-')}\n{item.get('lat',0):.3f}, {item.get('lon',0):.3f}")
                draw_tactical()
            elif kind=="CAM":
                place=item.get("region") or item.get("airport") or item.get("country_name") or item.get("kind") or "PUBLIC"
                detail.set(f"CAM // {item.get('title') or 'CAMERA'}\n{place}\nSOURCE: {item.get('source') or item.get('kind') or 'PUBLIC'}")
                draw_tactical()
                render_list(kind)
                show_camera_preview(item)
                return
            else:
                detail.set(f"RADIO // {item.get('country') or 'UNKNOWN'}\n{item.get('name') or 'UNKNOWN'}")
                draw_tactical()
            render_list(kind)

        def map_press(event):
            mode=map_view.get("mode","select")
            if mode=="zoom":
                zoom_map_at(event.x,event.y,1.7)
                return
            if mode=="pan":
                map_view["drag"]=(event.x,event.y,map_view["cx"],map_view["cy"])
                return
            marker_click(event)

        pan_state={"after":None,"dirty":False}

        def _flush_pan_redraw():
            pan_state["after"]=None
            if pan_state["dirty"]:
                pan_state["dirty"]=False
                draw_tactical()

        def map_drag(event):
            if map_view.get("mode")!="pan" or not map_view.get("drag"):
                return
            sx,sy,scx,scy=map_view["drag"]
            w=max(globe.winfo_width(),420); h=max(globe.winfo_height(),300)
            _,_,draw_w,draw_h=map_rect(w,h)
            z=map_view["zoom"]
            map_view["cx"]=scx-(event.x-sx)/(draw_w*z)
            map_view["cy"]=scy-(event.y-sy)/(draw_h*z)
            clamp_map_view()
            # Do not rebuild the complete map on every mouse-motion event.
            # On the old VAIO that caused visible flashing; cap panning redraws.
            pan_state["dirty"]=True
            if pan_state["after"] is None:
                pan_state["after"]=win.after(55,_flush_pan_redraw)

        def map_release(_event):
            map_view["drag"]=None
            if pan_state["after"] is not None:
                try: win.after_cancel(pan_state["after"])
                except Exception: pass
                pan_state["after"]=None
            pan_state["dirty"]=False
            draw_tactical()

        def map_wheel(event):
            if getattr(event,"num",None)==4:
                factor=1.3
            elif getattr(event,"num",None)==5:
                factor=1/1.3
            else:
                factor=1.3 if getattr(event,"delta",0)>0 else 1/1.3
            zoom_map_at(event.x,event.y,factor)

        globe.bind("<Configure>",draw_tactical)
        globe.bind("<Button-1>",map_press)
        globe.bind("<B1-Motion>",map_drag)
        globe.bind("<ButtonRelease-1>",map_release)
        globe.bind("<MouseWheel>",map_wheel)
        globe.bind("<Button-4>",map_wheel)
        globe.bind("<Button-5>",map_wheel)
        globe.bind("<Double-Button-3>",lambda _e:reset_map_view())

        def finish_layer(kind,message):
            loading_layers.discard(kind)
            loaded_layers.add(kind)
            if not win.winfo_exists(): return
            status_var.set("GLOBAL LINK // READY")
            if kind=="SEA":
                try:
                    sea_progress.stop()
                    sea_loading.pack_forget()
                except Exception:
                    pass
            if kind=="AIR":
                air_refresh_status.set("AUTO REFRESH // 30 S")
            detail.set(message)
            if enabled.get(kind):
                render_list(kind)
            draw_tactical()

        def fetch_layer(kind,force=False):
            if kind in loading_layers:
                return
            if kind in loaded_layers and not force:
                return
            loading_layers.add(kind)
            if kind=="AIR":
                air_refresh_status.set("REFRESHING..." if force else "LOADING...")
            if kind=="SEA":
                try:
                    sea_loading_text.set("SEA // SCANNING AIS... PLEASE WAIT")
                    if not sea_loading.winfo_manager():
                        try: sea_loading.pack(fill="x",padx=12,pady=(0,8),before=list_frame)
                        except Exception: sea_loading.pack(fill="x",padx=12,pady=(0,8))
                    sea_progress.start()
                except Exception:
                    pass
            status_var.set(f"{kind} // SYNCING")
            detail.set(f"{kind} // LOADING ON DEMAND...")
            def worker():
                message=f"{kind} // READY"
                try:
                    if kind=="AIR":
                        req=urllib.request.Request("https://opensky-network.org/api/states/all",
                                                   headers={"User-Agent":"UltronEye/1.0"})
                        with urllib.request.urlopen(req,timeout=8) as r:
                            data=json.loads(r.read().decode())
                        air=[]
                        for x in (data.get("states") or [])[:300]:
                            pos=normalize_geo(x[6] if len(x)>6 else None,x[5] if len(x)>5 else None)
                            if not pos: continue
                            lat,lon=pos
                            air.append({"icao24":x[0],"callsign":(x[1] or "UNKNOWN").strip(),"lon":lon,"lat":lat,
                                        "alt":x[7],"speed":x[9] if len(x)>9 else None,
                                        "heading":x[10] if len(x)>10 else 0,
                                        "vertical_rate":x[11] if len(x)>11 else None})
                        old_sel=selected_air.get("item")
                        old_callsign=(old_sel or {}).get("callsign")
                        self._eye_data["AIR"]=air
                        if old_callsign:
                            selected_air["item"]=next((a for a in air if a.get("callsign")==old_callsign),None)
                        message=f"AIR // {len(air)} AIRCRAFT"

                    elif kind=="RADIO":
                        req=urllib.request.Request("https://de1.api.radio-browser.info/json/stations/topvote/80",
                                                   headers={"User-Agent":"UltronEye/1.0"})
                        with urllib.request.urlopen(req,timeout=8) as r:
                            data=json.loads(r.read().decode())
                        radios=[]
                        for x in data:
                            pos=normalize_geo(x.get("geo_lat"),x.get("geo_long"))
                            if pos:
                                x["lat"],x["lon"]=pos
                            else:
                                x["lat"]=x["lon"]=None
                            radios.append(x)
                        self._eye_data["RADIO"]=radios
                        message=f"RADIO // {len(radios)} STATIONS"

                    elif kind=="SEA":
                        key=os.environ.get("AISSTREAM_API_KEY","").strip()
                        if not key:
                            message="SEA // AISSTREAM_API_KEY REQUIRED"
                        else:
                            import websockets
                            boxes=[
                                [[32,-100],[18,-75]],
                                [[42,-82],[24,-66]],
                                [[61,-10],[48,10]],
                                [[46,-6],[30,18]],
                                [[15,100],[1,125]],
                                [[38,118],[20,145]],
                            ]
                            sub={"APIKey":key,"BoundingBoxes":boxes,
                                 "FilterMessageTypes":["PositionReport","StandardClassBPositionReport","ExtendedClassBPositionReport"]}

                            async def collect_ais():
                                sea=[]; seen=set(); confirmed=False
                                raw_count=0; position_count=0; compression_ok=False
                                type_counts={}
                                async with websockets.connect(
                                    "wss://stream.aisstream.io/v0/stream",
                                    open_timeout=8,
                                    ping_interval=20,
                                    ping_timeout=20,
                                    compression="deflate",
                                    max_size=2**20,
                                ) as ws:
                                    try:
                                        ext=(getattr(getattr(ws,"response",None),"headers",{}) or {}).get("Sec-WebSocket-Extensions","")
                                        compression_ok="permessage-deflate" in str(ext).lower()
                                    except Exception:
                                        compression_ok=False
                                    await ws.send(json.dumps(sub))
                                    deadline=time.time()+15
                                    while time.time()<deadline and len(sea)<150:
                                        left=max(0.2,deadline-time.time())
                                        try:
                                            raw=await asyncio.wait_for(ws.recv(),timeout=min(3,left))
                                        except asyncio.TimeoutError:
                                            continue
                                        if isinstance(raw,(bytes,bytearray)):
                                            raw=raw.decode("utf-8","replace")
                                        raw_count+=1
                                        msg=json.loads(raw)
                                        mtype=msg.get("MessageType") or "UNKNOWN"
                                        type_counts[mtype]=type_counts.get(mtype,0)+1
                                        if mtype=="SubscriptionConfirmation":
                                            confirmed=True
                                            continue
                                        meta=msg.get("MetaData") or {}
                                        body=(msg.get("Message") or {}).get(mtype,{}) or {}
                                        lat=meta.get("Latitude")
                                        lon=meta.get("Longitude")
                                        if lat is None: lat=body.get("Latitude")
                                        if lon is None: lon=body.get("Longitude")
                                        pos=normalize_geo(lat,lon)
                                        if pos:
                                            lat,lon=pos
                                            if not is_ocean_geo(lat,lon):
                                                continue
                                            position_count+=1
                                        else:
                                            continue
                                        mmsi=meta.get("MMSI") or body.get("UserID")
                                        key_id=mmsi or (round(lat,4),round(lon,4))
                                        if key_id in seen:
                                            continue
                                        seen.add(key_id)
                                        sea.append({"name":(meta.get("ShipName") or "VESSEL").strip(),
                                                    "mmsi":mmsi,"lat":lat,"lon":lon,
                                                    "heading":body.get("TrueHeading"),
                                                    "course":body.get("Cog"),
                                                    "speed":body.get("Sog")})
                                return sea,confirmed,raw_count,position_count,compression_ok,type_counts

                            sea,confirmed,raw_count,position_count,compression_ok,type_counts=asyncio.run(collect_ais())
                            self._eye_data["SEA"]=sea
                            diag=(f"KEY // OK\n"
                                  f"SUBSCRIPTION // {'OK' if confirmed else 'NO'}\n"
                                  f"COMPRESSION // {'ON' if compression_ok else 'UNKNOWN'}\n"
                                  f"RAW MESSAGES // {raw_count}\n"
                                  f"POSITION REPORTS // {position_count}\n"
                                  f"VESSELS PARSED // {len(sea)}\n"
                                  f"TYPES // "+", ".join(f"{k}:{v}" for k,v in sorted(type_counts.items(),key=lambda kv:-kv[1])[:3]))
                            if sea:
                                message=f"SEA // {len(sea)} VESSELS\n"+diag
                            elif confirmed:
                                message="SEA // CONNECTED · NO VESSELS RECEIVED YET\n"+diag
                            else:
                                message="SEA // NO SUBSCRIPTION CONFIRMATION\n"+diag

                    elif kind=="CAM":
                        cams=[]
                        # Irapuato public cameras first.
                        try:
                            c5base="https://camarasc5i.guanajuato.gob.mx:8443"
                            req=urllib.request.Request(c5base+"/api/v1/camaras",
                                                       headers={"User-Agent":"Mozilla/5.0","Referer":c5base+"/"})
                            with urllib.request.urlopen(req,timeout=10) as r:
                                c5data=json.loads(r.read().decode())
                            for cam in (c5data.get("data") or []):
                                muni=(cam.get("municipio") or {}).get("nombre","")
                                if muni.strip().lower()!="irapuato": continue
                                preview=(cam.get("previewImagen") or "").strip() or f"{cam.get('id')}.jpg"
                                image_url=preview if preview.startswith("http") else c5base+"/img/previews/"+preview.lstrip("/")
                                cams.append({"title":cam.get("calle") or cam.get("descripcion") or f"CAM {cam.get('id')}",
                                             "kind":"C5I PUBLIC","airport":"Irapuato // Guanajuato C5i",
                                             "country_code":"MX","country_name":"MÉXICO","region":"Irapuato",
                                             "lat":None,"lon":None,"image_url":image_url,"live_url":c5base+"/",
                                             "refresh_seconds":60,"local_city":True,"source":"GTO C5I"})
                        except Exception:
                            pass

                        cache_path=os.path.join(os.path.dirname(os.path.dirname(__file__)),"data","eye_global_cameras.json")
                        raw=None
                        if os.path.exists(cache_path):
                            try: raw=Path(cache_path).read_bytes()
                            except Exception: raw=None
                        if raw is None or time.time()-os.path.getmtime(cache_path)>=900:
                            try:
                                req=urllib.request.Request("https://provenance-online.com/api/cameras",
                                                           headers={"User-Agent":"UltronEye/1.0"})
                                with urllib.request.urlopen(req,timeout=22) as r: raw=r.read()
                                Path(cache_path).parent.mkdir(parents=True,exist_ok=True)
                                Path(cache_path).write_bytes(raw)
                            except Exception:
                                if raw is None: raise
                        prov=json.loads(raw.decode())
                        for cam in (prov.get("cameras") or []):
                            if cam.get("available") is False: continue
                            cid=str(cam.get("id") or "").strip()
                            if not cid: continue
                            code=(cam.get("country") or "").upper()
                            pos=normalize_geo(cam.get("lat"),cam.get("lon"))
                            clat,clon=pos if pos else (None,None)
                            cams.append({"title":cam.get("name") or "PUBLIC CAMERA",
                                         "kind":"GLOBAL PUBLIC CAMERA","country_code":code,
                                         "country_name":country_names.get(code,code or "GLOBAL"),
                                         "region":cam.get("region") or "","lat":clat,"lon":clon,
                                         "image_url":"https://provenance-online.com/api/proxy?id="+urllib.parse.quote(cid,safe=""),
                                         "refresh_seconds":cam.get("refreshSeconds") or 180,
                                         "source":cam.get("source") or "PUBLIC",
                                         "attribution":cam.get("attribution") or "","camera_id":cid})
                        self._eye_data["CAM"]=cams
                        self._eye_cam_filtered=list(cams)
                        countries=sorted({c.get("country_name") for c in cams if c.get("country_name")})
                        win.after(0,lambda vals=["TODOS"]+countries: cam_country_menu.configure(values=vals))
                        message=f"CAM // {len(cams)} PUBLIC CAMERAS"
                except Exception as exc:
                    message=f"{kind} // OFFLINE: {type(exc).__name__}"
                win.after(0,lambda k=kind,m=message:finish_layer(k,m))
            threading.Thread(target=worker,daemon=True).start()

        def toggle_layer(kind):
            enabled[kind]=not enabled[kind]
            selected["kind"]=kind if enabled[kind] else None
            b=layer_buttons[kind]
            fixed={"AIR":"#ff7a00","SEA":"#0b4f9c","CAM":"#ff3333","RADIO":"#00d66b"}[kind]
            b.configure(fg_color=fixed if enabled[kind] else BG_PANEL,
                        border_color=fixed,
                        text_color=BG if enabled[kind] else fixed)
            if enabled[kind]:
                if kind in loaded_layers:
                    render_list(kind)
                else:
                    fetch_layer(kind)
            else:
                if kind=="CAM":
                    cam_filterbar.pack_forget()
                    cam_preview.pack_forget()
                if kind=="AIR":
                    air_tools.pack_forget()
                if kind=="SEA":
                    try:
                        sea_progress.stop()
                        sea_loading.pack_forget()
                    except Exception:
                        pass
                clear_list()
                panel_title.set("LAYERS // STANDBY")
                detail.set("Layer disabled. Select another layer to load it.")
            draw_tactical()

        air_refresh_btn.configure(command=lambda: fetch_layer("AIR",True))

        def auto_refresh_air():
            try:
                if not win.winfo_exists():
                    return
                if enabled.get("AIR") and "AIR" not in loading_layers:
                    fetch_layer("AIR",True)
                win.after(30000,auto_refresh_air)
            except Exception:
                pass
        win.after(30000,auto_refresh_air)

        layer_colors={
            "AIR":"#ff7a00",
            "SEA":"#0b4f9c",
            "CAM":"#ff3333",
            "RADIO":"#00d66b",
        }
        for kind in ("AIR","SEA","CAM","RADIO"):
            fixed=layer_colors[kind]
            b=ctk.CTkButton(controls,text=kind,command=lambda k=kind:toggle_layer(k),fg_color=BG_PANEL,
                            hover_color=BG_PANEL2,border_color=fixed,border_width=1,corner_radius=13,
                            text_color=fixed,height=34,font=("monospace",10,"bold"))
            b.pack(side="left",fill="x",expand=True,padx=6,pady=8)
            layer_buttons[kind]=b

        def fetch_all():
            status_var.set("GLOBAL LINK // SYNCING")
            errors=[]
            # AIR
            try:
                req=urllib.request.Request("https://opensky-network.org/api/states/all",headers={"User-Agent":"UltronEye/1.0"})
                with urllib.request.urlopen(req,timeout=8) as r: data=json.loads(r.read().decode())
                air=[]
                for x in (data.get("states") or [])[:300]:
                    if x[5] is None or x[6] is None: continue
                    air.append({"callsign":(x[1] or "UNKNOWN").strip(),"lon":x[5],"lat":x[6],
                                "alt":x[7],"heading":x[10] if len(x)>10 else 0})
                self._eye_data["AIR"]=air
            except Exception as exc: errors.append("AIR")
            # CAM: Irapuato public C5i + global public road-camera catalogue.
            cams=[]
            try:
                c5base="https://camarasc5i.guanajuato.gob.mx:8443"
                req=urllib.request.Request(c5base+"/api/v1/camaras",
                                           headers={"User-Agent":"Mozilla/5.0","Referer":c5base+"/"})
                with urllib.request.urlopen(req,timeout=10) as r:
                    c5data=json.loads(r.read().decode())
                for cam in (c5data.get("data") or []):
                    muni=(cam.get("municipio") or {}).get("nombre","")
                    if muni.strip().lower()!="irapuato": continue
                    preview=(cam.get("previewImagen") or "").strip()
                    if not preview: preview=f"{cam.get('id')}.jpg"
                    image_url=preview if preview.startswith("http") else c5base+"/img/previews/"+preview.lstrip("/")
                    cams.append({"title":cam.get("calle") or cam.get("descripcion") or f"CAM {cam.get('id')}",
                                 "kind":"C5I PUBLIC","airport":"Irapuato // Guanajuato C5i",
                                 "country_code":"MX","country_name":"MÉXICO","region":"Irapuato",
                                 "lat":None,"lon":None,"image_url":image_url,
                                 "live_url":c5base+"/","static_preview":True,
                                 "refresh_seconds":60,"local_city":True,"source":"GTO C5I"})
            except Exception:
                errors.append("CAM LOCAL")

            try:
                cache_path=os.path.join(os.path.dirname(os.path.dirname(__file__)),"data","eye_global_cameras.json")
                raw=None
                if os.path.exists(cache_path) and time.time()-os.path.getmtime(cache_path)<900:
                    try:
                        raw=Path(cache_path).read_bytes()
                    except Exception:
                        raw=None
                if raw is None:
                    req=urllib.request.Request("https://provenance-online.com/api/cameras",
                                               headers={"User-Agent":"UltronEye/1.0"})
                    with urllib.request.urlopen(req,timeout=22) as r:
                        raw=r.read()
                    try:
                        Path(cache_path).parent.mkdir(parents=True,exist_ok=True)
                        Path(cache_path).write_bytes(raw)
                    except Exception:
                        pass
                prov=json.loads(raw.decode())
                for cam in (prov.get("cameras") or []):
                    if cam.get("available") is False: continue
                    cid=str(cam.get("id") or "").strip()
                    if not cid: continue
                    code=(cam.get("country") or "").upper()
                    cname=country_names.get(code,code or "GLOBAL")
                    cams.append({
                        "title":cam.get("name") or "PUBLIC CAMERA",
                        "kind":"GLOBAL PUBLIC CAMERA",
                        "country_code":code,"country_name":cname,
                        "region":cam.get("region") or "",
                        "lat":cam.get("lat"),"lon":cam.get("lon"),
                        "image_url":"https://provenance-online.com/api/proxy?id="+urllib.parse.quote(cid,safe=""),
                        "refresh_seconds":cam.get("refreshSeconds") or 180,
                        "source":cam.get("source") or "PUBLIC",
                        "attribution":cam.get("attribution") or "",
                        "camera_id":cid,
                    })
            except Exception:
                # A stale cache is still preferable to losing the global layer.
                try:
                    raw=Path(cache_path).read_bytes()
                    prov=json.loads(raw.decode())
                    for cam in (prov.get("cameras") or []):
                        if cam.get("available") is False: continue
                        cid=str(cam.get("id") or "").strip()
                        if not cid: continue
                        code=(cam.get("country") or "").upper()
                        cams.append({
                            "title":cam.get("name") or "PUBLIC CAMERA",
                            "kind":"GLOBAL PUBLIC CAMERA",
                            "country_code":code,"country_name":country_names.get(code,code or "GLOBAL"),
                            "region":cam.get("region") or "",
                            "lat":cam.get("lat"),"lon":cam.get("lon"),
                            "image_url":"https://provenance-online.com/api/proxy?id="+urllib.parse.quote(cid,safe=""),
                            "refresh_seconds":cam.get("refreshSeconds") or 180,
                            "source":cam.get("source") or "PUBLIC",
                            "attribution":cam.get("attribution") or "",
                            "camera_id":cid,
                        })
                    errors.append("CAM GLOBAL CACHE")
                except Exception:
                    errors.append("CAM GLOBAL")
            self._eye_data["CAM"]=cams
            # RADIO
            try:
                req=urllib.request.Request("https://de1.api.radio-browser.info/json/stations/topvote/80",headers={"User-Agent":"UltronEye/1.0"})
                with urllib.request.urlopen(req,timeout=8) as r: data=json.loads(r.read().decode())
                radios=[]
                for x in data:
                    try:
                        lat=float(x.get("geo_lat")); lon=float(x.get("geo_long"))
                    except Exception: lat=lon=None
                    x["lat"]=lat; x["lon"]=lon; radios.append(x)
                self._eye_data["RADIO"]=radios
            except Exception as exc: errors.append("RADIO")
            # SEA (optional API key)
            key=os.environ.get("AISSTREAM_API_KEY","").strip()
            if key:
                try:
                    import websocket
                    ws=websocket.create_connection("wss://stream.aisstream.io/v0/stream",timeout=8)
                    sub={"APIKey":key,"BoundingBoxes":[[[-90,-180],[90,180]]],
                         "FilterMessageTypes":["PositionReport","StandardClassBPositionReport","ExtendedClassBPositionReport"]}
                    ws.send(json.dumps(sub)); sea=[]; deadline=time.time()+5
                    while time.time()<deadline and len(sea)<100:
                        msg=json.loads(ws.recv()); meta=msg.get("MetaData") or {}
                        if meta.get("Latitude") is not None:
                            sea.append({"name":(meta.get("ShipName") or "VESSEL").strip(),"mmsi":meta.get("MMSI"),
                                        "lat":meta.get("Latitude"),"lon":meta.get("Longitude")})
                    ws.close(); self._eye_data["SEA"]=sea
                except Exception: errors.append("SEA")
            else:
                errors.append("SEA*")
            def done():
                status_var.set("GLOBAL LINK // "+("PARTIAL" if errors else "ONLINE"))
                detail.set("SYNC COMPLETE\n"+("Pending: "+", ".join(errors) if errors else "All layers online."))
                countries=sorted({c.get("country_name") for c in self._eye_data.get("CAM",[]) if c.get("country_name")})
                cam_country_menu.configure(values=["TODOS"]+countries)
                self._eye_cam_filtered=list(self._eye_data.get("CAM",[]))
                draw_tactical(); render_list(selected["kind"])
            win.after(0,done)
        # Do not preload any network layer: this keeps old/low-power PCs responsive.
        status_var.set("GLOBAL LINK // STANDBY")
        panel_title.set("LAYERS // STANDBY")
        clear_list()
        ctk.CTkLabel(list_frame,text="SELECT A LAYER\nAIR · SEA · CAM · RADIO",
                     text_color=TEXT_DIM,font=("monospace",10,"bold"),justify="center").pack(pady=28)
        win.after(120,draw_tactical)

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
            card = tk.Frame(cards, bg=BG_PANEL, width=120, height=70)
            card.pack(side=tk.LEFT, padx=4, pady=2)
            card.pack_propagate(False)
            tk.Label(card, text=label, font=self.font_small,
                     fg=TEXT_DIM, bg=BG_PANEL).pack(pady=(8, 0))
            var = tk.StringVar(value="-- %")
            self.metric_vars[key] = var
            tk.Label(card, textvariable=var, font=self.font_title,
                     fg=ORANGE, bg=BG_PANEL).pack()

        logs_frame = tk.Frame(parent, bg=BG_PANEL, width=520)
        logs_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(8, 0))
        logs_frame.pack_propagate(False)

        log_header = tk.Frame(logs_frame, bg=BG_PANEL2, height=28)
        log_header.pack(fill=tk.X)
        log_header.pack_propagate(False)
        tk.Label(log_header, text="SYSTEM LOGS", font=self.font_small,
                 fg=ORANGE, bg=BG_PANEL2).pack(side=tk.LEFT, padx=10, pady=4)
        tk.Label(log_header, text="● LIVE", font=self.font_small,
                 fg=GREEN, bg=BG_PANEL2).pack(side=tk.RIGHT, padx=10, pady=4)

        self.log_text = tk.Text(
            logs_frame, bg="#080808", fg=TEXT_DIM, font=self.font_mono,
            relief=tk.FLAT, height=8, state=tk.DISABLED,
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

    def _activate_consciousness(self):
        """
        Un clic activa CONCIENCIA de forma continua.
        Otro clic la desactiva.
        Mientras está activa: escucha -> piensa -> habla -> vuelve a escuchar.
        """
        if not hasattr(self, "core"):
            return

        if self.consciousness_active:
            self.consciousness_active = False
            self._stop_speaking()
            self.ai_busy = False
            self._set_live_text("")
            self._set_consciousness_state(
                "IDLE",
                "● SYSTEM ONLINE",
                TURQUOISE
            )
            self._add_log("CONCIENCIA desactivada")
            return

        self.consciousness_active = True
        self._add_log("CONCIENCIA activada")
        self._begin_continuous_listening()

    def _begin_continuous_listening(self):
        if not self.consciousness_active or self.ai_busy:
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
            daemon=True
        ).start()

    def _set_live_text(self, text):
        self.root.after(0, lambda t=text: self.live_transcript_var.set(t))

    def _record_until_silence(self, wav_path):
        """Graba hasta detectar una pausa después de que el usuario hable."""
        source = self._resolve_input_device()
        cmd = ["parecord"]
        if source:
            cmd.append(f"--device={source}")
        cmd.extend(["--raw", "--format=s16le", "--rate=16000", "--channels=1"])

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        rate = 16000
        sample_width = 2
        chunk_ms = 100
        chunk_bytes = int(rate * sample_width * chunk_ms / 1000)
        max_chunks = int(self.voice_record_seconds * 1000 / chunk_ms)
        silence_needed = max(1, int(self.voice_silence_seconds * 1000 / chunk_ms))

        frames = []
        started = False
        silent = 0
        threshold = 450

        try:
            for _ in range(max_chunks):
                data = proc.stdout.read(chunk_bytes)
                if not data:
                    break
                frames.append(data)
                samples = memoryview(data).cast("h")
                level = int(
                    (sum(sample * sample for sample in samples) / len(samples)) ** 0.5
                ) if samples else 0

                if level >= threshold:
                    started = True
                    silent = 0
                elif started:
                    silent += 1
                    if silent >= silence_needed:
                        break

            if not started:
                raise RuntimeError(
                    "No detecté voz. Revisa el micrófono en Preferencias > Audio."
                )
        finally:
            try:
                proc.terminate()
                proc.wait(timeout=1)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass

        with wave.open(wav_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(sample_width)
            wf.setframerate(rate)
            wf.writeframes(b"".join(frames))

    def _animate_response_text(self, text):
        """Muestra la respuesta palabra por palabra."""
        words = text.split()
        shown = []

        def step(i=0):
            if i >= len(words):
                return
            shown.append(words[i])
            self.live_transcript_var.set("ULTRON: " + " ".join(shown))
            self.root.after(35, lambda: step(i + 1))

        self.root.after(0, step)

    def _voice_cycle(self):
        """Grabación -> Groq STT -> Groq chat -> voz local."""
        wav_path = None

        try:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise RuntimeError(
                    "No encuentro GROQ_API_KEY en el entorno. "
                    "Abre ULTRON desde la misma terminal donde "
                    "`echo $GROQ_API_KEY` muestra tu clave."
                )

            if not shutil.which("parecord"):
                raise RuntimeError(
                    "No encuentro `parecord`. Instala PulseAudio utilities con: "
                    "sudo apt install pulseaudio-utils"
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
            self._set_live_text("🎙 ESCUCHANDO…")
            self._record_until_silence(wav_path)

            self.root.after(
                0,
                lambda: self._set_consciousness_state(
                    "THINKING",
                    "● CONCIENCIA PENSANDO",
                    ORANGE_L
                )
            )
            self._safe_log("CONCIENCIA: audio capturado")

            user_text = self._groq_transcribe(wav_path, api_key).strip()

            if not user_text:
                raise RuntimeError("No pude detectar voz en la grabación.")

            self._safe_log(f"TÚ: {user_text}")
            self._set_live_text(f"TÚ: {user_text}")

            self.ai_history.append({
                "role": "user",
                "content": user_text
            })

            # Evitar mandar una conversación enorme en cada petición.
            system_message = self.ai_history[0]
            recent = self.ai_history[1:][-12:]
            payload_history = [system_message] + recent

            response_text = self._groq_chat(payload_history, api_key).strip()

            if not response_text:
                raise RuntimeError("Groq devolvió una respuesta vacía.")

            self.ai_history.append({
                "role": "assistant",
                "content": response_text
            })

            self._safe_log(f"ULTRON: {response_text}")
            self._animate_response_text(response_text)

            self.root.after(
                0,
                lambda: self._set_consciousness_state(
                    "SPEAKING",
                    "● CONCIENCIA HABLANDO",
                    GREEN
                )
            )

            self._speak_text(response_text)

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

            if self.consciousness_active:
                self.root.after(
                    120,
                    self._begin_continuous_listening
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
        self.root.after(0, lambda t=text: self._add_log(t))

    def _voice_error(self, message):
        self._set_consciousness_state(
            "IDLE",
            "● CONCIENCIA ERROR",
            RED
        )
        self._show_module(
            "CONCIENCIA / AUDIO",
            message
        )

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
        """Detiene la reproducción actual inmediatamente."""
        process = self.tts_process
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

    def _speak_text(self, text):
        """
        Voz principal: edge-tts (más natural, online).
        Respaldo: espeak-ng/espeak si edge-tts no está instalado o falla.
        """
        edge_tts = shutil.which("edge-tts")
        paplay = shutil.which("paplay")

        if not paplay:
            raise RuntimeError(
                "No encuentro `paplay`. Instala: sudo apt install pulseaudio-utils"
            )

        default_sink = self._resolve_output_device()

        if default_sink:
            try:
                subprocess.run(
                    ["pactl", "set-sink-volume", default_sink, f"{int(self.ultron_volume)}%"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=3
                )
            except Exception:
                pass

        # Voz natural principal.
        if edge_tts:
            mp3 = tempfile.NamedTemporaryFile(
                prefix="ultron_tts_",
                suffix=".mp3",
                delete=False
            )
            speech_path = mp3.name
            mp3.close()

            try:
                synth = subprocess.run(
                    [
                        edge_tts,
                        "--voice", "es-MX-DaliaNeural",
                        "--rate=+0%",
                        "--pitch=+0Hz",
                        "--text", text,
                        "--write-media", speech_path
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=45
                )

                if synth.returncode == 0 and os.path.getsize(speech_path) > 500:
                    player = shutil.which("ffplay") or shutil.which("mpv")
                    if player:
                        if os.path.basename(player) == "ffplay":
                            cmd = [player, "-nodisp", "-autoexit", "-loglevel", "quiet", speech_path]
                        else:
                            cmd = [player, "--no-video", "--really-quiet", speech_path]

                        self.tts_process = subprocess.Popen(
                            cmd,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        self.tts_process.wait()
                        self.tts_process = None
                        return
            finally:
                try:
                    os.remove(speech_path)
                except Exception:
                    pass

        raise RuntimeError(
            "La voz natural no está disponible. Instala edge-tts con: "
            "python3 -m pip install edge-tts --break-system-packages "
            "y ffmpeg con: sudo apt install ffmpeg"
        )


    def _start_animation(self):
        def tick():
            if hasattr(self, "core"):
                self.core.animate()
            self.root.after(40, tick)
        self.root.after(100, tick)

    def _update_metrics(self):
        if HAS_PSUTIL:
            try:
                self.metric_vars["cpu"].set(f"{psutil.cpu_percent():.0f} %")
                self.metric_vars["ram"].set(f"{psutil.virtual_memory().percent:.0f} %")
                self.metric_vars["disk"].set(f"{psutil.disk_usage('/').percent:.0f} %")
                self.metric_vars["net"].set("connected")
            except Exception:
                pass
        else:
            self.metric_vars["cpu"].set("-- %")
            self.metric_vars["ram"].set("-- %")
            self.metric_vars["disk"].set("-- %")
            self.metric_vars["net"].set("N/A")
        self.root.after(2000, self._update_metrics)

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

    def _open_module_window(self, key, title, geometry, minsize=None):
        old = getattr(self, "active_module_window", None)
        if old is not None and old.winfo_exists():
            same = getattr(self, "active_module_key", None) == key
            old.destroy()
            self.active_module_window = None
            self.active_module_key = None
            if same:
                return None
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry(geometry)
        if minsize:
            win.minsize(*minsize)
        win.transient(self.root)
        self.active_module_window = win
        self.active_module_key = key
        def closed(_event=None):
            if self.active_module_window is win:
                self.active_module_window = None
                self.active_module_key = None
        win.bind("<Destroy>", closed)
        return win

    def _ui_card(self, parent, title=None, expand=False):
        card = tk.Frame(parent, bg=BG_PANEL2, highlightbackground=ORANGE_D, highlightthickness=1)
        if title:
            tk.Label(card, text=title, font=self.font_title, fg=ORANGE, bg=BG_PANEL2, anchor="w").pack(fill=tk.X, padx=16, pady=(12,6))
        return card

    def _ui_button(self, parent, text, command, accent=False):
        return tk.Button(parent, text=text, font=self.font_small, fg=TURQUOISE if accent else TEXT,
                         bg=BG_PANEL2, activeforeground=ORANGE_L, activebackground=GRAY,
                         highlightbackground=ORANGE_D, highlightthickness=1, relief=tk.FLAT,
                         cursor="hand2", command=command, padx=12, pady=8)

    def _neo_window(self, key, title, geometry="920x650"):
        win = self._open_module_window(key, f"ULTRON — {title}", geometry, (760, 520))
        if win is None: return None, None
        win.configure(bg=BG)
        if HAS_CTK:
            shell = ctk.CTkFrame(win, fg_color=BG, corner_radius=0)
            shell.pack(fill="both", expand=True, padx=12, pady=12)
            ctk.CTkLabel(shell, text=title, text_color=ORANGE, font=("monospace",22,"bold"), anchor="w").pack(fill="x", padx=16, pady=(10,8))
            body = ctk.CTkScrollableFrame(shell, fg_color=BG, corner_radius=0, scrollbar_button_color=ORANGE_D)
            body.pack(fill="both", expand=True)
        else:
            body=tk.Frame(win,bg=BG); body.pack(fill=tk.BOTH,expand=True,padx=16,pady=16)
            tk.Label(body,text=title,font=self.font_title,fg=ORANGE,bg=BG).pack(anchor="w")
        return win, body

    def _neo_card(self, parent, title, text="", accent=None):
        accent = accent or ORANGE
        if HAS_CTK:
            card=ctk.CTkFrame(parent,fg_color=BG_PANEL2,border_color=accent,border_width=1,corner_radius=18)
            card.pack(fill="x",padx=10,pady=7)
            ctk.CTkLabel(card,text=title,text_color=accent,font=("monospace",15,"bold"),anchor="w").pack(fill="x",padx=16,pady=(12,4))
            if text: ctk.CTkLabel(card,text=text,text_color=TEXT,font=("monospace",12),justify="left",anchor="w",wraplength=760).pack(fill="x",padx=16,pady=(0,13))
        else:
            card=tk.Frame(parent,bg=BG_PANEL2,highlightbackground=accent,highlightthickness=1); card.pack(fill=tk.X,padx=10,pady=7)
            tk.Label(card,text=title,font=self.font_title,fg=accent,bg=BG_PANEL2).pack(anchor="w",padx=14,pady=8)
            if text: tk.Label(card,text=text,font=self.font_mono,fg=TEXT,bg=BG_PANEL2,justify="left").pack(anchor="w",padx=14,pady=(0,10))
        return card

    def _neo_button(self, parent, text, command, accent=None):
        accent=accent or ORANGE
        if HAS_CTK:
            b=ctk.CTkButton(parent,text=text,command=command,fg_color=BG_PANEL2,hover_color=GRAY,border_color=accent,border_width=1,corner_radius=16,text_color=accent,font=("monospace",12,"bold"),height=38)
            b.pack(fill="x",padx=12,pady=5)
        else:
            b=tk.Button(parent,text=text,command=command,bg=BG_PANEL2,fg=accent,relief=tk.FLAT); b.pack(fill=tk.X,padx=12,pady=5)
        return b

    def _on_ai(self):
        self._add_log("Module CONCIENCIA selected")
        win=self._open_module_window("AI","ULTRON — CONCIENCIA","940x650",(760,520))
        if win is None:return
        win.configure(bg=BG)
        if not HAS_CTK:return
        shell=ctk.CTkFrame(win,fg_color=BG,corner_radius=0); shell.pack(fill="both",expand=True,padx=18,pady=14)
        head=ctk.CTkFrame(shell,fg_color="transparent"); head.pack(fill="x",padx=8,pady=(0,8))
        ctk.CTkLabel(head,text="Conciencia",text_color=ORANGE,font=("monospace",25,"bold")).pack(side="left")
        status=ctk.CTkLabel(head,text="● IA LISTA",text_color=TURQUOISE,font=("monospace",10,"bold")); status.pack(side="right",padx=8)
        chat_card=ctk.CTkFrame(shell,fg_color=BG_PANEL2,border_color=ORANGE_D,border_width=1,corner_radius=22); chat_card.pack(fill="both",expand=True,pady=(0,10))
        chat=ctk.CTkTextbox(chat_card,fg_color=BG_PANEL,corner_radius=17,text_color=TEXT,font=("monospace",11),wrap="word",activate_scrollbars=True); chat.pack(fill="both",expand=True,padx=12,pady=12); chat.configure(state="disabled")
        bottom=ctk.CTkFrame(shell,fg_color=BG_PANEL2,border_color=ORANGE_D,border_width=1,corner_radius=22,height=64); bottom.pack(fill="x"); bottom.pack_propagate(False)
        entry=ctk.CTkEntry(bottom,placeholder_text="Escribe a ULTRON...",fg_color=BG_PANEL,border_color=GRAY,corner_radius=18,text_color=TEXT,height=42,font=("monospace",11)); entry.pack(side="left",fill="x",expand=True,padx=(12,7),pady=11)
        def add(who,text):
            chat.configure(state="normal"); chat.insert("end",f"{who}  //  {text}\n\n"); chat.see("end"); chat.configure(state="disabled")
        def send(_event=None):
            message=entry.get().strip()
            if not message or self.ai_busy:return
            entry.delete(0,"end"); add("TÚ",message); self.ai_busy=True; status.configure(text="● PENSANDO...",text_color=ORANGE)
            def worker():
                try:
                    api_key=os.getenv("GROQ_API_KEY")
                    if not api_key:raise RuntimeError("No encuentro GROQ_API_KEY en el entorno.")
                    self.ai_history.append({"role":"user","content":message}); history=[self.ai_history[0]]+self.ai_history[1:][-12:]
                    answer=self._groq_chat(history,api_key).strip()
                    if not answer:raise RuntimeError("Groq devolvió una respuesta vacía.")
                    self.ai_history.append({"role":"assistant","content":answer}); self.root.after(0,lambda:add("ULTRON",answer)); self._safe_log(f"CHAT IA: {answer}")
                except Exception as exc:self.root.after(0,lambda e=str(exc):add("ERROR",e))
                finally:
                    self.ai_busy=False; self.root.after(0,lambda:status.configure(text="● IA LISTA",text_color=TURQUOISE))
            threading.Thread(target=worker,daemon=True).start()
        send_btn=ctk.CTkButton(bottom,text="➤",command=send,width=52,height=42,corner_radius=18,fg_color=ORANGE_D,hover_color=ORANGE,text_color=TEXT,font=("monospace",22,"bold")); send_btn.pack(side="right",padx=(0,12),pady=11)
        entry.bind("<Return>",send); add("ULTRON","CONCIENCIA lista. Escribe un mensaje."); entry.focus_set()

    def _on_system(self):
        self._add_log("Module SISTEMA selected")
        win=self._open_module_window("SYSTEM","ULTRON — SISTEMA","940x650",(760,520))
        if win is None:return
        win.configure(bg=BG)
        if not HAS_CTK:return
        shell=ctk.CTkFrame(win,fg_color=BG,corner_radius=0); shell.pack(fill="both",expand=True,padx=18,pady=14)
        ctk.CTkLabel(shell,text="Sistema",text_color=ORANGE,font=("monospace",25,"bold"),anchor="e").pack(fill="x",padx=10,pady=(0,8))
        body=ctk.CTkFrame(shell,fg_color="transparent"); body.pack(fill="both",expand=True)
        left=ctk.CTkFrame(body,fg_color=BG_PANEL2,border_color=ORANGE_D,border_width=1,corner_radius=22); left.pack(side="left",fill="both",expand=True,padx=(0,6))
        right=ctk.CTkFrame(body,fg_color=BG_PANEL2,border_color=TURQUOISE_D,border_width=1,corner_radius=22); right.pack(side="right",fill="both",expand=True,padx=(6,0))
        ctk.CTkLabel(left,text="INFORMACIÓN DEL SISTEMA",text_color=ORANGE,font=("monospace",15,"bold")).pack(anchor="w",padx=18,pady=(18,8))
        info=ctk.CTkLabel(left,text="Cargando...",text_color=TEXT,font=("monospace",11),justify="left",anchor="nw"); info.pack(fill="x",padx=18,pady=5)
        ctk.CTkLabel(right,text="RECURSOS EN TIEMPO REAL",text_color=TURQUOISE,font=("monospace",15,"bold")).pack(anchor="w",padx=18,pady=(18,10))
        rows={}
        for key,label in (("cpu","CPU"),("ram","MEMORIA RAM"),("disk","ALMACENAMIENTO")):
            card=ctk.CTkFrame(right,fg_color=BG_PANEL,corner_radius=16); card.pack(fill="x",padx=14,pady=6)
            top=ctk.CTkFrame(card,fg_color="transparent"); top.pack(fill="x",padx=12,pady=(9,2))
            ctk.CTkLabel(top,text=label,text_color=TEXT_DIM,font=("monospace",10,"bold")).pack(side="left")
            val=ctk.CTkLabel(top,text="--%",text_color=ORANGE,font=("monospace",11,"bold")); val.pack(side="right")
            bar=ctk.CTkProgressBar(card,height=9,corner_radius=5,progress_color=ORANGE,fg_color=BG_PANEL2); bar.pack(fill="x",padx=12,pady=(3,10)); bar.set(0); rows[key]=(val,bar)
        detail=ctk.CTkLabel(right,text="",text_color=TEXT_DIM,font=("monospace",10),justify="left",anchor="nw"); detail.pack(fill="x",padx=18,pady=10)
        def refresh():
            os_name=f"{platform.system()} {platform.release()}"; arch=platform.machine(); host=platform.node(); up=self._uptime_str()
            cpu_name=run_cmd("lscpu | sed -n 's/^Model name:[[:space:]]*//p' | head -1").strip() or platform.processor() or "No detectado"
            kernel=platform.release(); info.configure(text=f"Sistema operativo\n{os_name}\n\nArquitectura\n{arch}\n\nEquipo\n{host}\n\nProcesador\n{cpu_name}\n\nKernel\n{kernel}\n\nTiempo encendido\n{up}")
            if HAS_PSUTIL:
                cpu=psutil.cpu_percent(interval=.25); ram=psutil.virtual_memory(); disk=psutil.disk_usage('/')
                vals={'cpu':cpu,'ram':ram.percent,'disk':disk.percent}
                for k,v in vals.items():
                    rows[k][0].configure(text=f"{v:.0f}%",text_color=RED if v>=90 else ORANGE if v>=75 else TURQUOISE); rows[k][1].configure(progress_color=RED if v>=90 else ORANGE if v>=75 else TURQUOISE); rows[k][1].set(v/100)
                detail.configure(text=f"RAM   {ram.used/1024**3:.1f} / {ram.total/1024**3:.1f} GB\nDISCO {disk.used/1024**3:.1f} / {disk.total/1024**3:.1f} GB")
        refresh()
        ctk.CTkButton(left,text="ACTUALIZAR SISTEMA",command=refresh,fg_color=BG_PANEL,hover_color=GRAY,border_color=ORANGE,border_width=1,corner_radius=17,text_color=ORANGE,height=40,font=("monospace",11,"bold")).pack(side="bottom",fill="x",padx=18,pady=18)

    def _on_network(self):
        self._add_log("Module RED // SEGURIDAD selected")
        win=self._open_module_window("NETWORK","ULTRON — RED // SEGURIDAD","940x650",(760,520))
        if win is None:return
        win.configure(bg=BG)
        if not HAS_CTK:return
        shell=ctk.CTkFrame(win,fg_color=BG,corner_radius=0); shell.pack(fill="both",expand=True,padx=18,pady=14)
        ctk.CTkLabel(shell,text="Red // seguridad",text_color=ORANGE,font=("monospace",24,"bold"),anchor="e").pack(fill="x",padx=10,pady=(0,8))
        body=ctk.CTkFrame(shell,fg_color="transparent"); body.pack(fill="both",expand=True)
        left=ctk.CTkFrame(body,fg_color=BG_PANEL2,border_color=ORANGE_D,border_width=1,corner_radius=22); left.pack(side="left",fill="both",expand=True,padx=(0,6))
        right=ctk.CTkFrame(body,fg_color=BG_PANEL2,border_color=TURQUOISE_D,border_width=1,corner_radius=22); right.pack(side="right",fill="both",expand=True,padx=(6,0))
        ctk.CTkLabel(left,text="INFORMACIÓN DE RED",text_color=ORANGE,font=("monospace",15,"bold")).pack(anchor="w",padx=18,pady=(18,8))
        info=ctk.CTkLabel(left,text="Escaneando...",text_color=TEXT,font=("monospace",11),justify="left",anchor="nw"); info.pack(fill="x",padx=18,pady=5)
        ctk.CTkLabel(right,text="PUERTOS",text_color=TURQUOISE,font=("monospace",15,"bold")).pack(anchor="w",padx=18,pady=(18,8))
        ports=ctk.CTkTextbox(right,fg_color=BG_PANEL,corner_radius=16,text_color=TEXT,font=("monospace",11),wrap="word"); ports.pack(fill="both",expand=True,padx=14,pady=(0,8))
        security=ctk.StringVar(value="SEGURIDAD  •  ANALIZANDO")
        sec_lbl=ctk.CTkLabel(right,textvariable=security,text_color=TURQUOISE,font=("monospace",11,"bold")); sec_lbl.pack(anchor="w",padx=18,pady=5)
        def refresh():
            wifi=run_cmd("nmcli -t -f ACTIVE,SSID,SIGNAL dev wifi | grep '^yes' | head -1").strip().split(':')
            ssid=wifi[1] if len(wifi)>1 else "No conectado"; signal=(wifi[2]+"%") if len(wifi)>2 else "--"
            ip=run_cmd("hostname -I").strip() or "Sin IP"
            eth=bool(run_cmd("nmcli -t -f TYPE,STATE dev | grep '^ethernet:connected' | head -1").strip())
            info.configure(text=f"IP local: {ip}\n\nWi-Fi: {'CONECTADO' if wifi else 'NO CONECTADO'}\nRed: {ssid}\nSeñal: {signal}\n\nEthernet: {'CONECTADO' if eth else 'NO CONECTADO'}")
            raw=run_cmd("ss -tulnH"); common=[(22,'SSH'),(53,'DNS'),(80,'HTTP'),(443,'HTTPS')]; lines=[]; opened=0
            for port,name in common:
                isopen=any((f':{port} ' in x or x.rstrip().endswith(f':{port}')) for x in raw.splitlines())
                opened+=int(isopen); lines.append(f"{port:<5} {name:<8}  {'OPEN' if isopen else 'CLOSED'}")
            listeners=len([x for x in raw.splitlines() if x.strip()]); lines += ["",f"Puertos escuchando: {listeners}",f"Comunes abiertos: {opened}/4"]
            ports.configure(state="normal"); ports.delete("1.0","end"); ports.insert("end","\n".join(lines)); ports.configure(state="disabled")
            security.set("SEGURIDAD  •  SIN ALERTAS" if opened<4 else "SEGURIDAD  •  REVISAR SERVICIOS")
            sec_lbl.configure(text_color=GREEN if opened<4 else ORANGE)
        refresh()
        def power_action(action):
            from tkinter import messagebox
            label="reiniciar" if action=="reboot" else "apagar"
            if not messagebox.askyesno("ULTRON // SEGURIDAD",f"¿Seguro que quieres {label} el equipo?\n\nSe cerrarán los programas abiertos.",parent=win): return
            try:
                if platform.system().lower()=="windows": subprocess.Popen(["shutdown","/r" if action=="reboot" else "/s","/t","0"])
                else: subprocess.Popen(["systemctl",action])
            except Exception as exc: messagebox.showerror("ULTRON // SEGURIDAD",f"No se pudo {label}:\n{exc}",parent=win)
        power=ctk.CTkFrame(left,fg_color="transparent"); power.pack(side="bottom",fill="x",padx=18,pady=(0,18))
        ctk.CTkButton(power,text="REINICIAR",command=lambda:power_action("reboot"),fg_color=BG_PANEL,hover_color=GRAY,border_color=ORANGE,border_width=1,corner_radius=15,text_color=ORANGE).pack(side="left",fill="x",expand=True,padx=(0,4))
        ctk.CTkButton(power,text="APAGAR",command=lambda:power_action("poweroff"),fg_color=BG_PANEL,hover_color=GRAY,border_color=RED,border_width=1,corner_radius=15,text_color=RED).pack(side="left",fill="x",expand=True,padx=(4,0))
        ctk.CTkButton(left,text="ACTUALIZAR RED",command=refresh,fg_color=BG_PANEL,hover_color=GRAY,border_color=ORANGE,border_width=1,corner_radius=17,text_color=ORANGE,height=40,font=("monospace",11,"bold")).pack(side="bottom",fill="x",padx=18,pady=(0,8))

    def _on_files(self):
        self._add_log("Module ALMACENAMIENTO selected")
        win=self._open_module_window("STORAGE","ULTRON — ALMACENAMIENTO","940x650",(760,520))
        if win is None:return
        win.configure(bg=BG)
        if not HAS_CTK:return
        shell=ctk.CTkFrame(win,fg_color=BG,corner_radius=0); shell.pack(fill="both",expand=True,padx=18,pady=14)
        ctk.CTkLabel(shell,text="Almacenamiento",text_color=ORANGE,font=("monospace",24,"bold"),anchor="e").pack(fill="x",padx=10,pady=(0,8))
        body=ctk.CTkFrame(shell,fg_color="transparent"); body.pack(fill="both",expand=True)
        left=ctk.CTkFrame(body,fg_color=BG_PANEL2,border_color=ORANGE_D,border_width=1,corner_radius=22,width=350); left.pack(side="left",fill="both",padx=(0,6)); left.pack_propagate(False)
        right=ctk.CTkFrame(body,fg_color=BG_PANEL2,border_color=TURQUOISE_D,border_width=1,corner_radius=22); right.pack(side="right",fill="both",expand=True,padx=(6,0))
        ctk.CTkLabel(left,text="ESPACIO DEL DISCO",text_color=ORANGE,font=("monospace",15,"bold")).pack(anchor="w",padx=18,pady=(18,12))
        d=psutil.disk_usage('/') if HAS_PSUTIL else None
        rootline=run_cmd("findmnt -no SOURCE,FSTYPE / 2>/dev/null").strip().split()
        dev=rootline[0] if rootline else "/"; fs=rootline[1] if len(rootline)>1 else "--"
        ctk.CTkLabel(left,text=f"Disco: {dev}\nMontaje: /\nSistema: {fs}",text_color=TEXT,font=("monospace",12),justify="left").pack(anchor="w",padx=18,pady=4)
        if d:
            used=d.used/1024**3; total=d.total/1024**3; free=d.free/1024**3
            ctk.CTkLabel(left,text=f"CAPACIDAD   {total:.1f} GB\nUSADO       {used:.1f} GB\nDISPONIBLE  {free:.1f} GB",text_color=TEXT,font=("monospace",12,"bold"),justify="left").pack(anchor="w",padx=18,pady=(18,8))
            ctk.CTkLabel(left,text=f"{d.percent:.0f}%",text_color=TURQUOISE,font=("monospace",22,"bold")).pack(anchor="w",padx=18)
            bar=ctk.CTkProgressBar(left,corner_radius=10,progress_color=TURQUOISE,fg_color=BG_PANEL,height=15); bar.pack(fill="x",padx=18,pady=7); bar.set(d.percent/100)
            state="ADVERTENCIA" if d.percent>=85 else "NORMAL"; color=RED if d.percent>=90 else (ORANGE if d.percent>=85 else GREEN)
            ctk.CTkLabel(left,text=f"// ESTADO: {state}\n{100-d.percent:.0f}% disponible",text_color=color,font=("monospace",12,"bold"),justify="left").pack(anchor="w",padx=18,pady=12)
        ctk.CTkLabel(right,text="DISCOS Y PARTICIONES",text_color=TURQUOISE,font=("monospace",15,"bold")).pack(anchor="w",padx=18,pady=(18,8))
        tree=ctk.CTkTextbox(right,fg_color=BG_PANEL,corner_radius=16,text_color=TEXT,font=("monospace",11),wrap="none"); tree.pack(fill="both",expand=True,padx=14,pady=(0,10))
        def refresh():
            out=run_cmd("lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINTS,MODEL")
            tree.configure(state="normal"); tree.delete("1.0","end"); tree.insert("end",out or "No se encontraron discos."); tree.configure(state="disabled")
        refresh()
        ctk.CTkButton(right,text="ACTUALIZAR DISCOS",command=refresh,fg_color=BG_PANEL,hover_color=GRAY,border_color=TURQUOISE,border_width=1,corner_radius=17,text_color=TURQUOISE,height=40,font=("monospace",11,"bold")).pack(fill="x",padx=14,pady=(0,14))

    def _run_command_async(self, command, output_widget, title="COMANDO"):
        """Ejecuta comandos sin congelar la interfaz."""
        output_widget.configure(state=tk.NORMAL)
        output_widget.delete("1.0", tk.END)
        output_widget.insert(tk.END, f"> {command}\n\nEjecutando...\n")
        output_widget.configure(state=tk.DISABLED)

        def worker():
            try:
                result = subprocess.run(
                    command,
                    shell=True,
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
        """Abre un comando administrativo en una terminal para que sudo pueda pedir contraseña."""
        script = f"{command}; echo; echo 'Presiona ENTER para cerrar'; read _"
        terminals = [
            ["x-terminal-emulator", "-e", "bash", "-lc", script],
            ["gnome-terminal", "--", "bash", "-lc", script],
            ["konsole", "-e", "bash", "-lc", script],
            ["xfce4-terminal", "-e", f"bash -lc {shlex.quote(script)}"],
        ]

        for terminal_cmd in terminals:
            try:
                subprocess.Popen(
                    terminal_cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                self._add_log(f"Terminal administrativa: {command}")
                return
            except FileNotFoundError:
                continue
            except Exception:
                continue

        self._show_module(
            "COMANDO ADMINISTRATIVO",
            "No encontré un emulador de terminal compatible.\n\n"
            f"Ejecuta manualmente:\n\n{command}"
        )

    def _module_action_window(self, title, actions, search_action=None):
        """Ventana reutilizable para módulos de comandos."""
        win = self._open_module_window(f"ACTION:{title}", f"ULTRON — {title}", "780x560", (650, 480))
        if win is None:
            return
        win.configure(bg=BG)
        win.transient(self.root)

        header = tk.Frame(win, bg=BG_PANEL2, height=44)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header, text=title,
            font=self.font_title, fg=ORANGE, bg=BG_PANEL2
        ).pack(side=tk.LEFT, padx=16, pady=8)

        main = tk.Frame(win, bg=BG)
        main.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        controls = tk.Frame(main, bg=BG_PANEL2, width=300, highlightbackground=ORANGE_D, highlightthickness=1)
        controls.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        output_frame = tk.Frame(main, bg=BG_PANEL2, highlightbackground=ORANGE_D, highlightthickness=1)
        output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

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
            self._run_command_async(command, output, title)

        def run_search():
            value = search_var.get().strip()
            if not value:
                output.configure(state=tk.NORMAL)
                output.delete("1.0", tk.END)
                output.insert(tk.END, "Escribe primero el nombre del paquete.")
                output.configure(state=tk.DISABLED)
                return
            command = search_action.format(query=shlex.quote(value))
            run_normal("buscar", command)

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

        tk.Label(
            controls,
            text="Los comandos con sudo se abren\nen una terminal para solicitar\nla contraseña de forma normal.",
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
        self._add_log("Module HERRAMIENTAS selected")
        win=self._open_module_window("TOOLS","ULTRON — HERRAMIENTAS","940x650",(760,520))
        if win is None:return
        win.configure(bg=BG)
        if not HAS_CTK:return
        shell=ctk.CTkFrame(win,fg_color=BG,corner_radius=0); shell.pack(fill="both",expand=True,padx=18,pady=14)
        ctk.CTkLabel(shell,text="Herramientas",text_color=ORANGE,font=("monospace",24,"bold"),anchor="e").pack(fill="x",padx=10,pady=(0,8))
        body=ctk.CTkFrame(shell,fg_color="transparent"); body.pack(fill="both",expand=True)
        tools=ctk.CTkScrollableFrame(body,fg_color=BG_PANEL2,border_color=ORANGE_D,border_width=1,corner_radius=22,width=430,scrollbar_button_color=ORANGE_D); tools.pack(side="left",fill="both",expand=True,padx=(0,6))
        side=ctk.CTkFrame(body,fg_color=BG_PANEL2,border_color=TURQUOISE_D,border_width=1,corner_radius=22,width=270); side.pack(side="right",fill="y",padx=(6,0)); side.pack_propagate(False)
        ctk.CTkLabel(tools,text="HERRAMIENTAS DEL SISTEMA",text_color=ORANGE,font=("monospace",14,"bold")).pack(anchor="w",padx=14,pady=(12,7))
        result=ctk.CTkTextbox(side,fg_color=BG_PANEL,corner_radius=16,text_color=TEXT,font=("monospace",10),wrap="word",height=250); result.pack(fill="both",expand=True,padx=12,pady=(12,8)); result.insert("end","ULTRON // TOOLS\nSelecciona una herramienta."); result.configure(state="disabled")
        def show(title,cmd):
            result.configure(state="normal"); result.delete("1.0","end"); result.insert("end",title+"\n\nEjecutando..."); result.configure(state="disabled")
            def work():
                out=run_cmd(cmd)
                win.after(0,lambda:(result.configure(state="normal"),result.delete("1.0","end"),result.insert("end",title+"\n\n"+(out or "Sin resultados.")),result.configure(state="disabled")))
            threading.Thread(target=work,daemon=True).start()
        entries=[
          ("TERMINAL","Abrir terminal",None),("PROCESOS","Ver y finalizar procesos","ps aux --sort=-%cpu | head -22"),("PUERTOS","Ver conexiones y puertos activos","ss -tuln"),("PING","Probar conexión a Internet","ping -c 4 1.1.1.1"),("RED LOCAL","Ver dispositivos de tu red","ip neigh"),("DISCOS","Ver discos y particiones","lsblk"),("USB","Ver dispositivos conectados","lsusb"),("SENSORES","Temperaturas y hardware","sensors"),("LIMPIEZA","Ver archivos temporales","du -sh /tmp ~/.cache 2>/dev/null"),("IP","Información de red","ip -br addr") ]
        for key,desc,cmd in entries:
            card=ctk.CTkFrame(tools,fg_color=BG_PANEL,corner_radius=15,height=45); card.pack(fill="x",padx=10,pady=4); card.pack_propagate(False)
            ctk.CTkLabel(card,text=f"[ {key} ]",text_color=TURQUOISE,font=("monospace",10,"bold"),width=105,anchor="w").pack(side="left",padx=(12,2))
            ctk.CTkLabel(card,text=desc,text_color=TEXT,font=("monospace",10),anchor="w").pack(side="left",fill="x",expand=True)
            cb=(lambda:self._run_admin_terminal("x-terminal-emulator")) if cmd is None else (lambda k=key,c=cmd:show(k,c))
            ctk.CTkButton(card,text="›",command=cb,width=34,height=28,corner_radius=14,fg_color="transparent",hover_color=GRAY,border_color=ORANGE_D,border_width=1,text_color=ORANGE).pack(side="right",padx=8)
        ctk.CTkLabel(side,text="ACCIONES RÁPIDAS",text_color=TURQUOISE,font=("monospace",12,"bold")).pack(anchor="w",padx=14,pady=(2,5))
        def quick(text,cmd):
            ctk.CTkButton(side,text=text,command=lambda:show(text,cmd),fg_color=BG_PANEL,hover_color=GRAY,border_color=TURQUOISE_D,border_width=1,corner_radius=15,text_color=TURQUOISE,height=36,font=("monospace",10,"bold")).pack(fill="x",padx=12,pady=4)
        quick("REINICIAR RED","nmcli networking off; sleep 1; nmcli networking on")
        quick("BORRAR CACHÉ","rm -rf ~/.cache/thumbnails/* 2>/dev/null; echo 'Caché de miniaturas liberada'")
        quick("LIBERAR RAM","sync; echo 'Sincronización de memoria completada'")

    def _on_diagnostics(self):
        self._add_log("Module DIAGNOSTICO selected")
        win=self._open_module_window("DIAGNOSTICS","ULTRON — DIAGNÓSTICO","940x650",(760,520))
        if win is None:return
        win.configure(bg=BG)
        if not HAS_CTK:return
        shell=ctk.CTkFrame(win,fg_color=BG,corner_radius=0); shell.pack(fill="both",expand=True,padx=18,pady=14)
        ctk.CTkLabel(shell,text="Diagnóstico",text_color=ORANGE,font=("monospace",24,"bold"),anchor="e").pack(fill="x",padx=10,pady=(0,8))
        body=ctk.CTkFrame(shell,fg_color="transparent"); body.pack(fill="both",expand=True)
        left=ctk.CTkFrame(body,fg_color=BG_PANEL2,border_color=ORANGE_D,border_width=1,corner_radius=22); left.pack(side="left",fill="both",expand=True,padx=(0,6))
        right=ctk.CTkFrame(body,fg_color=BG_PANEL2,border_color=TURQUOISE_D,border_width=1,corner_radius=22); right.pack(side="right",fill="both",expand=True,padx=(6,0))
        ctk.CTkLabel(left,text="ESTADO DEL SISTEMA",text_color=ORANGE,font=("monospace",15,"bold")).pack(anchor="w",padx=18,pady=(16,8))
        status_box=ctk.CTkFrame(left,fg_color=BG_PANEL,corner_radius=16); status_box.pack(fill="x",padx=14,pady=5)
        rows={}
        for name in ("CPU","RAM","TEMPERATURA","ALMACENAMIENTO","RED","AUDIO","USB","SERVICIOS"):
            row=ctk.CTkFrame(status_box,fg_color="transparent",height=28); row.pack(fill="x",padx=12,pady=2)
            ctk.CTkLabel(row,text=name,text_color=TEXT,font=("monospace",11,"bold")).pack(side="left")
            lbl=ctk.CTkLabel(row,text="[ ESPERA ]",text_color=TEXT_DIM,font=("monospace",11,"bold")); lbl.pack(side="right"); rows[name]=lbl
        general=ctk.StringVar(value="Estado general: --%")
        ctk.CTkLabel(left,textvariable=general,text_color=TURQUOISE,font=("monospace",13,"bold")).pack(anchor="w",padx=18,pady=(12,4))
        progress=ctk.CTkProgressBar(left,corner_radius=10,progress_color=TURQUOISE,fg_color=BG_PANEL,height=14); progress.pack(fill="x",padx=18); progress.set(0)
        ctk.CTkLabel(right,text="PROBLEMAS DETECTADOS",text_color=TURQUOISE,font=("monospace",15,"bold")).pack(anchor="w",padx=18,pady=(16,8))
        problems=ctk.CTkTextbox(right,fg_color=BG_PANEL,corner_radius=16,text_color=TEXT,font=("monospace",11),wrap="word",height=210); problems.pack(fill="both",expand=True,padx=14,pady=(0,10)); problems.insert("end","Aún no se ha ejecutado el diagnóstico."); problems.configure(state="disabled")
        def run_diag():
            for x in rows.values(): x.configure(text="[ ... ]",text_color=TEXT_DIM)
            problems.configure(state="normal"); problems.delete("1.0","end"); problems.insert("end","Analizando sistema..."); problems.configure(state="disabled")
            def work():
                checks={}
                checks["CPU"]=(psutil.cpu_percent(interval=.3)<95 if HAS_PSUTIL else True,"Uso de CPU muy alto")
                checks["RAM"]=(psutil.virtual_memory().percent<95 if HAS_PSUTIL else True,"Memoria RAM casi llena")
                checks["ALMACENAMIENTO"]=(psutil.disk_usage('/').percent<90 if HAS_PSUTIL else True,"Disco principal por encima del 90%")
                checks["RED"]=(bool(run_cmd("hostname -I").strip()),"Sin dirección IP de red")
                checks["USB"]=(True if run_cmd("lsusb").strip() else False,"No se detectaron dispositivos USB")
                checks["AUDIO"]=(bool(run_cmd("aplay -l 2>/dev/null").strip()),"Dispositivo de audio sin respuesta")
                checks["SERVICIOS"]=(not bool(run_cmd("systemctl --failed --no-legend 2>/dev/null").strip()),"Hay servicios del sistema con fallos")
                temp=run_cmd("sensors 2>/dev/null"); checks["TEMPERATURA"]=(bool(temp),"Sensores de temperatura no disponibles")
                ok=sum(1 for v,_ in checks.values() if v); pct=round(ok/len(checks)*100); issues=[]
                for name,(good,msg) in checks.items():
                    if not good:
                        detail=msg
                        if name=="SERVICIOS":
                            raw=run_cmd("systemctl --failed --no-legend --plain 2>/dev/null").strip()
                            if raw: detail += "\n\n" + raw
                        elif name=="ALMACENAMIENTO" and HAS_PSUTIL:
                            detail += f" ({psutil.disk_usage('/').percent:.0f}% usado)"
                        elif name=="RED":
                            detail += "\nRevisa Wi-Fi/Ethernet y la asignación de IP."
                        elif name=="AUDIO":
                            detail += "\nNo se encontró una salida ALSA utilizable."
                        issues.append(f"⚠ {name}\n{detail}")
                def paint():
                    for name,(good,_) in checks.items(): rows[name].configure(text="[ OK ]" if good else "[ ALERTA ]",text_color=GREEN if good else RED)
                    general.set(f"Estado general: {pct}%"); progress.set(pct/100)
                    problems.configure(state="normal"); problems.delete("1.0","end"); problems.insert("end","\n\n────────────────────\n\n".join(issues) if issues else "✓ No se detectaron problemas en las pruebas realizadas."); problems.configure(state="disabled")
                win.after(0,paint)
            threading.Thread(target=work,daemon=True).start()
        ctk.CTkButton(right,text="INICIAR DIAGNÓSTICO COMPLETO",command=run_diag,fg_color=BG_PANEL,hover_color=GRAY,border_color=ORANGE,border_width=1,corner_radius=17,text_color=ORANGE,font=("monospace",11,"bold"),height=42).pack(fill="x",padx=14,pady=(0,14))

    def _on_packages(self):
        self._add_log("Module PAQUETES selected")
        win=self._open_module_window("PACKAGES","ULTRON — PAQUETES","940x650",(760,520))
        if win is None:return
        win.configure(bg=BG)
        if not HAS_CTK:
            self._module_action_window("PAQUETES",actions=[]); return
        shell=ctk.CTkFrame(win,fg_color=BG,corner_radius=0); shell.pack(fill="both",expand=True,padx=18,pady=14)
        ctk.CTkLabel(shell,text="Paquetes",text_color=ORANGE,font=("monospace",24,"bold"),anchor="e").pack(fill="x",padx=10,pady=(0,10))
        body=ctk.CTkFrame(shell,fg_color="transparent"); body.pack(fill="both",expand=True)
        left=ctk.CTkFrame(body,fg_color=BG_PANEL2,border_color=ORANGE_D,border_width=1,corner_radius=22,width=270); left.pack(side="left",fill="y",padx=(0,10)); left.pack_propagate(False)
        right=ctk.CTkFrame(body,fg_color=BG_PANEL2,border_color=TURQUOISE_D,border_width=1,corner_radius=22); right.pack(side="right",fill="both",expand=True)
        ctk.CTkLabel(left,text="ACCIONES",text_color=ORANGE,font=("monospace",15,"bold")).pack(anchor="w",padx=18,pady=(18,10))
        ctk.CTkLabel(right,text="Resultados",text_color=TURQUOISE,font=("monospace",16,"bold")).pack(anchor="w",padx=18,pady=(16,6))
        output=ctk.CTkTextbox(right,fg_color=BG_PANEL,border_width=0,corner_radius=16,text_color=TEXT,font=("monospace",11),wrap="word"); output.pack(fill="both",expand=True,padx=14,pady=(0,14)); output.insert("end","ULTRON // PAQUETES\n\nSelecciona una acción."); output.configure(state="disabled")
        search_var=tk.StringVar()
        search=ctk.CTkEntry(left,textvariable=search_var,placeholder_text="Buscar paquete...",fg_color=BG_PANEL,border_color=ORANGE_D,corner_radius=16,height=38,text_color=TEXT); search.pack(fill="x",padx=14,pady=(0,8))
        def show(text):
            output.configure(state="normal"); output.delete("1.0","end"); output.insert("end",text or "Sin resultados."); output.configure(state="disabled")
        def run(label,cmd):
            show(f"{label}\n\nEjecutando...")
            def work():
                result=run_cmd(cmd); win.after(0,lambda:show(f"{label}\n\n{result}"))
            threading.Thread(target=work,daemon=True).start()
        def search_pkg():
            q=search_var.get().strip();
            if q: run("BUSCAR: "+q,"apt-cache search "+shlex.quote(q))
        search.bind("<Return>",lambda _e:search_pkg())
        def btn(text,cmd=None,admin=False,accent=None,callback=None):
            color=accent or ORANGE
            cb=callback or (lambda:self._run_admin_terminal(cmd) if admin else run(text,cmd))
            ctk.CTkButton(left,text=text,command=cb,fg_color=BG_PANEL,hover_color=GRAY,border_color=color,border_width=1,corner_radius=16,text_color=color,font=("monospace",11,"bold"),height=39,anchor="w").pack(fill="x",padx=14,pady=5)
        btn("[ BUSCAR ]",callback=search_pkg,accent=TURQUOISE)
        btn("Ver paquetes instalados","apt list --installed 2>/dev/null")
        btn("Actualizar repos","sudo apt update",True)
        btn("Actualizar sistema","sudo apt upgrade",True)
        btn("Limpiar paquetes","sudo apt autoremove",True,RED)
        ctk.CTkLabel(left,text="Los comandos administrativos\nse abren en una terminal para\nsolicitar la contraseña.",text_color=TEXT_DIM,font=("monospace",10),justify="left").pack(side="bottom",anchor="w",padx=16,pady=16)

    # ============================================================
    # CHAT WIFI - adaptación gráfica del módulo original
    # ============================================================
    def _on_chat(self):
        self._add_log("Module CHAT WIFI selected")
        win=self._open_module_window("CHAT_WIFI","ULTRON — CHAT WIFI","940x650",(760,520))
        if win is None:return
        win.configure(bg=BG); win.transient(self.root)
        state={"server":None,"client":None,"clients":{},"running":False,"mode":None,"username":"","threads":[]}
        chat_lock=threading.Lock()
        username_var=tk.StringVar(value=socket.gethostname()[:12] or "Usuario")
        host_var=tk.StringVar(value="127.0.0.1"); port_var=tk.StringVar(value="5050"); message_var=tk.StringVar()
        status_var=tk.StringVar(value="● DESCONECTADO"); users_var=tk.StringVar(value="Usr: 0")
        if not HAS_CTK:
            self._show_module("CHAT WIFI","CustomTkinter no está disponible. Reinicia ULTRON con Python 3 del sistema."); return
        shell=ctk.CTkFrame(win,fg_color=BG,corner_radius=0); shell.pack(fill="both",expand=True,padx=18,pady=14)
        top=ctk.CTkFrame(shell,fg_color="transparent"); top.pack(fill="x",pady=(0,10))
        ctk.CTkLabel(top,text="Chat wifi",text_color=ORANGE,font=("monospace",24,"bold")).pack(side="right",padx=8)
        status_lbl=ctk.CTkLabel(top,textvariable=status_var,text_color=RED,font=("monospace",12,"bold")); status_lbl.pack(side="left",padx=8)
        stage=ctk.CTkFrame(shell,fg_color="transparent",corner_radius=0); stage.pack(fill="both",expand=True)
        setup=ctk.CTkFrame(stage,fg_color=BG_PANEL2,border_color=ORANGE_D,border_width=1,corner_radius=24); setup.pack(fill="both",expand=True,padx=24,pady=12)
        ctk.CTkLabel(setup,text="CONECTAR A CHAT LOCAL",text_color=ORANGE,font=("monospace",18,"bold")).pack(pady=(26,8))
        ctk.CTkLabel(setup,text="Crea un servidor o conéctate a otro equipo dentro de la misma red Wi-Fi.",text_color=TEXT_DIM,font=("monospace",12)).pack(pady=(0,18))
        form=ctk.CTkFrame(setup,fg_color="transparent"); form.pack(fill="x",padx=80,pady=(0,8))
        for ph,var in (("Nombre",username_var),("IP  xx.x.xxx.xx",host_var),("Puerto: XXXX",port_var)):
            ctk.CTkEntry(form,textvariable=var,placeholder_text=ph,fg_color=BG_PANEL,border_color=ORANGE_D,border_width=1,corner_radius=18,text_color=TEXT,height=40,font=("monospace",12)).pack(fill="x",pady=5)
        setup_buttons=ctk.CTkFrame(setup,fg_color="transparent",height=54); setup_buttons.pack(fill="x",padx=80,pady=(12,24),side="bottom"); setup_buttons.pack_propagate(False)
        chat=ctk.CTkFrame(stage,fg_color="transparent",corner_radius=0)
        users_bar=ctk.CTkFrame(chat,fg_color=BG_PANEL2,corner_radius=18,height=48); users_bar.pack(fill="x",pady=(0,8)); users_bar.pack_propagate(False)
        ctk.CTkLabel(users_bar,textvariable=users_var,text_color=TURQUOISE,font=("monospace",12,"bold")).pack(side="left",padx=16,pady=12)
        users_list=tk.Listbox(chat,bg=BG_PANEL2,fg=TEXT,font=self.font_small,relief=tk.FLAT,height=2,selectbackground=ORANGE_D,highlightthickness=0)
        messages=ctk.CTkTextbox(chat,fg_color=BG_PANEL2,border_color=ORANGE_D,border_width=1,corner_radius=22,text_color=TEXT,font=("monospace",12),wrap="word"); messages.pack(fill="both",expand=True,pady=8); messages.configure(state="disabled")
        bottom=ctk.CTkFrame(chat,fg_color="transparent"); bottom.pack(fill="x",pady=(8,0))
        entry=ctk.CTkEntry(bottom,textvariable=message_var,placeholder_text="Mensaje...",fg_color=BG_PANEL2,border_color=ORANGE_D,border_width=1,corner_radius=22,text_color=TEXT,height=46,font=("monospace",12)); entry.pack(side="left",fill="x",expand=True,padx=(0,8))
        def show_chat():
            setup.pack_forget(); chat.pack(fill="both",expand=True,padx=12,pady=4); entry.focus_set()
        def show_setup():
            chat.pack_forget(); setup.pack(fill="both",expand=True,padx=24,pady=12)
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
                    users_list.insert(tk.END, f"■ {name}")
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
            ui_log(f"■ {username} se conectó ({address[0]}).")
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
                ui_log(f"■ {username} se desconectó.")
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
                            ui_log("■ " + line[4:])
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

        # Botones redondeados del diseño Canva
        ctk.CTkButton(setup_buttons,text="Iniciar servidor",command=lambda:(start_server(), show_chat() if state["running"] else None),fg_color=BG_PANEL,border_color=GREEN,border_width=1,corner_radius=18,text_color=GREEN,height=42,font=("monospace",12,"bold")).pack(side="left",fill="x",expand=True,padx=(0,6))
        ctk.CTkButton(setup_buttons,text="Conectar",command=lambda:(connect_client(), show_chat() if state["running"] else None),fg_color=BG_PANEL,border_color=TURQUOISE,border_width=1,corner_radius=18,text_color=TURQUOISE,height=42,font=("monospace",12,"bold")).pack(side="right",fill="x",expand=True,padx=(6,0))
        ctk.CTkButton(bottom,text="➤",command=send_message,width=54,height=46,corner_radius=22,fg_color=ORANGE,hover_color=ORANGE_D,text_color=BG,font=("monospace",18,"bold")).pack(side="right")
        ctk.CTkButton(users_bar,text="Desconectar",command=lambda:(disconnect(),show_setup()),width=130,height=30,corner_radius=15,fg_color="transparent",border_color=RED,border_width=1,text_color=RED,font=("monospace",11,"bold")).pack(side="right",padx=10,pady=8)
        entry.bind("<Return>",lambda _e:send_message())
        def close_chat():
            disconnect(); win.destroy()
        win.protocol("WM_DELETE_WINDOW",close_chat)

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

        try:
            redraw=getattr(self,"_eye_redraw_theme",None)
            if redraw: redraw()
        except Exception:
            pass

        self.root.configure(bg=BG)
        self.root.update_idletasks()

    def _list_audio_sources(self):
        """Devuelve fuentes de audio visibles en PipeWire/PulseAudio."""
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
                cmd = ["parecord"]
                if device:
                    cmd.append(f"--device={device}")
                cmd.extend([
                    "--file-format=wav",
                    "--format=s16le",
                    "--rate=16000",
                    "--channels=1",
                    path
                ])

                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    text=True
                )

                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.terminate()
                    try:
                        proc.wait(timeout=1)
                    except subprocess.TimeoutExpired:
                        proc.kill()

                size = os.path.getsize(path) if os.path.exists(path) else 0
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
        """Genera una frase corta y la reproduce en la salida seleccionada."""
        def worker():
            try:
                espeak = shutil.which("espeak-ng") or shutil.which("espeak")
                paplay = shutil.which("paplay")

                if not espeak or not paplay:
                    raise RuntimeError(
                        "Falta espeak-ng/espeak o paplay."
                    )

                tmp = tempfile.NamedTemporaryFile(
                    prefix="ultron_voice_test_",
                    suffix=".wav",
                    delete=False
                )
                path = tmp.name
                tmp.close()

                subprocess.run(
                    [
                        espeak,
                        "-v", "es",
                        "-s", "150",
                        "-p", "42",
                        "-w", path,
                        "Sistema de audio de Ultron operativo."
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=20
                )

                device = self._resolve_output_device()
                cmd = ["paplay"]
                if device:
                    cmd.append(f"--device={device}")
                cmd.append(path)

                subprocess.run(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=20
                )
                msg = f"Prueba enviada a:\n{device or 'salida predeterminada'}"
            except Exception as exc:
                msg = f"Error probando salida de audio:\n{exc}"
            finally:
                try:
                    os.remove(path)
                except Exception:
                    pass

            self.root.after(
                0,
                lambda: self._show_module("PRUEBA DE VOZ", msg)
            )

        threading.Thread(target=worker, daemon=True).start()

    def _on_appearance(self):
        self._add_log("Module PREFERENCIAS selected")
        if not HAS_CTK:
            return self._on_appearance_legacy()
        win=self._open_module_window("PREFERENCIAS","ULTRON — PREFERENCIAS","980x680",(800,560))
        if win is None:return
        win.configure(bg=BG)
        shell=ctk.CTkFrame(win,fg_color=BG,corner_radius=0); shell.pack(fill="both",expand=True,padx=16,pady=12)
        head=ctk.CTkFrame(shell,fg_color="transparent"); head.pack(fill="x")
        ctk.CTkLabel(head,text="Preferencias",text_color=ORANGE,font=("monospace",25,"bold")).pack(side="left",padx=8)
        status=ctk.CTkLabel(head,text="● LIVE THEME ENGINE",text_color=TURQUOISE,font=("monospace",11,"bold")); status.pack(side="right",padx=8)
        ctk.CTkLabel(shell,text="APARIENCIAS PREDEFINIDAS",text_color=TEXT_DIM,font=("monospace",11,"bold"),anchor="w").pack(fill="x",padx=10,pady=(8,3))
        preset_scroll=ctk.CTkScrollableFrame(shell,orientation="horizontal",height=66,fg_color=BG_PANEL2,corner_radius=18,scrollbar_button_color=ORANGE_D); preset_scroll.pack(fill="x",padx=8,pady=(0,8))
        main=ctk.CTkFrame(shell,fg_color="transparent"); main.pack(fill="both",expand=True)
        controls=ctk.CTkScrollableFrame(main,fg_color=BG_PANEL2,border_color=ORANGE_D,border_width=1,corner_radius=22,width=430,scrollbar_button_color=ORANGE_D); controls.pack(side="left",fill="both",expand=True,padx=(8,6))
        preview_card=ctk.CTkFrame(main,fg_color=BG_PANEL2,border_color=TURQUOISE_D,border_width=1,corner_radius=22,width=400); preview_card.pack(side="right",fill="both",expand=True,padx=(6,8)); preview_card.pack_propagate(False)
        ctk.CTkLabel(preview_card,text="VISUALIZACIÓN",text_color=TURQUOISE,font=("monospace",15,"bold")).pack(anchor="w",padx=18,pady=(16,4))
        ctk.CTkLabel(preview_card,text="Vista previa del estilo ULTRON",text_color=TEXT_DIM,font=("monospace",10)).pack(anchor="w",padx=18)
        preview=tk.Canvas(preview_card,bg=BG,highlightthickness=0,bd=0)
        preview.pack(fill="both",expand=True,padx=14,pady=14)

        current=self._theme_dict_from_globals(); keys=[("Texto","TEXT"),("Color primario","PRIMARY"),("Color secundario","SECONDARY"),("Panel secundario","BG_PANEL2"),("Panel primario","BG_PANEL"),("Estado","GOOD"),("Color de fondo","BG"),("Alerta","DANGER")]; vars={k:tk.StringVar(value=current[k]) for _,k in keys}
        hidden={k:current[k] for k in ("PRIMARY_L","PRIMARY_D","PRIMARY_DIM","SECONDARY_D","SECONDARY_DIM","TEXT_DIM")}
        def safe_color(key,fallback):
            v=vars[key].get().strip() if key in vars else current.get(key,fallback)
            return v if re.match(r"^#[0-9a-fA-F]{6}$",v) else fallback

        def refresh_preview(*_):
            preview.delete("all")
            preview.update_idletasks()
            w = max(preview.winfo_width(), 300)
            h = max(preview.winfo_height(), 380)

            bg = safe_color("BG", BG)
            panel = safe_color("BG_PANEL", BG_PANEL)
            panel2 = safe_color("BG_PANEL2", BG_PANEL2)
            pri = safe_color("PRIMARY", ORANGE)
            pril = hidden["PRIMARY_L"]
            sec = safe_color("SECONDARY", TURQUOISE)
            text = safe_color("TEXT", TEXT)
            dim = hidden["TEXT_DIM"]
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
                fill=panel, outline=hidden["PRIMARY_DIM"], width=1
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
                "05  ALMACENAMIENTO",
                "06  HERRAMIENTAS",
            ]
            yy = 112
            for i, name in enumerate(module_names):
                preview.create_rectangle(
                    28, yy, left_w-10, yy+34,
                    fill=panel2,
                    outline=pri if i == 2 else hidden["PRIMARY_DIM"],
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

        def theme_from_vars():
            t=current.copy(); t.update({k:v.get() for k,v in vars.items()}); t.update(hidden); return t
        def repaint():
            refresh_preview()
        palette=["#FF5F1F","#FF003C","#FFD600","#39FF14","#00FF9D","#00FFFF","#00B8FF","#0066FF","#7C00FF","#B026FF","#FF00FF","#FF1493","#FFFFFF","#B0B7C3","#11151C","#05070A"]
        def choose(var,label):
            pop=ctk.CTkToplevel(win); pop.title("Color — "+label); pop.geometry("390x210"); pop.configure(fg_color=BG_PANEL); pop.transient(win)
            ctk.CTkLabel(pop,text=label.upper(),text_color=ORANGE,font=("monospace",13,"bold")).pack(anchor="w",padx=16,pady=10)
            grid=ctk.CTkFrame(pop,fg_color="transparent"); grid.pack(padx=12,pady=4)
            for i,col in enumerate(palette):
                ctk.CTkButton(grid,text="",fg_color=col,hover_color=col,width=38,height=32,corner_radius=10,command=lambda c=col:(var.set(c),repaint(),pop.destroy())).grid(row=i//8,column=i%8,padx=3,pady=3)
        ctk.CTkLabel(controls,text="PERSONALIZAR",text_color=ORANGE,font=("monospace",14,"bold")).pack(anchor="w",padx=14,pady=(12,7))
        for label,key in keys:
            row=ctk.CTkFrame(controls,fg_color=BG_PANEL,corner_radius=15,height=46); row.pack(fill="x",padx=10,pady=4); row.pack_propagate(False)
            ctk.CTkLabel(row,text=label,text_color=TEXT,font=("monospace",10,"bold")).pack(side="left",padx=12)
            sw=ctk.CTkButton(row,text="",width=36,height=28,corner_radius=10,fg_color=vars[key].get(),hover_color=vars[key].get(),command=lambda v=vars[key],l=label:choose(v,l)); sw.pack(side="right",padx=10)
            vars[key].trace_add("write",lambda *_a,w=sw,v=vars[key]:(w.configure(fg_color=v.get(),hover_color=v.get()),repaint()))
        def apply_preset(name):
            t=THEMES[name].copy(); self._apply_theme_live(t); save_theme_config({"theme":name}); status.configure(text="● "+name,text_color=t['SECONDARY']); self._add_log("Apariencia aplicada: "+name)
            for _,k in keys: vars[k].set(t[k])
            for k in hidden:hidden[k]=t[k]
            repaint()
        for name,t in THEMES.items():
            ctk.CTkButton(preset_scroll,text=name,command=lambda n=name:apply_preset(n),fg_color=t['BG_PANEL2'],hover_color=t['BG_PANEL'],border_color=t['PRIMARY'],border_width=1,corner_radius=16,text_color=t['PRIMARY'],font=("monospace",10,"bold"),width=145,height=40).pack(side="left",padx=5,pady=3)
        ctk.CTkLabel(controls,text="AUDIO",text_color=ORANGE,font=("monospace",14,"bold")).pack(anchor="w",padx=14,pady=(16,7))
        input_var=tk.StringVar(value=self.audio_input_device or "Automático"); output_var=tk.StringVar(value=self.audio_output_device or "Automático"); volume_var=tk.IntVar(value=self.ultron_volume)
        for label,var,vals in (("Entrada",input_var,["Automático"]+self._list_audio_sources()),("Salida",output_var,["Automático"]+self._list_audio_sinks())):
            ctk.CTkLabel(controls,text=label,text_color=TEXT_DIM,font=("monospace",10)).pack(anchor="w",padx=14); ctk.CTkOptionMenu(controls,variable=var,values=vals,fg_color=BG_PANEL,button_color=ORANGE_D,button_hover_color=ORANGE,text_color=TEXT,corner_radius=14).pack(fill="x",padx=12,pady=(2,7))
        ctk.CTkLabel(controls,text="Volumen ULTRON",text_color=TEXT_DIM,font=("monospace",10)).pack(anchor="w",padx=14); ctk.CTkSlider(controls,from_=10,to=100,variable=volume_var,progress_color=ORANGE,button_color=ORANGE).pack(fill="x",padx=14,pady=8)
        def save():
            self.audio_input_device=input_var.get(); self.audio_output_device=output_var.get(); self.ultron_volume=volume_var.get(); t=theme_from_vars(); save_theme_config({"theme":"CUSTOM","custom_theme":t}); self._apply_theme_live(t); status.configure(text="● GUARDADO",text_color=GREEN); self._add_log("Preferencias guardadas")
        ctk.CTkButton(controls,text="GUARDAR Y APLICAR",command=save,fg_color=ORANGE,hover_color=ORANGE_D,corner_radius=18,text_color=BG,font=("monospace",12,"bold"),height=44).pack(fill="x",padx=10,pady=(16,18))
        preview.bind("<Configure>", refresh_preview)
        repaint()

    def _on_appearance_legacy(self):
        self._add_log("Module PREFERENCIAS selected")

        win = self._open_module_window("PREFERENCIAS", "ULTRON — PREFERENCIAS", "980x680", (800, 560))
        if win is None:
            return
        win.configure(bg=BG)

        header = tk.Frame(win, bg=BG_PANEL2, height=48)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header, text="PREFERENCIAS   ↕ DESPLAZA PARA MÁS OPCIONES",
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
            width=22,
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
                pref_canvas.yview_scroll(int(-2 * (event.delta / 120)), "units")
            elif getattr(event, "num", None) == 4:
                pref_canvas.yview_scroll(-2, "units")
            elif getattr(event, "num", None) == 5:
                pref_canvas.yview_scroll(2, "units")

        def _bind_pref_scroll(_event=None):
            pref_canvas.bind_all("<MouseWheel>", _pref_mousewheel)
            pref_canvas.bind_all("<Button-4>", _pref_mousewheel)
            pref_canvas.bind_all("<Button-5>", _pref_mousewheel)

        def _unbind_pref_scroll(_event=None):
            pref_canvas.unbind_all("<MouseWheel>")
            pref_canvas.unbind_all("<Button-4>")
            pref_canvas.unbind_all("<Button-5>")

        # Toda la ventana de preferencias responde a la rueda.
        # La rueda funciona en toda Preferencias; así siempre se puede llegar a Texto, Audio y Guardar.
        _bind_pref_scroll()
        win.bind("<Destroy>", _unbind_pref_scroll, add="+")

        content = tk.Frame(body, bg=BG)
        content.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)

        controls = tk.Frame(content, bg=BG, width=500)
        controls.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))

        preview_side = tk.Frame(content, bg=BG_PANEL, width=360, height=500)
        preview_side.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        preview_side.pack_propagate(False)

        tk.Label(
            controls, text="APARIENCIAS PREDEFINIDAS",
            font=self.font_small, fg=TEXT_DIM, bg=BG
        ).pack(anchor="w", pady=(0, 6))

        preset_wrap = tk.Frame(controls, bg=BG)
        preset_wrap.pack(fill=tk.X, pady=(0, 4))
        preset_canvas = tk.Canvas(preset_wrap, bg=BG, highlightthickness=0, height=48)
        preset_scroll = tk.Scrollbar(preset_wrap, orient="horizontal", command=preset_canvas.xview,
                                     width=18, bg=BG_PANEL2, troughcolor=BG, activebackground=ORANGE_D)
        preset_frame = tk.Frame(preset_canvas, bg=BG)
        preset_canvas.create_window((0, 0), window=preset_frame, anchor="nw")
        preset_frame.bind("<Configure>", lambda e: preset_canvas.configure(scrollregion=preset_canvas.bbox("all")))
        preset_canvas.configure(xscrollcommand=preset_scroll.set)
        preset_canvas.pack(fill=tk.X)
        preset_scroll.pack(fill=tk.X)

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
                "05  ALMACENAMIENTO",
                "06  HERRAMIENTAS",
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
        win.after(100, _sync_pref_scrollregion)

        def apply_preset(name):
            theme = THEMES[name].copy()
            load_vars_from_theme(theme)
            self._apply_theme_live(theme)
            save_theme_config({"theme": name})
            self._add_log(f"Apariencia aplicada en vivo: {name}")
            status.configure(text=f"● {name} APLICADO", fg=TURQUOISE)

        for name in THEMES:
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
                padx=9,
                pady=7,
                command=lambda n=name: apply_preset(n)
            )
            btn.pack(side=tk.LEFT, padx=3, pady=4)

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
            ("Fondo principal", "BG"), ("Panel", "BG_PANEL"),
            ("Panel secundario", "BG_PANEL2"), ("Color primario", "PRIMARY"),
            ("Brillo primario", "PRIMARY_L"), ("Color secundario", "SECONDARY"),
            ("Texto", "TEXT"), ("Texto tenue", "TEXT_DIM"),
            ("Estado OK", "GOOD"), ("Alerta", "DANGER"),
        ]

        # Paleta amplia Cyberpunk + Neón, sin códigos repetidos.
        palette = [
            "#FF003C","#FF1744","#FF3131","#FF5F1F","#FF6D00","#FF9500","#FFB300","#FFD600",
            "#FFFF00","#CCFF00","#76FF03","#39FF14","#00FF66","#00FF9D","#00FFC8","#00FFFF",
            "#00E5FF","#00B8FF","#009DFF","#0066FF","#304FFE","#4D00FF","#651FFF","#7C00FF",
            "#9D00FF","#B026FF","#D500F9","#E100FF","#FF00FF","#FF00C8","#FF00A8","#FF1493",
            "#FF2D95","#FF4FA3","#FF6EC7","#F50057","#C51162","#AA00FF","#6200EA","#3D00A8",
            "#00F5D4","#00D9FF","#18FFFF","#64FFDA","#69F0AE","#B2FF59","#EEFF41","#FFFF8D",
            "#FF80AB","#EA80FC","#B388FF","#8C9EFF","#82B1FF","#80D8FF","#84FFFF","#A7FFEB",
            "#FF4081","#E040FB","#7C4DFF","#536DFE","#448AFF","#40C4FF","#00BFA5","#1DE9B6",
        ]
        neon_var = tk.BooleanVar(value=False)

        def neonize(color):
            # Aumenta saturación y brillo manteniendo el tono elegido.
            import colorsys
            h = color.lstrip("#")
            r,g,b = (int(h[i:i+2],16)/255 for i in (0,2,4))
            hh,ss,vv = colorsys.rgb_to_hsv(r,g,b)
            ss = max(.92, ss); vv = 1.0
            r,g,b = colorsys.hsv_to_rgb(hh,ss,vv)
            return "#%02X%02X%02X" % (int(r*255),int(g*255),int(b*255))

        def open_palette(var, label):
            pop = tk.Toplevel(win)
            pop.title(f"Color — {label}")
            pop.configure(bg=BG_PANEL)
            pop.resizable(False, False)
            pop.transient(win)
            tk.Label(pop, text=f"COLOR // {label.upper()}", font=self.font_small, fg=ORANGE, bg=BG_PANEL).grid(
                row=0, column=0, columnspan=8, sticky="w", padx=10, pady=10)
            def choose(color):
                var.set(neonize(color) if neon_var.get() else color)
                pop.destroy()
            for n,color in enumerate(palette):
                r,c=divmod(n,8)
                tk.Button(pop,bg=color,activebackground=color,width=4,height=2,relief=tk.FLAT,cursor="hand2",
                          command=lambda x=color: choose(x)).grid(row=r+1,column=c,padx=3,pady=3)
            tk.Checkbutton(pop,text="NEÓN",variable=neon_var,font=self.font_small,fg=TEXT,bg=BG_PANEL,
                           selectcolor=BG_PANEL2,activebackground=BG_PANEL,activeforeground=ORANGE).grid(
                               row=9,column=0,columnspan=8,sticky="w",padx=10,pady=(8,10))

        for i, (label, key) in enumerate(labels):
            tk.Label(grid, text=label, font=self.font_small, fg=TEXT_DIM, bg=BG,
                     width=18, anchor="w").grid(row=i, column=0, sticky="w", padx=(0,6), pady=4)
            swatch = tk.Button(grid, text="     ", bg=color_vars[key].get(), relief=tk.FLAT,
                               cursor="hand2", command=lambda v=color_vars[key], l=label: open_palette(v,l))
            swatch.grid(row=i, column=1, padx=4, pady=4, ipadx=8, ipady=4)
            tk.Button(grid, text="COLOR", font=self.font_small, fg=ORANGE, bg=BG_PANEL2,
                      activeforeground=ORANGE_L, activebackground=GRAY, relief=tk.FLAT, width=9,
                      command=lambda v=color_vars[key], l=label: open_palette(v,l)).grid(
                          row=i, column=2, padx=(6,0), pady=4)
            color_vars[key].trace_add("write", lambda *_a, b=swatch, v=color_vars[key]: b.configure(bg=v.get()))

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
            text="GUARDAR Y APLICAR",
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

    def _show_module(self, title, content):
        win = self._open_module_window(f"SHOW:{title}", f"ULTRON — {title}", "640x440")
        if win is None:
            return
        win.configure(bg=BG)

        header = tk.Frame(win, bg=BG_PANEL2, height=42)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(
            header, text=f"// {title}",
            font=self.font_title, fg=ORANGE, bg=BG_PANEL2
        ).pack(side=tk.LEFT, padx=16, pady=8)

        text_frame = tk.Frame(win, bg=BG)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        txt = tk.Text(
            text_frame, bg="#080808", fg=TEXT, font=self.font_mono,
            relief=tk.FLAT, padx=14, pady=12, wrap=tk.WORD
        )
        txt_scroll = tk.Scrollbar(
            text_frame,
            orient="vertical",
            command=txt.yview,
            bg=BG_PANEL2,
            troughcolor=BG,
            activebackground=ORANGE_D
        )
        txt.configure(yscrollcommand=txt_scroll.set)

        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        txt_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        txt.insert(tk.END, content)
        txt.configure(state=tk.DISABLED)

        btn_frame = tk.Frame(win, bg=BG)
        btn_frame.pack(fill=tk.X, pady=8)
        tk.Button(
            btn_frame, text="[ CERRAR ]", font=self.font_small,
            fg=ORANGE, bg=BG_PANEL2, relief=tk.FLAT,
            command=win.destroy, padx=18, pady=6
        ).pack()


if __name__ == "__main__":
    root = tk.Tk()
    app = UltronGUI(root)
    root.mainloop()
                     

