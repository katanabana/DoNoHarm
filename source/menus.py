from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel

from source.check import Check
from source.order import Order
from source.widgets import Dialog, Table, EditTable, ScrollDialog


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

    def add_service(self, name, widget, dialog_type=Dialog):
        button = QPushButton(name)
        button.clicked.connect(dialog_type(self, widget).show)
        self.layout().addWidget(button)


class Technician(Menu):
    def __init__(self, user):
        super().__init__(user)
        self.add_service('Формировать заказ', Order())
        self.add_service('Редактировать клиента', EditTable('Client', 'Email', 'Phone'))


class Bookkeeper(Menu):
    def __init__(self, user):
        super().__init__(user)
        self.add_service('Формировать счет', Check())


class Administrator(Menu):
    def __init__(self, user):
        super().__init__(user)
        self.add_service('Смотреть историю входа', Table('User'))
