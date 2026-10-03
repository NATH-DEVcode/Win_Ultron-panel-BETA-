import os
import shutil
import subprocess

ALIASES = {
    "calculadora": ["calc.exe"],
    "calculator": ["calc.exe"],
    "terminal": ["wt.exe", "powershell.exe", "cmd.exe"],
    "powershell": ["powershell.exe"],
    "bloc de notas": ["notepad.exe"],
    "notepad": ["notepad.exe"],
    "explorador": ["explorer.exe"],
    "explorer": ["explorer.exe"],
    "editor de texto": ["notepad.exe", "code.exe"],
    "navegador web": ["msedge.exe", "chrome.exe", "firefox.exe"],
    "chrome": ["chrome.exe"],
    "edge": ["msedge.exe"],
    "firefox": ["firefox.exe"],
    "code": ["code.exe"],
}

def _candidate_names(target):
    target = (target or "").strip().lower()
    return ALIASES.get(target, [target, target + ".exe"])

def search_app(target):
    for name in _candidate_names(target):
        found = shutil.which(name)
        if found:
            return found
    return None

def launch_app(target):
    app = search_app(target)
    if not app:
        return None
    try:
        subprocess.Popen(
            [app],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        return "ULTRON:\nAbriendo " + str(target) + "..."
    except Exception:
        return None
