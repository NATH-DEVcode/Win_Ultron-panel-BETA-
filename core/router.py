from core.app_finder import launch_app
from skills.files import open_folder
from skills.system import system_action

from core.learner import find_skill

from core.system_admin import (
    list_processes,
    search_files,
    create_folder
)


def route(action):

    intent = action.get(
        "intent",
        ""
    )

    target = action.get(
        "target",
        ""
    ).lower()



    # ======================
    # ABRIR
    # ======================

    if intent == "open":


        # Revisar habilidades aprendidas

        learned = find_skill(
            target
        )

        if learned:

            target = learned



        # Carpetas

        result = open_folder(
            target
        )

        if result:

            return result



        # Sistema

        result = system_action(
            target
        )

        if result:

            return result



        # Aplicaciones

        result = launch_app(
            target
        )

        if result:

            return result



        return (
            "ULTRON:\n"
            "Eso aún no lo sé.\n"
            f"No encontré: {target}"
        )



    # ======================
    # CERRAR
    # ======================

    elif intent == "close":


        from core.executor import close_program


        if close_program(target):

            return (
                "ULTRON:\n"
                f"Cerrando {target}..."
            )


        return (
            "ULTRON:\n"
            "No encontré ese programa abierto."
        )



    # ======================
    # ADMINISTRADOR
    # ======================

    elif intent == "system":


        if "procesos" in target:

            return (
                "ULTRON:\n"
                +
                list_processes()
            )



        if target.startswith(
            "buscar "
        ):

            name = target.replace(
                "buscar ",
                ""
            )

            files = search_files(
                name
            )


            if files:

                return (
                    "ULTRON:\n"
                    +
                    "\n".join(files)
                )


            return (
                "ULTRON:\n"
                "No encontré archivos."
            )



        if target.startswith(
            "crear carpeta "
        ):

            name = target.replace(
                "crear carpeta ",
                ""
            )

            return create_folder(
                name
            )



    # ======================
    # PREGUNTAS IA
    # ======================

    elif intent == "answer":

        return (
            "ULTRON:\n"
            +
            action.get(
                "content",
                ""
            )
        )



    return (
        "ULTRON:\n"
        "Eso aún no lo sé."
    )
