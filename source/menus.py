from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel

from source.order import Order
from source.widgets import Dialog


def get_user_menu(user):
    menu_type = [Technician, Bookkeeper, Administrator][user.Type - 1]
    return menu_type(user)


class Menu(QWidget):
    def __init__(self, user):
        super().__init__()
        self.exit_button = QPushButton('Выйти')
        header = QHBoxLayout()
        header.addWidget(self.exit_button)
        header.addWidget(QLabel(user.Name))
        QVBoxLayout(self)
        self.layout().addLayout(header)

    def add_service(self, name, widget):
        button = QPushButton(name)
        button.clicked.connect(Dialog(self, widget).show)
        self.layout().addWidget(button)


class Technician(Menu):
    def __init__(self, user):
        super().__init__(user)
        self.add_service('Формировать заказ', Order())


class Bookkeeper(Menu):
    def __init__(self, user):
        super().__init__(user)
        self.add_service('Формировать счет', QWidget())


class Administrator(Menu):
    def __init__(self, user):
        super().__init__(user)
        self.add_service('Смотреть историю входа', QWidget())
