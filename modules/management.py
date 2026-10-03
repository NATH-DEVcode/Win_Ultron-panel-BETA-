from modules.packages import packages_menu
from modules.files import files_menu
from modules.tools import tools_menu


def management_menu():

    while True:

        print("""
╔══════════════════════════════╗
║          🧰 GESTIÓN          ║
╠══════════════════════════════╣
║ 1. 📦 Gestor de paquetes     ║
║ 2. 📁 Archivos               ║
║ 3. 🛠️ Herramientas           ║
║ 0. ← Volver                  ║
╚══════════════════════════════╝
""")

        option = input("\nSeleccione una opción: ")

        if option == "1":
            result = packages_menu()

        elif option == "2":
            result = files_menu()

        elif option == "3":
            result = tools_menu()

        elif option == "0":
            return "home"

        else:
            print("\nULTRON: Opción no válida.")
            input("\nENTER para continuar...")
            continue

        if result == "home":
            continue
