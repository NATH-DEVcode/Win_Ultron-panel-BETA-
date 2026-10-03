from core.brain import think
from core.router import route
from core.memory import add_history


def process(message):


    action = think(message)


    result = route(
        action
    )


    add_history(
        message,
        result
    )


    return result
