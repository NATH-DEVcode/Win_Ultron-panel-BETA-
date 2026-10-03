import os
import time
from datetime import datetime

from core.identity import verify_identity
from core.user import get_username


LOG_FILE = "logs/startup.log"



def write_log(message):

    os.makedirs(
        "logs",
        exist_ok=True
    )


    with open(
        LOG_FILE,
        "a"
    ) as f:

        f.write(
            f"{datetime.now()} - {message}\n"
        )



def loading(text, delay=0.4):

    print(text)

    time.sleep(
        delay
    )



def boot_sequence():

    os.system(
        "cls" if os.name == "nt" else "cls" if os.name == "nt" else "clear"
    )


    print(r"""

â–ˆâ–ˆâ–ˆâ•—   â–ˆâ–ˆâ•— â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•— â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•—â–ˆâ–ˆâ•—  â–ˆâ–ˆâ•—
â–ˆâ–ˆâ–ˆâ–ˆâ•—  â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•—â•šâ•â•â–ˆâ–ˆâ•”â•â•â•â–ˆâ–ˆâ•‘  â–ˆâ–ˆâ•‘
â–ˆâ–ˆâ•”â–ˆâ–ˆâ•— â–ˆâ–ˆâ•‘â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ•‘
â–ˆâ–ˆâ•‘â•šâ–ˆâ–ˆâ•—â–ˆâ–ˆâ•‘â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•”â•â•â–ˆâ–ˆâ•‘
â–ˆâ–ˆâ•‘ â•šâ–ˆâ–ˆâ–ˆâ–ˆâ•‘â–ˆâ–ˆâ•‘  â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•‘   â–ˆâ–ˆâ•‘  â–ˆâ–ˆâ•‘
â•šâ•â•  â•šâ•â•â•â•â•šâ•â•  â•šâ•â•   â•šâ•â•   â•šâ•â•  â•šâ•â•

              nath-dev

""")


    print(
        "ULTRON:\n"
    )


    loading(
        "Inicializando nÃºcleo..."
    )


    print()


    if verify_identity():

        loading(
            "âœ“ Identidad verificada"
        )

        write_log(
            "Identidad OK"
        )


    else:

        loading(
            "âœ— Identidad fallida"
        )

        write_log(
            "Identidad ERROR"
        )



    username = get_username()


    loading(
        "âœ“ Sistema cargado"
    )


    loading(
        "âœ“ MÃ³dulos listos"
    )


    print(
        f"""
Sistema listo, {username}.
"""
    )


    write_log(
        f"Usuario activo: {username}"
    )


    time.sleep(
        2
    )


    return True

