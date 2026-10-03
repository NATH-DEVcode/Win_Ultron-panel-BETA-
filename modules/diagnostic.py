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



def diagnostic_menu():

    while True:

        clear()

        module_banner("DIAGNOSTICO")


        menu = """
1. Información del procesador
2. Memoria RAM
3. Uso del disco
4. Procesos activos
5. Temperatura del sistema

00. Inicio
0. Volver
"""


        menu_box(
            menu,
            "DIAGNOSTICO"
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

            print("\nProcesador:\n")

            print(
                run_command(
                    "lscpu | grep 'Model name'"
                )
            )

            input("\nENTER para continuar")



        elif option == "2":

            print("\nMemoria RAM:\n")

            print(
                run_command(
                    "free -h"
                )
            )

            input("\nENTER para continuar")



        elif option == "3":

            print("\nUso del disco:\n")

            print(
                run_command(
                    "df -h"
                )
            )

            input("\nENTER para continuar")



        elif option == "4":

            print("\nProcesos activos:\n")

            print(
                run_command(
                    "ps aux --sort=-%cpu | head -15"
                )
            )

            input("\nENTER para continuar")



        elif option == "5":

            print("\nTemperatura:\n")

            print(
                run_command(
                    "sensors"
                )
            )

            input("\nENTER para continuar")



        else:

            print("\nOpción no válida")

            input(
                "\nENTER para continuar"
            )
