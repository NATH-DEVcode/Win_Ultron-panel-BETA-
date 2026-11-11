import os
import sys
from pathlib import Path

def portable_root():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

ROOT = portable_root()
os.chdir(ROOT)

# Groq keys belong to each local user account and are configured by the GUI.
# Avoid prompting before login or persisting an unprotected portable.key file.

ffmpeg_dir = ROOT / "tools" / "ffmpeg"
if ffmpeg_dir.exists():
    os.environ["PATH"] = str(ffmpeg_dir) + os.pathsep + os.environ.get("PATH", "")

from launcher import main

if __name__ == "__main__":
    raise SystemExit(main())
