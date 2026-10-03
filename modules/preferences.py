from core.theme import appearance_menu
from core.language import set_language, get_language
from core.ui import clear



LANGUAGES = {

    "1": ("Español", "es"),
    "2": ("English", "en"),
    "3": ("Français", "fr"),
    "4": ("Deutsch", "de"),
    "5": ("Italiano", "it"),
    "6": ("Português", "pt"),
    "7": ("日本語", "ja"),
    "8": ("한국어", "ko"),
    "9": ("中文", "zh"),
    "10": ("Русский", "ru"),
    "11": ("العربية", "ar"),
    "12": ("हिन्दी", "hi"),
    "13": ("Nederlands", "nl"),
    "14": ("Polski", "pl"),
    "15": ("Türkçe", "tr"),
    "16": ("Svenska", "sv"),
    "17": ("Dansk", "da"),
    "18": ("Norsk", "no"),
    "19": ("Suomi", "fi"),
    "20": ("Ελληνικά", "el")

}



def language_menu():

    while True:

        clear()


        print("""
========================
        IDIOMAS
========================
""")


        print(
            "Idioma actual:",
            get_language()
        )


        print()


        for number, data in LANGUAGES.items():

            print(
                f"{number}. {data[0]}"
            )


        print("""
0. Volver
""")


        option = input(
            "Selecciona idioma: "
        )


        if option == "0":

            return "home"



        if option in LANGUAGES:

            name, code = LANGUAGES[option]


            set_language(code)


            clear()


            print("""
========================
     IDIOMA CAMBIADO
========================
""")


            print(
                "Nuevo idioma:",
                name
            )


            input(
                "\nENTER para continuar"
            )



def preferences_menu():

    while True:

        clear()


        print("""
========================
    PREFERENCIAS
========================

1. Apariencia
2. Idioma

0. Volver
""")


        option = input(
            "Selecciona: "
        )



        if option == "0":

            return "home"



        elif option == "1":

            result = appearance_menu()


            if result == "home":

                continue



        elif option == "2":

            result = language_menu()


            if result == "home":

                continue



        else:

            print(
                "\nOpción no válida"
            )


            input(
                "\nENTER para continuar"
            )
