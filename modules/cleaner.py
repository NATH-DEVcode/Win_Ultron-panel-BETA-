import os
import shutil


VAULT = os.path.expanduser(
    "~/.ultron_vault"
)


def clean_file(path):

    os.makedirs(
        VAULT,
        exist_ok=True
    )


    if os.path.exists(path):

        shutil.move(
            path,
            VAULT
        )

        return (
            "ULTRON:\n"
            "Archivo movido a zona segura."
        )


    return (
        "ULTRON:\n"
        "Archivo no encontrado."
    )

