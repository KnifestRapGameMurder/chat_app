import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication
from connect_window import ConnectWindow
from main_window import MainWindow

import socket
import threading

from json_utils.methods import *
import json_utils.json_keys as json_keys
import json_utils.message_types as message_types
import json_utils.error_types as error_types
import json_utils.success_types as success_types


class MySignal(QObject):
    clear_chat_sig = pyqtSignal()
    message_sig = pyqtSignal(str)
    chats_sig = pyqtSignal(dict)
    connect_sig = pyqtSignal()


class ClientApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.connect_window = ConnectWindow()
        self.connect_window.setIP("127.0.0.1")
        self.connect_window.nickname_input.setText("Bohdan")
        self.connect_window.setConnectCallback(self.onConnect)
        self.is_client_active = False
        self.current_chat_id = ""
        self.chats = dict()

        self.connect_window.show()
        sys.exit(self.app.exec_())

    def onConnect(self, ip_address, nickname):
        if not self.is_client_active:
            self.nickname = nickname

            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((ip_address, 55555))

            self.is_client_active = True

            self.signal = MySignal()
            self.signal.connect_sig.connect(self.onConnected)

            receive_thread = threading.Thread(target=self.receive)
            receive_thread.start()

    def receive(self):
        while self.is_client_active:
            try:
                received = deserialize(self.client.recv(1024))
                recv_type = received[json_keys.TYPE]
                print(recv_type)

                if recv_type == message_types.ERROR:
                    if received[json_keys.ERROR_TYPE] == error_types.NAME_TAKEN:
                        self.onNameTakenError()
                elif recv_type == message_types.SUCCESS:
                    if received[json_keys.SUCCESS_TYPE] == success_types.CONNECTED:
                        self.signal.connect_sig.emit()
                if recv_type == message_types.NAME_REQ:
                    self.client.send(
                        serialize(
                            {
                                json_keys.TYPE: message_types.NAME_RESP,
                                json_keys.NAME: self.nickname,
                            }
                        )
                    )
                elif recv_type == message_types.CHATS:
                    chats = received[json_keys.CHATS]
                    print(chats)
                    self.chats = chats
                    self.current_chat_id = ""
                    self.signal.chats_sig.emit(chats)
                elif recv_type == message_types.DIRECT:
                    self.handleDirectMessage(received)
                else:
                    print("No specified action for: " + recv_type)
                    # self.signal.message_sig.emit(received)
            except:
                if self.is_client_active:
                    print("An error occured!")
                self.client.close()
                print("Connection closed!")
                break

    def onNameTakenError(self):
        self.client.close()
        self.is_client_active = False
        print("Name taken")

    def onConnected(self):
        self.connect_window.close()

        self.main_window = MainWindow()
        self.main_window.setNickname(self.nickname)
        self.main_window.setUserSelectCallback(self.onUserSelect)
        self.main_window.setSendCallback(self.sendMessage)

        self.signal.message_sig.connect(self.main_window.addMessageToHistory)
        self.signal.chats_sig.connect(self.main_window.setChats)
        self.signal.clear_chat_sig.connect(self.main_window.clearChat)
        self.main_window.show()
        self.app.lastWindowClosed.connect(self.closeClient)

    def onUserSelect(self, chat_id):
        print("Selected chat ID: " + chat_id)
        if chat_id != self.current_chat_id:
            self.signal.clear_chat_sig.emit()
            self.current_chat_id = chat_id

            self.client.send(
                serialize(
                    {
                        json_keys.TYPE: message_types.GET_CHAT,
                        json_keys.CHAT_ID: chat_id,
                    }
                )
            )

    def handleDirectMessage(self, received):
        if received[json_keys.CHAT_ID] == self.current_chat_id:
            message_obj = received[json_keys.MESSAGE]
            message = "{}: {}".format(message_obj["Sender"], message_obj["Text"])
            self.signal.message_sig.emit(message)

    def sendMessage(self, message):
        if self.current_chat_id != "":
            self.client.send(
                serialize(
                    {
                        json_keys.TYPE: message_types.DIRECT,
                        json_keys.CHAT_ID: self.current_chat_id,
                        json_keys.MESSAGE: message,
                    }
                )
            )

    def closeClient(self):
        self.is_client_active = False
        self.client.close()


app = ClientApp()
