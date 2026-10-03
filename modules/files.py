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



def files_menu():

    while True:

        clear()

        module_banner("ARCHIVOS")


        menu = """
1. Ver espacio del disco
2. Buscar archivo
3. Listar carpeta actual
4. Información de almacenamiento

00. Inicio
0. Volver
"""


        menu_box(
            menu,
            "ARCHIVOS"
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

            print("\nEspacio del disco:\n")

            print(
                run_command("df -h")
            )

            input("\nENTER para continuar")



        elif option == "2":

            nombre = input(
                "\nNombre del archivo: "
            )

            print("\nBuscando...\n")

            print(
                run_command(
                    f"find ~ -name '{nombre}' 2>/dev/null"
                )
            )

            input("\nENTER para continuar")



        elif option == "3":

            print("\nContenido de la carpeta actual:\n")

            print(
                run_command("ls -lah")
            )

            input("\nENTER para continuar")



        elif option == "4":

            print("\nInformación de almacenamiento:\n")

            print(
                run_command("lsblk")
            )

            input("\nENTER para continuar")



        else:

            print("\nOpción no válida")

            input(
                "\nENTER para continuar"
            )
