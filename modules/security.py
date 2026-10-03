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



def security_menu():

    while True:

        clear()

        module_banner("SEGURIDAD")


        menu = """
1. Ver puertos abiertos
2. Estado del firewall
3. Servicios activos
4. Procesos del sistema
5. Información de seguridad

00. Inicio
0. Volver
"""


        menu_box(
            menu,
            "SEGURIDAD"
        )


        option = input(
            "\nSeleccione una opción: "
        )


        nav = check_navigation(option)


        if nav == "home":
            return "home"


        if nav == "back":
            return "back"



        if option == "1":

            print(
                """
Puertos abiertos:

Analizando puertos del equipo...
"""
            )

            result = run_command(
                "ss -tuln"
            )

            print(result)

            input("\nENTER para continuar")



        elif option == "2":

            print(
                """
Estado del firewall:
"""
            )

            result = run_command(
                "systemctl status ufw --no-pager"
            )

            print(result)

            input("\nENTER para continuar")



        elif option == "3":

            print(
                """
Servicios activos:
"""
            )

            result = run_command(
                "systemctl --type=service --state=running"
            )

            print(result)

            input("\nENTER para continuar")



        elif option == "4":

            print(
                """
Procesos del sistema:
"""
            )

            result = run_command(
                "ps aux --sort=-%cpu | head -15"
            )

            print(result)

            input("\nENTER para continuar")



        elif option == "5":

            print(
                """
Información general:

Sistema:
"""
            )

            result = run_command(
                "uname -a"
            )

            print(result)

            input("\nENTER para continuar")



        else:

            print(
                "\nOpción no válida"
            )

            input(
                "\nENTER para continuar"
            )
