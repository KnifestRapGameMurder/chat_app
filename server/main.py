import socket
import threading

host = "127.0.0.1"
port = 55555

ENCODING = "ascii"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
nicknames = []


def broadcast(message):
    print(message.decode(ENCODING))
    for client in clients:
        client.send(message)


def handle(client):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast("{} left!".format(nickname).encode(ENCODING))
            nicknames.remove(nickname)
            break


def receive():
    while True:
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        client.send("NICK".encode(ENCODING))
        nickname = client.recv(1024).decode(ENCODING)
        nicknames.append(nickname)
        clients.append(client)

        print("Nickname is {}".format(nickname))
        broadcast("{} joined!".format(nickname).encode(ENCODING))
        client.send("Connected to server!".encode(ENCODING))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


receive()
