import os
import sys
from pathlib import Path

def portable_root():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

ROOT = portable_root()
os.chdir(ROOT)

key_file = ROOT / "config" / "portable.key"
key = os.environ.get("GROQ_API_KEY", "").strip()

if not key and key_file.exists():
    key = key_file.read_text(encoding="utf-8").strip()

if not key:
    import tkinter as tk
    from tkinter import simpledialog
    prompt_root = tk.Tk()
    prompt_root.withdraw()
    key = (simpledialog.askstring("ULTRON", "Pega tu GROQ API Key (solo se pide la primera vez):", show="*") or "").strip()
    prompt_root.destroy()
    if key:
        key_file.parent.mkdir(parents=True, exist_ok=True)
        key_file.write_text(key, encoding="utf-8")

if key:
    os.environ["GROQ_API_KEY"] = key

ffmpeg_dir = ROOT / "tools" / "ffmpeg"
if ffmpeg_dir.exists():
    os.environ["PATH"] = str(ffmpeg_dir) + os.pathsep + os.environ.get("PATH", "")

from gui.ultron import main

if __name__ == "__main__":
    main()
