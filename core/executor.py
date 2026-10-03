import os
import shutil
import subprocess
import webbrowser

from core.app_finder import launch_app

PROCESS_MAP = {
    "navegador": ["msedge.exe", "chrome.exe", "firefox.exe"],
    "firefox": ["firefox.exe"],
    "chrome": ["chrome.exe"],
    "edge": ["msedge.exe"],
    "terminal": ["WindowsTerminal.exe", "powershell.exe", "cmd.exe"],
    "whatsapp": ["WhatsApp.exe"],
    "editor": ["Code.exe", "notepad.exe"],
}

FOLDERS = {
    "descargas": "Downloads",
    "downloads": "Downloads",
    "documentos": "Documents",
    "imagenes": "Pictures",
    "fotos": "Pictures",
    "musica": "Music",
    "escritorio": "Desktop",
}

def close_program(name):
    targets = PROCESS_MAP.get((name or "").lower(), [name])
    closed = False
    for process in targets:
        process = str(process or "").strip()
        if not process:
            continue
        if not process.lower().endswith(".exe"):
            process += ".exe"
        result = subprocess.run(
            ["taskkill", "/IM", process, "/F"],
            capture_output=True,
            text=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if result.returncode == 0:
            closed = True
    return closed

def open_folder(folder):
    key = (folder or "").lower()
    relative = FOLDERS.get(key)
    if not relative:
        return False
    path = os.path.join(os.path.expanduser("~"), relative)
    try:
        os.startfile(path)
        return True
    except Exception:
        return False

def execute(action):
    intent = action.get("intent", "")
    target = action.get("target", "").lower()

    if intent == "open":
        if target in ["youtube", "yt"]:
            webbrowser.open("https://youtube.com")
            return "ULTRON:\nAbriendo YouTube..."
        if target in ["whatsapp", "whatsapp web", "wasap", "whats"]:
            webbrowser.open("https://web.whatsapp.com")
            return "ULTRON:\nAbriendo WhatsApp Web..."
        if target == "google":
            webbrowser.open("https://google.com")
            return "ULTRON:\nAbriendo Google..."
        if open_folder(target):
            return f"ULTRON:\nAbriendo {target}..."
        result = launch_app(target)
        if result:
            return result
        return "ULTRON:\nNo encontre esa aplicacion."

    if intent == "close":
        if close_program(target):
            return f"ULTRON:\nCerrando {target}..."
        return "ULTRON:\nNo encontre ese programa abierto."

    if intent == "answer":
        return "ULTRON:\n" + action.get("content", "")

    return "ULTRON:\nNecesito una habilidad nueva para eso."
