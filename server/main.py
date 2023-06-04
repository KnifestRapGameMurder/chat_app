import socket
import threading
import json

import json_utils.json_keys as json_keys
import json_utils.message_types as message_types
import json_utils.error_types as error_types

SERVER = "127.0.0.1"
PORT = 55555
ADDRESS = (SERVER, PORT)
ENCODING = "ascii"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS)
server.listen()

users = []


class User:
    def __init__(self, client: socket.socket, nickname: str):
        self.client = client
        self.nickname = nickname
        pass


def broadcast(user: User, message: str):
    for u in users:
        u.client.send(message)


def handle(user: User):
    client = user.client
    nickname = user.nickname
    while True:
        try:
            message = client.recv(1024)
            message = message.decode(ENCODING)
            message = "{}: {}".format(user.nickname, message)
            print(message)
            message = message.encode(ENCODING)
            broadcast(user, message)
        except:
            client.close()
            print("{} left!".format(nickname))
            users.remove(user)
            broadcast(user, "{} left!".format(nickname).encode(ENCODING))
            break


def receive():
    while True:
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        client.send(
            json.dumps({json_keys.TYPE: message_types.NAME_REQ}).encode(ENCODING)
        )

        try:
            raw_message = client.recv(1024).decode(ENCODING)
            response = json.loads(raw_message)
            
            if response[json_keys.TYPE] == message_types.NAME_RESP:
                nickname = response[json_keys.NAME]

                if any(u.nickname == nickname for u in users):
                    client.send(
                        json.dumps(
                            {
                                json_keys.TYPE: message_types.ERROR,
                                json_keys.ERROR_TYPE: error_types.NAME_TAKEN,
                            }
                        ).encode(ENCODING)
                    )
                else:
                    user = User(client, nickname)
                    users.append(user)

                    print("Nickname is {}".format(nickname))

                    users_names = list(map(lambda u: u.nickname, users))
                    broadcast(
                        user,
                        json.dumps(
                            {
                                json_keys.TYPE: message_types.USERS,
                                json_keys.USERS: users_names,
                            }
                        ).encode(ENCODING),
                    )

                    thread = threading.Thread(target=handle, args=(user,))
                    thread.start()
            else:
                print("Name expected, but wrong type received!")
        except:
            print("Client did not respond!")


receive()
