import socket
import threading

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

        client.send("NAME".encode(ENCODING))
        nickname = client.recv(1024).decode(ENCODING)
        user = User(client, nickname)
        users.append(user)

        print("Nickname is {}".format(nickname))
        broadcast(user, "{} joined!".format(nickname).encode(ENCODING))

        thread = threading.Thread(target=handle, args=(user,))
        thread.start()


receive()
