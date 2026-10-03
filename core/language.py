import json
import os


LANGUAGE_FOLDER = "data/languages"
CONFIG_FILE = "data/preferences.json"


current_language = "es"



def load_preferences():

    if not os.path.exists(CONFIG_FILE):

        return {}


    try:

        with open(
            CONFIG_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)


    except:

        return {}



def save_preferences(data):

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



def load_current_language():

    global current_language

    preferences = load_preferences()


    current_language = preferences.get(
        "language",
        "es"
    )


    return current_language



def set_language(language):

    global current_language

    current_language = language


    preferences = load_preferences()

    preferences["language"] = language


    save_preferences(
        preferences
    )



def get_language():

    return current_language



def load_language():

    path = os.path.join(
        LANGUAGE_FOLDER,
        f"{current_language}.json"
    )


    if not os.path.exists(path):

        return {}


    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)


    except:

        return {}



def translate(key):

    language = load_language()


    return language.get(
        key,
        key
    )


load_current_language()
