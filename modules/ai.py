from core.ultron import process
from core.ui import clear, banner


def ai_menu():

    while True:

        clear()

        banner()

        print("""
╔════════════════════════════╗
║        CONCIENCIA          ║
╚════════════════════════════╝

Escribe una orden.
Escribe "salir" para volver.

""")

        message = input("Tú: ")


        if message.lower() in [
            "salir",
            "exit",
            "0"
        ]:
            return "home"


        try:

            print("\nULTRON:")
            print("Orden recibida.")

            result = process(message)

            print(result)


        except Exception as e:

            print("\nULTRON:")
            print("Error al procesar la orden.")
            print(e)


        input("\nENTER para continuar")
