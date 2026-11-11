import os
import platform
import subprocess


def run_command(command):
    try:
        return subprocess.check_output(
            command,
            shell=False,
            text=True,
            stderr=subprocess.STDOUT,
            timeout=20,
        ).strip()
    except Exception as exc:
        return f"No disponible: {exc}"


IS_WINDOWS = os.name == "nt"


def get_ip():
    return run_command(["ipconfig"] if IS_WINDOWS else ["hostname", "-I"])


def get_interfaces():
    return run_command(
        ["netsh", "interface", "show", "interface"]
        if IS_WINDOWS else ["ip", "-brief", "address"]
    )


def scan_wifi():
    return run_command(
        ["netsh", "wlan", "show", "networks", "mode=bssid"]
        if IS_WINDOWS
        else ["nmcli", "device", "wifi", "list"]
    )


def connection_status():
    return run_command(
        ["netsh", "interface", "show", "interface"]
        if IS_WINDOWS else ["nmcli", "networking"]
    )


def network_info():
    return run_command(["ipconfig", "/all"] if IS_WINDOWS else ["ip", "address"])


def network_menu():
    from core.ui import module_banner, menu_box, clear
    from core.navigation import check_navigation

    actions = {
        "1": ("IP del equipo", get_ip),
        "2": ("Interfaces de red", get_interfaces),
        "3": ("Redes WiFi", scan_wifi),
        "4": ("Estado de conexión", connection_status),
        "5": ("Información de red", network_info),
    }

    while True:
        clear()
        module_banner("RED")
        menu_box(
            "1. Ver IP\n2. Ver interfaces de red\n3. Escanear redes WiFi"
            "\n4. Estado de conexión\n5. Información de red"
            "\n\n00. Inicio\n0. Volver",
            "RED",
        )
        option = input("\nSeleccione una opción: ")
        navigation = check_navigation(option)

        if navigation == "home":
            return "home"
        if navigation == "back":
            return "back"
        if option in actions:
            title, action = actions[option]
            print(f"\n{title}:\n\n{action()}")
            input("\nENTER para continuar")
