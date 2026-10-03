import json
import os

from core.ui import clear, pause


CONFIG_FILE = "data/preferences.json"



THEMES = {


    "1": {

        "name": "Default",

        "colors": {

            "banner_logo": "#ff8800",
            "banner_subtitle": "#ffff00",

            "border": "#0066ff",
            "title": "#0066ff",

            "text": "#ffffff",
            "menu": "#ffffff",

            "success": "#00ff00",
            "warning": "#ffff00",
            "error": "#ff0000",
            "info": "#ffffff"

        }

    },



    "2": {

        "name": "Nova Core",

        "colors": {

            "banner_logo": "#0088ff",
            "banner_subtitle": "#00ffff",

            "border": "#0055ff",
            "title": "#ffaa00",

            "text": "#ffffff",
            "menu": "#ffffff",

            "success": "#00ff88",
            "warning": "#ffff00",
            "error": "#ff3333",
            "info": "#00ffff"

        }

    },



    "3": {

        "name": "Hacker",

        "colors": {

            "banner_logo": "#00aa00",
            "banner_subtitle": "#00ff00",

            "border": "#008800",
            "title": "#00cc00",

            "text": "#aaaaaa",
            "menu": "#ffffff",

            "success": "#00ff00",
            "warning": "#ffff00",
            "error": "#ff0000",
            "info": "#ffffff"

        }

    },



    "4": {

        "name": "Jarvis",

        "colors": {

            "banner_logo": "#0088ff",
            "banner_subtitle": "#00ccff",

            "border": "#0044aa",
            "title": "#3399ff",

            "text": "#ffffff",
            "menu": "#eeeeee",

            "success": "#3399ff",
            "warning": "#ffaa00",
            "error": "#ff5555",
            "info": "#00ccff"

        }

    },



    "5": {

        "name": "Cyberpunk",

        "colors": {

            "banner_logo": "#ff00ff",
            "banner_subtitle": "#00ffff",

            "border": "#9900ff",
            "title": "#ffff00",

            "text": "#ffffff",
            "menu": "#00ffff",

            "success": "#00ff66",
            "warning": "#ffcc00",
            "error": "#ff0033",
            "info": "#00ffff"

        }

    },



    "6": {

        "name": "Matrix",

        "colors": {

            "banner_logo": "#00ff00",
            "banner_subtitle": "#66ff66",

            "border": "#008800",
            "title": "#00ff00",

            "text": "#00aa00",
            "menu": "#66ff66",

            "success": "#00ff00",
            "warning": "#ccff00",
            "error": "#ff4444",
            "info": "#66ff66"

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

    os.makedirs(
        "data",
        exist_ok=True
    )


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

            apply_theme(option)



def apply_theme(option):

    data = load_preferences()

    selected = THEMES[option]


    data["theme"] = selected["name"]

    data["colors"] = selected["colors"]


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
        f"Tema elegido: {selected['name']}"
    )


    pause()



def custom_menu():

    clear()


    print("""
========================
   PERSONALIZADO
========================

Próximamente:

- Banner
- Subtítulo
- Bordes
- Títulos
- Menú
- Mensajes

""")


    pause()
