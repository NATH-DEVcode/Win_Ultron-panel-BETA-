from core.ui import module_banner, menu_box, clear
from core.navigation import check_navigation
import subprocess


def run_command(command):

    try:
        return subprocess.check_output(
            command,
            shell=True,
            text=True,
            stderr=subprocess.DEVNULL
        ).strip()

    except Exception:

        return "No disponible"



def packages_menu():

    while True:

        clear()

        module_banner("GESTOR DE PAQUETES")


        menu = """
1. Buscar paquete
2. Ver paquetes instalados
3. Actualizar repositorios
4. Actualizar sistema
5. Limpiar paquetes

00. Inicio
0. Volver
"""


        menu_box(
            menu,
            "GESTOR DE PAQUETES"
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

            name = input(
                "\nNombre del paquete: "
            )

            print("\nBuscando...\n")

            print(
                run_command(
                    f"apt-cache search {name}"
                )
            )

            input("\nENTER para continuar")



        elif option == "2":

            print(
                "\nPaquetes instalados:\n"
            )

            print(
                run_command(
                    "apt list --installed"
                )
            )

            input("\nENTER para continuar")



        elif option == "3":

            print(
                "\nActualizando repositorios...\n"
            )

            print(
                run_command(
                    "sudo apt update"
                )
            )

            input("\nENTER para continuar")



        elif option == "4":

            print(
                "\nActualizando sistema...\n"
            )

            print(
                run_command(
                    "sudo apt upgrade"
                )
            )

            input("\nENTER para continuar")



        elif option == "5":

            print(
                "\nLimpiando paquetes...\n"
            )

            print(
                run_command(
                    "sudo apt autoremove"
                )
            )

            input("\nENTER para continuar")



        else:

            print(
                "\nOpción no válida"
            )

            input(
                "\nENTER para continuar"
            )
