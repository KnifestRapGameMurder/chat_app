import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class ConnectWindow(QMainWindow):
    def __init__(self):
        super(ConnectWindow, self).__init__()
        self.size = QSize(350, 250)
        self.resize(self.size)
        self.setWindowTitle("My Window")
        self.initUI()

    def setIP(self, ip_address):
        self.ip_address_input.setText(ip_address)

    def setConnectCallback(self, callback):
        self.connectCallback = callback

    def initUI(self):
        self.main_widget = QWidget(self)
        main_widget_offset = QPoint(30, 30)
        main_widget_margin = QSize(30, 30)
        main_widget_size = QRect(main_widget_offset, self.size - 2 * main_widget_margin)
        self.main_widget.setGeometry(main_widget_size)

        self.gridLayout_2 = QGridLayout(self.main_widget)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)

        self.gridLayout = QGridLayout()

        self.ip_address_input = QLineEdit(self.main_widget)
        self.ip_address_label = QLabel(self.main_widget)
        self.ip_address_label.setText("IP Address")
        self.gridLayout.addWidget(self.ip_address_input, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.ip_address_label, 0, 0, 1, 1)

        self.nickname_label = QLabel(self.main_widget)
        self.nickname_label.setText("Nickname")
        self.nickname_input = QLineEdit(self.main_widget)
        self.nickname_input.setFocus()
        self.gridLayout.addWidget(self.nickname_label, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.nickname_input, 1, 1, 1, 1)

        self.connect_btn = QPushButton(self.main_widget)
        self.connect_btn.setText("Connect")
        self.connect_btn.setStyleSheet("background-color: rgb(0, 255, 0);")

        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.connect_btn, 1, 0, 1, 1)

        self.connect_btn.clicked.connect(self.onConnectBtnClick)

    def onConnectBtnClick(self):
        ip_address = self.ip_address_input.text()
        nickname = self.nickname_input.text()
        self.connectCallback(ip_address, nickname)
