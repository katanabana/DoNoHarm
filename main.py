import random
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QLineEdit, QPushButton, \
    QLabel
from sqlalchemy import select

from source.constants import PROJECT_NAME
from source.database import DB
from source.menus import get_user_menu
from source.widgets import Dialog


class Captcha(Dialog):
    def __init__(self):
        self.text = ''.join(random.choices('wertyuiofghjklcvbnm3456789', k=10))
        self.input = QLineEdit()
        self.button = QPushButton('Проверить')
        self.label = QLabel('Введите следующую капчу: ' + self.text)
        super().__init__(self.label, self.input, self.button)

    def validate(self):
        return self.input.text() == self.text


class LoginMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.errors = 0
        self.password = QLineEdit()
        self.login = QLineEdit()
        self.enter_button = QPushButton('Войти')
        self.captcha = Captcha()
        self.error = Dialog(self, QLabel('Неверные данные'))

        self.error.hide()
        self.captcha.button.clicked.connect(self.check_captcha)
        self.error.setWindowTitle(PROJECT_NAME)

        QVBoxLayout(self)
        self.layout().addWidget(QLabel('Логин:'))
        self.layout().addWidget(self.login)
        self.layout().addWidget(QLabel('Пароль:'))
        self.layout().addWidget(self.password)
        self.layout().addWidget(self.enter_button)

        technician_password = '4tzqHdkqzo4'
        technician_login = 'chacking0'

        administrator_password = 'Cbmj3Yi'
        administrator_login = 'srobken8'

        bookkeeper_password = 'ukM0e6'
        bookkeeper_login = 'nmably1'

        self.login.setText(bookkeeper_login)
        self.password.setText(bookkeeper_password)

    def get_user(self):
        password = self.password.text()
        login = self.login.text()
        session = DB.get_session()
        user = DB.tables.User
        query = select(user).where(user.Login == login, user.Password == password)
        user = session.scalar(query)
        if user is None:
            self.errors += 1
            if self.errors == 2:
                self.show_captcha()
        return user

    def show_captcha(self):
        self.captcha.show()
        self.enter_button.setDisabled(True)

    def check_captcha(self):
        if self.captcha.validate():
            self.enter_button.setDisabled(False)
            self.captcha.hide()
        else:
            sys.exit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(PROJECT_NAME)
        self.menu_manager = QStackedWidget()
        self.setCentralWidget(self.menu_manager)
        self.to_login_menu()

    def to_login_menu(self):
        menu = LoginMenu()
        menu.enter_button.clicked.connect(lambda: self.try_to_enter(menu.get_user()))
        self.change_menu(menu)

    def try_to_enter(self, user):
        self.menu_manager.currentWidget().error.hide()
        if user is not None:
            menu = get_user_menu(user)
            menu.exit_button.clicked.connect(self.to_login_menu)
            self.change_menu(menu)
        else:
            self.menu_manager.currentWidget().error.show()

    def change_menu(self, widget):
        current = self.menu_manager.currentWidget()
        self.menu_manager.removeWidget(current)
        self.menu_manager.addWidget(widget)
        self.menu_manager.setCurrentWidget(widget)


def hook(ex_type, exception, traceback):
    return sys.__excepthook__(ex_type, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    sys.excepthook = hook
    window = MainWindow()
    window.show()
    app.exec()
