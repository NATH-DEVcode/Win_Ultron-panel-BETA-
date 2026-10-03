import json
import os


FILE = "memory/profile.json"


def load_profile():

    if not os.path.exists(FILE):

        return {
            "user": None
        }


    with open(FILE,"r") as f:
        return json.load(f)



def save_profile(name):

    os.makedirs(
        "memory",
        exist_ok=True
    )

    data = {
        "user": name
    }


    with open(FILE,"w") as f:
        json.dump(
            data,
            f,
            indent=4
        )



def get_user():

    return load_profile().get(
        "user"
    )
