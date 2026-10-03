import json
import os
from datetime import datetime


MEMORY_FILE = "memory/data.json"


def load_memory():

    if not os.path.exists(MEMORY_FILE):

        return {
            "knowledge": {},
            "history": []
        }


    with open(MEMORY_FILE, "r") as file:

        return json.load(file)



def save_memory(data):

    os.makedirs(
        "memory",
        exist_ok=True
    )

    with open(
        MEMORY_FILE,
        "w"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )



def remember(key, value):

    data = load_memory()

    data["knowledge"][key] = value

    save_memory(data)



def recall(key):

    data = load_memory()

    return data["knowledge"].get(key)



def add_history(user, result):

    data = load_memory()

    data["history"].append(
        {
            "time": str(datetime.now()),
            "user": user,
            "result": result
        }
    )


    # Mantener solo las últimas 20 conversaciones

    data["history"] = data["history"][-20:]


    save_memory(data)



def get_history():

    data = load_memory()

    return data["history"]
