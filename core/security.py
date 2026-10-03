import os


DANGEROUS_ACTIONS = [
    "borrar",
    "eliminar",
    "rm",
    "apagar",
    "reiniciar",
    "formatear"
]


def needs_confirmation(command):

    command = command.lower()

    for action in DANGEROUS_ACTIONS:

        if action in command:

            return True

    return False



def ask_confirmation(action):

    print(
        "ULTRON:\n"
        f"Voy a ejecutar una acción importante: {action}"
    )

    answer = input(
        "¿Confirmas? (s/n): "
    )

    return answer.lower() == "s"



def safe_mode():

    return {
        "enabled": True,
        "message": "Modo seguro activo."
    }
