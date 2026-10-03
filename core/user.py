import json
import os


CONFIG_FILE = "data/settings.json"



def load_settings():

    if not os.path.exists(CONFIG_FILE):

        return {}


    with open(
        CONFIG_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)



def save_settings(data):

    with open(
        CONFIG_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )



def get_username():

    settings = load_settings()

    username = settings.get(
        "username",
        ""
    )


    if username.strip():

        return username


    print(
        "\nUsuario nuevo detectado.\n"
    )


    username = input(
        "Nombre de usuario: "
    )


    settings["username"] = username


    save_settings(
        settings
    )


    return username
