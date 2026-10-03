from core.ui import banner, clear, menu_box
from core.startup import boot_sequence

from modules.ai import ai_menu
from modules.system import system_menu
from modules.preferences import preferences_menu
from modules.network import network_menu
from modules.security import security_menu
from modules.diagnostic import diagnostic_menu
from modules.status import status_menu
from modules.management import management_menu
from modules.chat import chat_menu


def check_navigation(option):

    if option == "00":
        return "home"

    if option.lower() in ["s", "salir"]:
        return "exit"

    return None


def main():

    boot_sequence()

    while True:

        clear()
        banner()

        menu = """
1. Conciencia
2. Gestion
3. Sistema
4. Red
5. Seguridad
6. Diagnostico
7. Preferencias
8. Estado de ULTRON
9. Chat local

0. Inicio
S. Salir
"""

        menu_box(
            menu,
            "ULTRON PANEL"
        )

        option = input("\nSeleccione una opcion: ")

        nav = check_navigation(option)

        if nav == "exit":

            clear()

            print("""
ULTRON:

Cerrando sistema...
""")

            break

        if nav == "home":
            continue

        result = None

        if option == "1":
            result = ai_menu()

        elif option == "2":
            result = management_menu()

        elif option == "3":
            result = system_menu()

        elif option == "4":
            result = network_menu()

        elif option == "5":
            result = security_menu()

        elif option == "6":
            result = diagnostic_menu()

        elif option == "7":
            result = preferences_menu()

        elif option == "8":
            result = status_menu()

        elif option == "9":

            result = chat_menu()

        else:

            print("""
ULTRON:

Opcion no valida.
""")

            input("\nENTER para continuar...")

        if result == "home":
            continue


if __name__ == "__main__":
    main()
