import json
import os

from core.ui import clear, pause


CONFIG_FILE = "data/preferences.json"



THEMES = {

    "1": {
        "name": "Default",
        "colors": {
            "banner": "blue",
            "title": "blue",
            "border": "blue",
            "text": "white",
            "menu": "white",
            "success": "green",
            "warning": "yellow",
            "error": "red",
            "info": "white"
        }
    },


    "2": {
        "name": "Nova Core",
        "colors": {
            "banner": "bright_blue",
            "title": "bright_blue",
            "border": "bright_cyan",
            "text": "grey70",
            "menu": "grey70",
            "success": "bright_green",
            "warning": "gold1",
            "error": "bright_red",
            "info": "bright_cyan"
        }
    },


    "3": {
        "name": "Hacker",
        "colors": {
            "banner": "green",
            "title": "green",
            "border": "green",
            "text": "grey70",
            "menu": "white",
            "success": "bright_green",
            "warning": "yellow",
            "error": "red",
            "info": "white"
        }
    },


    "4": {
        "name": "Jarvis",
        "colors": {
            "banner": "blue",
            "title": "blue",
            "border": "cyan",
            "text": "white",
            "menu": "white",
            "success": "bright_blue",
            "warning": "yellow",
            "error": "bright_red",
            "info": "bright_white"
        }
    },


    "5": {
        "name": "Cyberpunk",
        "colors": {
            "banner": "magenta",
            "title": "magenta",
            "border": "bright_magenta",
            "text": "purple",
            "menu": "white",
            "success": "bright_green",
            "warning": "bright_yellow",
            "error": "bright_red",
            "info": "bright_cyan"
        }
    },


    "6": {
        "name": "Matrix",
        "colors": {
            "banner": "green",
            "title": "green",
            "border": "bright_green",
            "text": "green",
            "menu": "bright_green",
            "success": "bright_green",
            "warning": "yellow",
            "error": "red",
            "info": "bright_green"
        }
    }

}



def load_preferences():

    if not os.path.exists(CONFIG_FILE):

        return {
            "theme": "Default",
            "colors": {}
        }


    try:

        with open(
            CONFIG_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)


    except:

        return {
            "theme": "Default",
            "colors": {}
        }



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



def appearance_menu():

    while True:

        clear()


        print("""
========================
      APARIENCIA
========================

1. Default
2. Nova Core
3. Hacker
4. Jarvis
5. Cyberpunk
6. Matrix

11. Personalizado

0. Volver
""")


        option = input(
            "Selecciona: "
        )


        if option == "0":

            return "home"



        if option in THEMES:

            set_theme(option)



        elif option == "11":

            custom_menu()



def set_theme(option):

    data = load_preferences()


    theme = THEMES[option]


    data["theme"] = theme["name"]

    data["colors"] = theme["colors"]


    save_preferences(
        data
    )


    clear()


    print("""
========================
     TEMA ELEGIDO
========================
""")


    print(
        "Tema elegido:",
        theme["name"]
    )


    pause()



def custom_menu():

    clear()


    print("""
========================
   PERSONALIZADO
========================

Próximamente podrás crear
tu propio tema.

""")


    pause()
