import sys
from PyQt5.QtWidgets import QApplication
from connect_window import ConnectWindow

import socket
import threading


ENCODING = "ascii"


class ClientApp:
    def __init__(self):
        app = QApplication(sys.argv)
        connect_window = ConnectWindow()
        connect_window.setIP("127.0.0.1")
        connect_window.setConnectCallback(self.onConnect)

        connect_window.show()
        sys.exit(app.exec_())

    def onConnect(self, ip_address, nickname):
        self.nickname = nickname
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((ip_address, 55555))

        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

    def receive(self):
        while True:
            try:
                message = self.client.recv(1024).decode(ENCODING)
                if message == "NAME":
                    self.client.send(self.nickname.encode(ENCODING))
                else:
                    print(message)
            except:
                print("An error occured!")
                self.client.close()
                break


app = ClientApp()
#########################################

# import socket
# import threading
# import

# ENCODING = "ascii"

# nickname = input("Choose your nickname: ")

# client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client.connect(("127.0.0.1", 55555))


# def receive():
#     while True:
#         try:
#             message = client.recv(1024).decode(ENCODING)
#             if message == "NICK":
#                 client.send(nickname.encode(ENCODING))
#             else:
#                 print(message)
#         except:
#             print("An error occured!")
#             client.close()
#             break


# def write():
#     while True:
#         message = input("")
#         client.send(message.encode(ENCODING))


# receive_thread = threading.Thread(target=receive)
# receive_thread.start()

# write_thread = threading.Thread(target=write)
# write_thread.start()
