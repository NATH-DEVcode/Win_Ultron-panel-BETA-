from core.ui import module_banner, menu_box, clear
from core.navigation import check_navigation
import subprocess


def run_command(command):

    try:
        result = subprocess.check_output(
            command,
            shell=True,
            text=True,
            stderr=subprocess.DEVNULL
        )

        return result.strip()

    except Exception:
        return "No disponible"



def tools_menu():

    while True:

        clear()

        module_banner("HERRAMIENTAS")


        menu = """
1. Ver herramientas instaladas
2. Buscar paquete
3. Actualizar lista de paquetes
4. Información de Python
5. Información de Kali

00. Inicio
0. Volver
"""


        menu_box(
            menu,
            "HERRAMIENTAS"
        )


        option = input(
            "\nSeleccione una opción: "
        )


        nav = check_navigation(option)


        if nav == "home":
            return "home"


        if nav == "back":
            return "back"



        elif option == "1":

            print("\nHerramientas disponibles:\n")

            print(
                run_command(
                    "which nmap sqlmap aircrack-ng hydra"
                )
            )

            input("\nENTER para continuar")



        elif option == "2":

            package = input(
                "\nNombre del paquete: "
            )

            print("\nBuscando paquete...\n")

            print(
                run_command(
                    f"apt-cache search {package}"
                )
            )

            input("\nENTER para continuar")



        elif option == "3":

            print(
                "\nActualizando lista de paquetes...\n"
            )

            print(
                run_command(
                    "sudo apt update"
                )
            )

            input("\nENTER para continuar")



        elif option == "4":

            print("\nPython:\n")

            print(
                run_command(
                    "python3 --version"
                )
            )

            input("\nENTER para continuar")



        elif option == "5":

            print("\nSistema:\n")

            print(
                run_command(
                    "cat /etc/os-release"
                )
            )

            input("\nENTER para continuar")



        else:

            print("\nOpción no válida")

            input(
                "\nENTER para continuar"
            )
