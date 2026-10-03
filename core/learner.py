import json
import os


FILE = "memory/skills.json"


def load_skills():

    os.makedirs(
        "memory",
        exist_ok=True
    )

    if not os.path.exists(FILE):

        return {}

    with open(FILE, "r") as f:
        return json.load(f)



def save_skills(data):

    os.makedirs(
        "memory",
        exist_ok=True
    )

    with open(FILE, "w") as f:

        json.dump(
            data,
            f,
            indent=4
        )



def remember_skill(name, target):

    data = load_skills()

    data[name.lower()] = target

    save_skills(data)



def find_skill(name):

    data = load_skills()

    return data.get(
        name.lower()
    )
