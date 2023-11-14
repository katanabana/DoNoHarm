from PyQt5.QtWidgets import QDialog, QVBoxLayout

from source.constants import PROJECT_NAME


class Dialog(QDialog):
    def __init__(self, *widgets):
        super().__init__()
        self.setWindowTitle(PROJECT_NAME)
        QVBoxLayout(self)
        for widget in widgets:
            self.layout().addWidget(widget)