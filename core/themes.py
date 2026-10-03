import json
import os

THEMES_DIR = "themes"


def load_theme(theme_name):
    theme_file = os.path.join(THEMES_DIR, f"{theme_name}.json")

    if not os.path.exists(theme_file):
        theme_file = os.path.join(THEMES_DIR, "default.json")

    with open(theme_file, "r", encoding="utf-8") as file:
        return json.load(file)


def list_themes():
    themes = []

    for file in os.listdir(THEMES_DIR):
        if file.endswith(".json"):
            themes.append(file[:-5])

    themes.sort()
    return themes
