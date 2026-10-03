from rich.console import Console
from rich.panel import Panel

from core.settings import load_settings
from core.themes import load_theme


console = Console()


def dashboard():

    settings = load_settings()
    theme = load_theme(settings["theme"])

    console.clear()

    console.print(
        Panel(
            f"""
[bold]SISTEMA[/bold]

Usuario      : {settings.get("username", "Usuario")}
Tema         : {settings["theme"]}
Idioma       : {settings["language"]}

ULTRON PANEL funcionando correctamente.
            """,
            title="ULTRON PANEL",
            border_style=theme["border"]
        )
    )

    input("\nENTER para volver...")
