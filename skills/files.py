import os

FOLDERS = {
    "descargas": "Downloads",
    "downloads": "Downloads",
    "documentos": "Documents",
    "imagenes": "Pictures",
    "fotos": "Pictures",
    "musica": "Music",
    "escritorio": "Desktop",
    "inicio": "",
}

def open_folder(name):
    key = (name or "").lower()
    if key not in FOLDERS:
        return None
    path = os.path.join(os.path.expanduser("~"), FOLDERS[key])
    try:
        os.startfile(path)
        return f"ULTRON:\nAbriendo {key}..."
    except Exception:
        return None
