import datetime

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSpinBox, QPushButton, QLabel, QFileDialog
from reportlab.pdfgen.canvas import Canvas

from source.database import DB
from source.widgets import Dialog, Table, AddInstance


def timestamp_to_date(timestamp):
    timedelta = datetime.timedelta(seconds=timestamp // 10000)
    start = datetime.date(1970, 1, 1)
    return start + timedelta


class Form(Dialog):
    def __init__(self, parent, order_id):
        self.id = order_id
        self.client_table = Table('Client')
        self.add_client_button = QPushButton('Добавить клиента')
        self.service_table = Table('Service')
        self.button = QPushButton('Формировать')
        super().__init__(
            parent, self.client_table, self.add_client_button, self.service_table, self.button
        )
        self.client_table.table_widget.single_selection = True
        self.add_client_button.clicked.connect(AddInstance(self, 'Client').show)
        self.button.clicked.connect(self.form)

    def form(self):
        path = QFileDialog().getSaveFileName(self, filter='(*.pdf)')[0]
        if path:
            if not self.client_table.table_widget.selected:
                return
            client = self.client_table.table_widget.selected[0]
            canvas = Canvas(path)
            services = self.service_table.table_widget.selected
            insurance_name = 'No insurance'
            for insurance in DB.get('Insurance'):
                if insurance.Id == client.InsuranceId:
                    insurance_name = insurance.Name
            lines = [
                datetime.date.today(),
                self.id,
                insurance_name,
                client.FullName,
                timestamp_to_date(client.BirthdateTimestamp),
                "service codes: " + ', '.join([service.Id for service in services]),
                sum([service.Price for service in services])
            ]
            for i, line in enumerate(lines[::-1]):
                canvas.drawString(0, i * 20, str(line))
            canvas.save()


class Order(QWidget):
    def __init__(self):
        super().__init__()
        self.id = QSpinBox()
        self.button = QPushButton('Формировать')
        order_id = 0
        for order in DB.get('Order'):
            if order.Id >= order_id:
                order_id = order.Id + 1
        self.id.setValue(order_id)
        self.button.clicked.connect(self.form)
        QVBoxLayout(self)
        self.layout().addWidget(self.id)
        self.layout().addWidget(self.button)

    def form(self):
        for order in DB.get('Order'):
            if order.Id == self.id.value():
                QLabel('Заказ с таким номером уже существует').show()
                break
        else:
            path = QFileDialog().getSaveFileName(self, filter='(*.pdf)')[0]
            if path:
                canvas = Canvas(path)
                lines = [
                    '|||||||||||||',
                    '000000' + str(self.id.value())
                ]
                for i, line in enumerate(lines[::-1]):
                    canvas.drawString(0, i * 20, str(line))
                canvas.save()
            Form(self, self.id.value()).show()
