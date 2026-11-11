"""Launcher with a visible error report for GUI starts without a console."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import os
import traceback


def _report_startup_error(exc: Exception) -> None:
    log_path = Path.home() / ".ultron" / "startup.log"
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(
                f"\n[{datetime.now().astimezone().isoformat()}] "
                "Error al iniciar ULTRON\n"
            )
            log_file.write("".join(traceback.format_exception(exc)))
        try:
            os.chmod(log_path.parent, 0o700)
            os.chmod(log_path, 0o600)
        except OSError:
            pass
    except OSError:
        log_path = Path("No se pudo escribir el registro de inicio")

    message = (
        f"ULTRON no pudo iniciar.\n\n{type(exc).__name__}: {exc}\n\n"
        f"Registro: {log_path}"
    )
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("ULTRON // ERROR DE INICIO", message, parent=root)
        root.destroy()
    except Exception:
        print(message)


def main() -> int:
    try:
        from gui.ultron import main as run_application
        run_application()
        return 0
    except Exception as exc:
        _report_startup_error(exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
