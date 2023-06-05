import socket
import threading

from json_utils.methods import *
import json_utils.json_keys as json_keys
import json_utils.message_types as message_types
import json_utils.error_types as error_types
import json_utils.success_types as success_types

SERVER = "127.0.0.1"
PORT = 55555
ADDRESS = (SERVER, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS)
server.listen()


class Message:
    def __init__(self):
        self.sender: User
        self.text = ""


class User:
    def __init__(self, client: socket.socket, nickname: str):
        self.client = client
        self.nickname = nickname


class ChatHistory:
    def __init__(self, users):
        self.users = users
        self.messages = []


class ServerApp:
    def __init__(self):
        self.users = []
        self.chat_histories = []
        self.receive()

    def receive(self):
        while True:
            client, address = server.accept()
            print("Connected with {}".format(str(address)))

            client.send(serialize({json_keys.TYPE: message_types.NAME_REQ}))

            try:
                response = deserialize(client.recv(1024))
                print(response[json_keys.TYPE])

                if response[json_keys.TYPE] == message_types.NAME_RESP:
                    nickname = response[json_keys.NAME]

                    if any(u.nickname == nickname for u in self.users):
                        client.send(
                            serialize(
                                {
                                    json_keys.TYPE: message_types.ERROR,
                                    json_keys.ERROR_TYPE: error_types.NAME_TAKEN,
                                }
                            )
                        )
                    else:
                        self.addUser(client, nickname)
                else:
                    print("Name expected, but wrong type received!")
            except:
                print("Client did not respond!")

    def addUser(self, userClient: socket.socket, userName: str):
        user = User(userClient, userName)

        user.client.send(
            serialize(
                {
                    json_keys.TYPE: message_types.SUCCESS,
                    json_keys.SUCCESS_TYPE: success_types.CONNECTED,
                }
            )
        )

        for u in self.users:
            chat = ChatHistory([u, user])

        self.users.append(user)
        print("Nickname is {}".format(userName))
        users_names = list(map(lambda u: u.nickname, self.users))

        self.broadcast(
            user,
            serialize(
                {
                    json_keys.TYPE: message_types.USERS,
                    json_keys.USERS: users_names,
                }
            ),
        )

        thread = threading.Thread(target=self.handle, args=(user,))
        thread.start()

    def handle(self, user: User):
        client = user.client
        nickname = user.nickname
        while True:
            try:
                recv = client.recv(1024)
                print(recv)
                received = deserialize(recv)
                print(received[json_keys.TYPE])

                # message = message.decode(ENCODING)
                # message = "{}: {}".format(user.nickname, message)
                # print(message)
                # message = message.encode(ENCODING)
                # self.broadcast(user, message)
            except:
                client.close()
                print("{} left!".format(nickname))
                self.users.remove(user)
                # self.broadcast(user, "{} left!".format(nickname).encode(ENCODING))
                break

    def broadcast(self, user: User, message: bytes):
        for u in self.users:
            u.client.send(message)


app = ServerApp()
