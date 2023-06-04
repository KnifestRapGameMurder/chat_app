import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication
from connect_window import ConnectWindow
from main_window import MainWindow

import socket
import threading


ENCODING = "ascii"


class MySignal(QObject):
    message_sig = pyqtSignal(str)


class ClientApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.connect_window = ConnectWindow()
        self.connect_window.setIP("127.0.0.1")
        self.connect_window.nickname_input.setText("Bohdan")
        self.connect_window.setConnectCallback(self.onConnect)

        self.connect_window.show()
        sys.exit(self.app.exec_())

    def onConnect(self, ip_address, nickname):
        self.connect_window.close()

        self.nickname = nickname
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((ip_address, 55555))

        self.is_client_active = True

        self.main_window = MainWindow()
        self.main_window.setWindowTitle("Client: " + self.nickname)
        self.main_window.show()

        self.signal = MySignal()
        self.signal.message_sig.connect(self.main_window.addMessageToHistory)

        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

        self.main_window.setSendCallback(self.sendMessage)

        self.app.lastWindowClosed.connect(self.closeClient)

    def receive(self):
        while self.is_client_active:
            try:
                message = self.client.recv(1024).decode(ENCODING)
                if message == "NAME":
                    self.client.send(self.nickname.encode(ENCODING))
                else:
                    self.signal.message_sig.emit(message)
            except:
                if self.is_client_active:
                    print("An error occured!")
                self.client.close()
                break

    def sendMessage(self, message):
        self.client.send(message.encode(ENCODING))

    def closeClient(self):
        self.is_client_active = False
        self.client.close()


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
