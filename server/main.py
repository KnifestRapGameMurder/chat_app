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


class User:
    def __init__(self, client: socket.socket, nickname: str):
        self.client = client
        self.nickname = nickname


class Message:
    def __init__(self, sender: User, text: str):
        self.sender = sender
        self.text = text


class ChatHistory:
    def __init__(self, users: list[User]):
        self.users = users
        self.messages = []


class ServerApp:
    def __init__(self):
        self.users = []
        self.last_chat_id = 0
        self.chat_histories = dict()
        self.users_chat_histories = dict()
        self.receive()

    def receive(self):
        while True:
            client, address = server.accept()
            print("Connected with {}".format(str(address)))

            client.send(serialize({json_keys.TYPE: message_types.NAME_REQ}))

            try:
                response = deserialize(client.recv(1024))

                if response[json_keys.TYPE] == message_types.NAME_RESP:
                    nickname = response[json_keys.NAME]

                    if any(u.nickname == nickname for u in self.users):
                        print(f"Join rejected: name '{nickname}' is already taken!")

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

        print(f"Joined successfuly: {userName}")

        user.client.send(
            serialize(
                {
                    json_keys.TYPE: message_types.SUCCESS,
                    json_keys.SUCCESS_TYPE: success_types.CONNECTED,
                }
            )
        )

        self.users_chat_histories[user] = dict()

        for u in self.users:
            chat = ChatHistory([u, user])
            self.chat_histories[self.last_chat_id] = chat

            print(f"New chat created: [ID: {self.last_chat_id}, Users:{[u, user]}]")

            self.users_chat_histories[user][self.last_chat_id] = chat
            self.users_chat_histories[u][self.last_chat_id] = chat

            self.last_chat_id += 1

        self.users.append(user)

        self.sendChats()

        thread = threading.Thread(target=self.handle, args=(user,))
        thread.start()

    def handle(self, user: User):
        client = user.client
        nickname = user.nickname
        print("Handling: " + nickname)
        while True:
            try:
                received = deserialize(client.recv(1024))
                recv_type = received[json_keys.TYPE]

                print(f"Requst from {nickname}: {recv_type}")

                if recv_type == message_types.GET_CHAT:
                    chat_id = received[json_keys.CHAT_ID]
                    print(f"- Chat ID: {chat_id}")

                    chat: ChatHistory = self.users_chat_histories[user][int(chat_id)]

                    for message in chat.messages:
                        print("- {}: {}".format(message.sender.nickname, message.text))

                        client.send(
                            serialize(
                                {
                                    json_keys.TYPE: message_types.DIRECT,
                                    json_keys.CHAT_ID: chat_id,
                                    json_keys.MESSAGE: {
                                        "Sender": message.sender.nickname,
                                        "Text": message.text,
                                    },
                                }
                            )
                        )

                elif recv_type == message_types.DIRECT:
                    chat_id = received[json_keys.CHAT_ID]
                    print(f"- Chat ID: {chat_id}")

                    message = received[json_keys.MESSAGE]
                    print(f"- {nickname}: {message}")

                    chat: ChatHistory = self.users_chat_histories[user][int(chat_id)]
                    chat.messages.append(Message(user, message))

                    data = serialize(
                        {
                            json_keys.TYPE: message_types.DIRECT,
                            json_keys.CHAT_ID: chat_id,
                            json_keys.MESSAGE: {
                                "Sender": nickname,
                                "Text": message,
                            },
                        }
                    )
                    for ch_u in chat.users:
                        ch_u.client.send(data)

            except:
                print(f"Connection with {nickname} closed!")
                client.close()
                self.users.remove(user)

                self.sendChats()

                break

    def sendChats(self):
        print("Updating chats...")

        for user in self.users:
            json_chats = dict()

            chats = self.users_chat_histories[user]
            for chat_id in chats:
                chat = chats[chat_id]
                if all(ch_u in self.users for ch_u in chat.users):
                    other_user_name = next(
                        ch_u.nickname
                        for ch_u in chats[chat_id].users
                        if ch_u is not user
                    )

                    json_chats[chat_id] = other_user_name

            print(f"Chats for {user.nickname}: {json_chats}")

            user.client.send(
                serialize(
                    {
                        json_keys.TYPE: message_types.CHATS,
                        json_keys.CHATS: json_chats,
                    }
                ),
            )

    def getChat(self, chat_id):
        return self.chat_histories[chat_id]


app = ServerApp()
