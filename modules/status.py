from datetime import datetime
import os

from core.identity import verify_identity


IDENTITY_FILE = ".ultron_identity"


def get_identity_data():

    if not os.path.exists(IDENTITY_FILE):
        return {}


    data = {}


    with open(
        IDENTITY_FILE,
        "r"
    ) as file:

        for line in file:

            if "=" in line:

                key, value = line.strip().split(
                    "=",
                    1
                )

                data[key] = value


    return data



def status_menu():

    identity = get_identity_data()


    estado = (
        "✓ Correcto"
        if verify_identity()
        else
        "✗ Error"
    )


    print("""
========================
     ULTRON STATUS
========================
""")


    print(
        f"Identidad: {estado}"
    )

    print(
        "Creador:",
        identity.get(
            "CREATOR",
            "Desconocido"
        )
    )


    print(
        "Proyecto:",
        identity.get(
            "PROJECT",
            "Desconocido"
        )
    )


    print(
        "Versión:",
        identity.get(
            "VERSION",
            "Desconocida"
        )
    )


    print(
        "Último chequeo:",
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )


    print(
        """
Estado:
✓ Núcleo cargado
✓ Módulos disponibles
"""
    )


    input(
        "\nENTER para volver"
    )

    return "home"
