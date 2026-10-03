import os
import subprocess
import shutil


VAULT = os.path.expanduser(
    "~/.ultron_vault"
)


def init_vault():

    if not os.path.exists(VAULT):
        os.makedirs(VAULT)



def list_processes():

    try:

        result = subprocess.check_output(
            [
                "ps",
                "aux"
            ],
            text=True
        )

        return result

    except:

        return "No pude obtener procesos."



def search_files(name):

    found = []

    home = os.path.expanduser("~")


    for root, dirs, files in os.walk(home):

        for file in files:

            if name.lower() in file.lower():

                found.append(
                    os.path.join(
                        root,
                        file
                    )
                )


        if len(found) >= 20:
            break


    return found



def create_folder(name):

    path = os.path.expanduser(
        "~/" + name
    )

    os.makedirs(
        path,
        exist_ok=True
    )


    return (
        "ULTRON:\n"
        f"Carpeta creada: {name}"
    )



def move_safe(path):

    init_vault()


    if not os.path.exists(path):

        return (
            "ULTRON:\n"
            "No encontré ese archivo."
        )


    destination = os.path.join(
        VAULT,
        os.path.basename(path)
    )


    shutil.move(
        path,
        destination
    )


    return (
        "ULTRON:\n"
        "Archivo movido a zona segura."
    )
