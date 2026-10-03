import socket
import threading


HOST = "0.0.0.0"
PORT = 5050

COLORS = [
    "\033[31m",  # Rojo
    "\033[33m",  # Amarillo
    "\033[32m",  # Verde
    "\033[34m",  # Azul
    "\033[35m",  # Morado
    "\033[36m",  # Cian
]

RESET = "\033[0m"

SQUARE = "■"

clients = {}
color_index = 0
lock = threading.Lock()


def send_message(client, message):

    try:
        client.sendall(
            (message + "\n").encode("utf-8")
        )
        return True

    except:
        return False


def get_users():

    with lock:

        users = []

        for data in clients.values():

            users.append(
                (
                    data["username"],
                    data["color"]
                )
            )

        return users


def users_message():

    users = get_users()

    if not users:
        return "USERS:0"

    lines = [
        f"USERS:{len(users)}"
    ]

    for username, color in users:

        lines.append(
            f"USER:{username}"
        )

    return "\n".join(lines)


def broadcast(message, sender=None):

    with lock:

        for client in list(clients.keys()):

            if client == sender:
                continue

            send_message(
                client,
                message
            )


def broadcast_user_list():

    message = users_message()

    with lock:

        for client in list(clients.keys()):

            send_message(
                client,
                message
            )


def handle_client(
    client,
    address,
    username,
    color,
    square
):

    print(
        f"\n{color}{square}{RESET} "
        f"{username} se conectó."
    )

    broadcast(
        f"{color}{square}{RESET} "
        f"{username} se conectó.",
        client
    )

    broadcast_user_list()

    buffer = ""

    while True:

        try:

            data = client.recv(4096)

            if not data:
                break

            buffer += data.decode(
                "utf-8",
                errors="replace"
            )

            while "\n" in buffer:

                message, buffer = buffer.split(
                    "\n",
                    1
                )

                message = message.strip()

                if not message:
                    continue

                if message.lower() == "/exit":
                    return

                if message.lower() == "/users":

                    send_message(
                        client,
                        users_message()
                    )

                    continue

                formatted = (
                    f"{color}{square}{RESET} "
                    f"{username}: {message}"
                )

                print(
                    f"\n{formatted}"
                )

                broadcast(
                    formatted,
                    client
                )

        except:
            break

    with lock:

        clients.pop(
            client,
            None
        )

    try:
        client.close()
    except:
        pass

    print(
        f"\n{color}{square}{RESET} "
        f"{username} se desconectó."
    )

    broadcast(
        f"{color}{square}{RESET} "
        f"{username} se desconectó."
    )

    broadcast_user_list()


def server_input(
    username,
    color,
    square
):

    while True:

        try:

            message = input("> ")

            if message.lower() == "/exit":

                print(
                    "\nCerrando chat..."
                )

                return

            if message.lower() == "/users":

                users = get_users()

                print(
                    "\nUSUARIOS CONECTADOS:"
                )

                print(
                    "--------------------"
                )

                print(
                    f"{color}{square}{RESET} "
                    f"{username} (tu)"
                )

                for user, user_color in users:

                    if user != username:

                        print(
                            f"{user_color}{square}{RESET} "
                            f"{user}"
                        )

                print()

                continue

            if not message.strip():
                continue

            formatted = (
                f"{color}{square}{RESET} "
                f"{username}: {message}"
            )

            print(
                f"\n{formatted}"
            )

            broadcast(
                formatted
            )

        except KeyboardInterrupt:

            return

        except:

            return


def chat_server():

    global color_index

    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server.bind(
        (HOST, PORT)
    )

    server.listen(10)

    print("""
╔══════════════════════════════╗
║        ULTRON CHAT           ║
╠══════════════════════════════╣
║ SERVIDOR                     ║
║ Puerto: 5050                 ║
╚══════════════════════════════╝
""")

    username = input(
        "Nombre de usuario: "
    ).strip()

    if not username:

        username = "Usuario"

    color = COLORS[
        color_index % len(COLORS)
    ]

    square = SQUARE

    color_index += 1

    print(
        f"\n{color}{square}{RESET} "
        f"Tu usuario: {username}"
    )

    print(
        "\nEsperando usuarios..."
    )

    threading.Thread(
        target=server_input,
        args=(
            username,
            color,
            square
        ),
        daemon=True
    ).start()

    while True:

        try:

            client, address = server.accept()

            username_data = client.recv(
                1024
            )

            if not username_data:

                client.close()
                continue

            client_username = username_data.decode(
                "utf-8",
                errors="replace"
            ).strip()

            if not client_username:

                client_username = "Usuario"

            with lock:

                client_color = COLORS[
                    color_index % len(COLORS)
                ]

                color_index += 1

                clients[client] = {
                    "username": client_username,
                    "color": client_color
                }

            send_message(
                client,
                "READY"
            )

            threading.Thread(
                target=handle_client,
                args=(
                    client,
                    address,
                    client_username,
                    client_color,
                    square
                ),
                daemon=True
            ).start()

        except KeyboardInterrupt:

            break

        except Exception as error:

            print(
                f"\nError: {error}"
            )

    server.close()


def receive_client_messages(client):

    buffer = ""

    while True:

        try:

            data = client.recv(4096)

            if not data:
                break

            buffer += data.decode(
                "utf-8",
                errors="replace"
            )

            while "\n" in buffer:

                message, buffer = buffer.split(
                    "\n",
                    1
                )

                message = message.strip()

                if not message:
                    continue

                if message == "READY":
                    continue

                if message.startswith("USERS:"):

                    try:

                        count = int(
                            message.split(
                                ":",
                                1
                            )[1]
                        )

                        print(
                            f"\nUSUARIOS CONECTADOS: {count}"
                        )

                    except:
                        pass

                    continue

                if message.startswith("USER:"):

                    username = message.split(
                        ":",
                        1
                    )[1]

                    print(
                        f"  {SQUARE} {username}"
                    )

                    continue

                print(
                    f"\n{message}"
                )

                print(
                    "> ",
                    end="",
                    flush=True
                )

        except:

            break


def chat_client():

    print("""
╔══════════════════════════════╗
║        ULTRON CHAT           ║
╠══════════════════════════════╣
║ CLIENTE                      ║
╚══════════════════════════════╝
""")

    host = input(
        "IP del servidor [127.0.0.1]: "
    ).strip()

    if not host:

        host = "127.0.0.1"

    username = input(
        "Nombre de usuario: "
    ).strip()

    if not username:

        username = "Usuario"

    client = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    try:

        client.connect(
            (host, PORT)
        )

        send_message(
            client,
            username
        )

    except Exception as error:

        print(
            "\nNo se pudo conectar:"
        )

        print(error)

        input(
            "\nENTER para continuar..."
        )

        return "home"

    print(
        "\nConectado."
    )

    print(
        "Escribe /users para ver usuarios."
    )

    print(
        "Escribe /exit para salir.\n"
    )

    threading.Thread(
        target=receive_client_messages,
        args=(client,),
        daemon=True
    ).start()

    while True:

        try:

            message = input("> ")

            if message.lower() == "/exit":

                send_message(
                    client,
                    "/exit"
                )

                break

            if not message.strip():

                continue

            send_message(
                client,
                message
            )

        except KeyboardInterrupt:

            break

        except:

            break

    client.close()

    return "home"


def chat_menu():

    while True:

        print("""
╔══════════════════════════════╗
║        CHAT LOCAL            ║
╠══════════════════════════════╣
║ 1. Iniciar servidor          ║
║ 2. Conectar a servidor       ║
║ 0. Volver                    ║
╚══════════════════════════════╝
""")

        option = input(
            "Seleccione una opción: "
        )

        if option == "1":

            chat_server()

        elif option == "2":

            return chat_client()

        elif option == "0":

            return "home"

        else:

            print(
                "\nULTRON: Opción no válida."
            )

            input(
                "\nENTER para continuar..."
            )
