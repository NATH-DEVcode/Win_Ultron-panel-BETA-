import subprocess

def system_action(target):
    target = (target or "").lower()

    if target in ["apagar", "apaga"]:
        return "ULTRON:\nConfirmacion necesaria para apagar."

    if target in ["reiniciar", "reinicio"]:
        return "ULTRON:\nConfirmacion necesaria para reiniciar."

    if target == "terminal":
        try:
            subprocess.Popen(["powershell.exe"], creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0))
            return "ULTRON:\nAbriendo terminal..."
        except Exception:
            return "ULTRON:\nNo pude abrir la terminal."

    return None
