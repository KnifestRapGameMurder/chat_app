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
        self.user_btns = []

    def initUI(self):
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)

        self.horizontalLayout_2 = QHBoxLayout(self.centralwidget)

        self.left_side = QWidget(self.centralwidget)

        self.verticalLayout = QVBoxLayout(self.left_side)
        self.chat_history = QTextEdit(self.left_side)
        self.chat_history.setReadOnly(True)
        self.chat_history.setPlaceholderText("Chat history...")

        self.verticalLayout.addWidget(self.chat_history)

        self.message_area = QWidget(self.left_side)

        self.message_area.setMaximumSize(QSize(16777215, 50))
        self.horizontalLayout_3 = QHBoxLayout(self.message_area)
        self.horizontalLayout_3.setSpacing(5)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)

        self.input_field = QTextEdit(self.message_area)
        self.input_field.setMinimumSize(QSize(0, 50))
        self.input_field.setPlaceholderText("Type here...")
        self.horizontalLayout_3.addWidget(self.input_field)

        self.send_btn = QPushButton(self.message_area)
        self.send_btn.setMinimumSize(QSize(100, 50))
        self.send_btn.setText("Send")
        self.send_btn.clicked.connect(self.onSendBtnClick)

        self.horizontalLayout_3.addWidget(self.send_btn)

        self.verticalLayout.addWidget(self.message_area)

        self.horizontalLayout_2.addWidget(self.left_side)

        self.right_side = QWidget(self.centralwidget)
        self.right_side.setMaximumSize(QSize(200, 16777215))
        self.verticalLayout_2 = QVBoxLayout(self.right_side)
        self.nickname_field = QLineEdit(self.right_side)
        self.nickname_field.setMinimumSize(QSize(100, 50))
        font = QFont()
        font.setPointSize(12)
        self.nickname_field.setFont(font)

        self.verticalLayout_2.addWidget(self.nickname_field)

        self.users_area = QScrollArea(self.right_side)
        self.users_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.users_area.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.users_area.setWidgetResizable(True)
        self.users_container = QWidget()
        self.users_container.setGeometry(QRect(0, 0, 176, 446))
        self.verticalLayout_3 = QVBoxLayout(self.users_container)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)

        # self.user_btn = QPushButton(self.users_container)
        # self.user_btn.setMinimumSize(0, 50)
        # self.user_btn.setText("No users online")
        # self.verticalLayout_3.addWidget(self.user_btn)

        self.verticalSpacer = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding
        )
        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.users_area.setWidget(self.users_container)

        self.verticalLayout_2.addWidget(self.users_area)

        self.horizontalLayout_2.addWidget(self.right_side)

    def setNickname(self, nickname):
        self.nickname = nickname
        self.setWindowTitle("Client: " + nickname)
        self.nickname_field.setText(nickname)

    def setSendCallback(self, callback):
        self.sendCallback = callback

    def onSendBtnClick(self):
        message = self.input_field.toPlainText()
        if len(message) > 0:
            self.sendCallback(message)
            self.input_field.clear()

    def setUsers(self, users: list):
        print(users)
        
        for user_btn in self.user_btns:
            user_btn.destroy()

        self.user_btns.clear()

        for user in users:
            if user != self.nickname:
                user_btn = QPushButton(self.users_container)
                user_btn.setMinimumSize(0, 50)
                user_btn.setText(user)
                userName = user
                user_btn.clicked.connect(lambda: self.onUserBtnClick(userName))
                self.verticalLayout_3.addWidget(user_btn)
                self.user_btns.append(user_btn)

        self.verticalLayout_3.removeItem(self.verticalSpacer)
        self.verticalLayout_3.addItem(self.verticalSpacer)

    def setUserSelectCallback(self, callback):
        self.userSelectCallback = callback

    def onUserBtnClick(self, userName: str):
        self.userSelectCallback(userName)

    def addMessageToHistory(self, message):
        chat = self.chat_history.toPlainText()
        chat += "\n\n"
        chat += message
        self.chat_history.setText(chat)
