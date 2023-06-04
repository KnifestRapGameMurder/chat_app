import sys
import json
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication
from connect_window import ConnectWindow
from main_window import MainWindow

import socket
import threading

import json_utils.json_keys as json_keys
import json_utils.message_types as message_types
import json_utils.error_types as error_types


ENCODING = "ascii"


class MySignal(QObject):
    message_sig = pyqtSignal(str)
    users_sig = pyqtSignal(list)


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
        self.main_window.setNickname(self.nickname)

        self.main_window.show()

        self.signal = MySignal()
        self.signal.message_sig.connect(self.main_window.addMessageToHistory)
        self.signal.users_sig.connect(self.main_window.setUsers)

        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

        self.main_window.setSendCallback(self.sendMessage)

        self.app.lastWindowClosed.connect(self.closeClient)

    def receive(self):
        while self.is_client_active:
            try:
                raw_message = self.client.recv(1024).decode(ENCODING)
                received = json.loads(raw_message)
                print(received[json_keys.TYPE])
                if received[json_keys.TYPE] == message_types.NAME_REQ:
                    self.client.send(
                        json.dumps(
                            {
                                json_keys.TYPE: message_types.NAME_RESP,
                                json_keys.NAME: self.nickname,
                            }
                        ).encode(ENCODING)
                    )
                elif received[json_keys.TYPE] == message_types.USERS:
                    users = received[json_keys.USERS]
                    # self.main_window.setUsers(users)
                    self.signal.users_sig.emit(users)
                else:
                    self.signal.message_sig.emit(raw_message)
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
