import json
import os

CONFIG_FILE = "data/settings.json"

DEFAULT_CONFIG = {
    "theme": "default",
    "language": "es",
    "animations": True,
    "username": "",
    "version": "0.1.0"
}


def load_settings():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(CONFIG_FILE):
        save_settings(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_settings(settings):
    os.makedirs("data", exist_ok=True)

    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4, ensure_ascii=False)
