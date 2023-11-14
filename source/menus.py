from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel


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

    def add_service(self, name):
        button = QPushButton(name)
        self.layout().addWidget(button)


class Technician(Menu):
    def __init__(self, user):
        super().__init__(user)
        self.add_service('Формировать отчет')


class Bookkeeper(Menu):
    def __init__(self, user):
        super().__init__(user)
        self.add_service('Формировать счет')


class Administrator(Menu):
    def __init__(self, user):
        super().__init__(user)
        self.add_service('Смотреть историю входа')
