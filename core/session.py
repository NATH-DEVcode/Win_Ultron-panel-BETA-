from collections import deque


class Session:

    def __init__(self):

        # Guarda solo los últimos 10 mensajes
        self.history = deque(
            maxlen=10
        )


    def add(
        self,
        user,
        assistant
    ):

        self.history.append(
            {
                "user": user,
                "assistant": assistant
            }
        )


    def get_context(self):

        text = ""

        for item in self.history:

            text += (
                "Usuario: "
                + item["user"]
                + "\n"
            )

            text += (
                "ULTRON: "
                + item["assistant"]
                + "\n"
            )


        return text



    def clear(self):

        self.history.clear()



# Memoria activa mientras ULTRON está abierto

session = Session()
