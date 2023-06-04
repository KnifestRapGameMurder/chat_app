from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.size = QSize(800, 600)
        self.resize(self.size)
        self.setWindowTitle("Client")
        self.initUI()

    def initUI(self):
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        self.chat_history = QTextEdit(self.main_widget)
        self.chat_history.setGeometry(QRect(20, 20, 550, 450))
        self.chat_history.setReadOnly(True)
        self.chat_history.setPlaceholderText("Chat history...")

        self.input_field = QTextEdit(self.main_widget)
        self.input_field.setGeometry(QRect(20, 480, 450, 50))
        self.input_field.setPlaceholderText("Type here...")

        self.send_btn = QPushButton(self.main_widget)
        self.send_btn.setGeometry(QRect(480, 480, 90, 50))
        self.send_btn.setText("Send")
        self.send_btn.clicked.connect(self.onSendBtnClick)

    def setSendCallback(self, callback):
        self.sendCallback = callback

    def onSendBtnClick(self):
        message = self.input_field.toPlainText()
        self.sendCallback(message)
        self.input_field.clear()

    def addMessageToHistory(self, message):
        chat = self.chat_history.toPlainText()
        chat += "\n\n"
        chat += message
        self.chat_history.setText(chat)
