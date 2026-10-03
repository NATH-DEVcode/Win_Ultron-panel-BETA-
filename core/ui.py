from rich.console import Console, Group
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.tree import Tree
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeElapsedColumn
)
from rich import box

import json
import os
import time


console = Console()


CONFIG_FILE = "data/preferences.json"



DEFAULT_THEME = {

    "banner_logo": "#ff8800",
    "banner_subtitle": "#ffff00",

    "border": "#0066ff",
    "title": "#0066ff",

    "text": "#ffffff",
    "menu": "#ffffff",

    "success": "#00ff00",
    "warning": "#ffff00",
    "error": "#ff0000",
    "info": "#ffffff"

}



def clear():

    os.system("cls" if os.name == "nt" else "clear")



def load_preferences():

    if not os.path.exists(CONFIG_FILE):

        return {}


    try:

        with open(
            CONFIG_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)


    except:

        return {}



def load_theme():

    theme = DEFAULT_THEME.copy()

    preferences = load_preferences()

    colors = preferences.get(
        "colors",
        {}
    )

    theme.update(colors)

    return theme



def current_theme():

    preferences = load_preferences()

    return preferences.get(
        "theme",
        "Default"
    )



def color(name):

    theme = load_theme()

    return theme.get(
        name,
        "white"
    )



def banner():

    logo = r"""
██╗   ██╗██╗  ████████╗██████╗  ██████╗ ███╗   ██╗
██║   ██║██║  ╚══██╔══╝██╔══██╗██╔═══██╗████╗  ██║
██║   ██║██║     ██║   ██████╔╝██║   ██║██╔██╗ ██║
██║   ██║██║     ██║   ██╔══██╗██║   ██║██║╚██╗██║
╚██████╔╝███████╗██║   ██║  ██║╚██████╔╝██║ ╚████║
 ╚═════╝ ╚══════╝╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
"""


    subtitle = Text(
        f"by nath-dev\nTema: {current_theme()}",
        style=f"bold {color('banner_subtitle')}",
        justify="center"
    )


    content = Group(

        Text(
            logo,
            style=f"bold {color('banner_logo')}",
            justify="center"
        ),

        subtitle

    )


    console.print(

        Panel(

            Align.center(content),

            title=f"[bold {color('title')}]ULTRON PANEL[/]",

            border_style=color("border"),

            box=box.DOUBLE

        )

    )



def module_banner(name):

    console.print(

        Panel(

            Align.center(

                Text(
                    name.upper(),
                    style=f"bold {color('title')}"
                )

            ),

            border_style=color("border"),

            box=box.ROUNDED

        )

    )



def menu_box(menu, title="MENU"):

    console.print(

        Panel(

            Text(
                menu,
                style=color("menu")
            ),

            title=f"[bold {color('title')}]{title}[/]",

            border_style=color("border"),

            box=box.DOUBLE

        )

    )



def success(message):

    console.print(
        f"[bold {color('success')}]✔ {message}[/]"
    )



def error(message):

    console.print(
        f"[bold {color('error')}]✘ {message}[/]"
    )



def warning(message):

    console.print(
        f"[bold {color('warning')}]⚠ {message}[/]"
    )



def info(message):

    console.print(
        f"[bold {color('info')}]ℹ {message}[/]"
    )



def pause():

    Prompt.ask(
        f"[{color('menu')}]ENTER para continuar[/]",
        default=""
    )



def ask(question):

    return Prompt.ask(
        f"[bold {color('title')}]{question}[/]"
    )



def confirm(question):

    return Confirm.ask(
        f"[bold {color('title')}]{question}[/]"
    )



def table(title, columns, rows):

    tbl = Table(

        title=title,

        border_style=color("border"),

        box=box.ROUNDED

    )


    for column in columns:

        tbl.add_column(column)


    for row in rows:

        tbl.add_row(
            *[str(x) for x in row]
        )


    console.print(tbl)



def tree(title, items):

    root = Tree(title)


    for item in items:

        root.add(
            str(item)
        )


    console.print(root)



def loading(message="Cargando ULTRON...", seconds=2):

    with Progress(

        SpinnerColumn(),

        TextColumn(
            "{task.description}"
        ),

        BarColumn(),

        TimeElapsedColumn()

    ) as progress:


        task = progress.add_task(
            message,
            total=100
        )


        for _ in range(100):

            time.sleep(
                seconds / 100
            )

            progress.update(
                task,
                advance=1
            )
