import platform
import time

import psutil

from core.ui import (
    clear,
    module_banner,
    menu_box,
    error,
    pause
)



def system_menu():

    while True:

        clear()

        module_banner(
            "Sistema"
        )


        menu = """
1. Información del sistema
2. Procesador
3. Memoria RAM
4. Almacenamiento

0. Volver al inicio
"""


        menu_box(
            menu,
            "SISTEMA"
        )


        option = input(
            "\nSeleccione una opción: "
        )


        if option == "0":

            return "home"


        elif option == "1":

            system_info()


        elif option == "2":

            cpu_info()


        elif option == "3":

            ram_info()


        elif option == "4":

            disk_info()


        else:

            error(
                "Opción no válida"
            )

            pause()



def system_info():

    clear()

    module_banner(
        "Información del sistema"
    )


    print(
        f"""
Sistema:
{platform.system()}

Versión:
{platform.release()}

Arquitectura:
{platform.machine()}

Equipo:
{platform.node()}

Tiempo activo:
{get_uptime()}
"""
    )


    pause()



def get_cpu_name():

    try:

        with open(
            "/proc/cpuinfo",
            "r"
        ) as file:

            for line in file:

                if "model name" in line:

                    return line.split(
                        ":",
                        1
                    )[1].strip()


    except:

        pass


    return (
        platform.processor()
        or
        "No detectado"
    )



def cpu_info():

    clear()

    module_banner(
        "Procesador"
    )


    cpu = get_cpu_name()


    print(
        f"""
Procesador:

{cpu}

Núcleos físicos:
{psutil.cpu_count(logical=False)}

Hilos:
{psutil.cpu_count(logical=True)}

Uso actual:
{psutil.cpu_percent()}%
"""
    )


    pause()



def ram_info():

    clear()

    module_banner(
        "Memoria RAM"
    )


    ram = psutil.virtual_memory()


    total = ram.total / (1024 ** 3)

    used = ram.used / (1024 ** 3)

    available = ram.available / (1024 ** 3)



    print(
        f"""
Memoria RAM:

RAM reconocida por Linux:
{total:.2f} GB

RAM usada:
{used:.2f} GB

RAM disponible:
{available:.2f} GB

Porcentaje usado:
{ram.percent}%


Nota:
Tu equipo puede tener memoria
reservada para hardware como la
gráfica integrada.
"""
    )


    pause()



def disk_info():

    clear()

    module_banner(
        "Almacenamiento"
    )


    disk = psutil.disk_usage("/")


    total = disk.total / (1024 ** 3)

    used = disk.used / (1024 ** 3)

    free = disk.free / (1024 ** 3)



    print(
        f"""
Almacenamiento:

Total:
{total:.2f} GB

Usado:
{used:.2f} GB

Libre:
{free:.2f} GB

Uso:
{disk.percent}%
"""
    )


    pause()



def get_uptime():

    seconds = int(
        time.time() - psutil.boot_time()
    )


    days = seconds // 86400

    hours = (
        seconds % 86400
    ) // 3600

    minutes = (
        seconds % 3600
    ) // 60


    return (
        f"{days} días, "
        f"{hours} horas, "
        f"{minutes} minutos"
    )
