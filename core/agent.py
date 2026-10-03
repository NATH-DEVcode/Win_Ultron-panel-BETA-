import os
import shutil
from core.learner import remember_skill


VAULT = os.path.expanduser(
    "~/.ultron_vault"
)


def init_agent():

    if not os.path.exists(VAULT):
        os.makedirs(VAULT)



def move_to_vault(path):

    init_agent()

    if not os.path.exists(path):
        return "Archivo no encontrado."


    name = os.path.basename(path)

    destination = os.path.join(
        VAULT,
        name
    )


    shutil.move(
        path,
        destination
    )


    return (
        "ULTRON:\n"
        f"Movido a zona segura: {name}"
    )



def learn(command, target):

    remember_skill(
        command,
        target
    )


    return (
        "ULTRON:\n"
        "Nueva habilidad guardada."
    )
