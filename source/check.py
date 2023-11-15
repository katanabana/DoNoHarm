from PyQt5.QtWidgets import QWidget, QVBoxLayout, QDateEdit, QPushButton, QHBoxLayout, QLabel, QFileDialog
from reportlab.pdfgen.canvas import Canvas

from source.widgets import Table


class DateRange(QWidget):
    def __init__(self, label):
        super().__init__()
        QHBoxLayout(self)
        self.start = QDateEdit()
        self.end = QDateEdit()
        self.layout().addWidget(QLabel(label))
        self.layout().addWidget(self.start)
        self.layout().addWidget(QLabel('-'))
        self.layout().addWidget(self.end)
        self.layout().addStretch()

    @property
    def text(self):
        return self.start.text() + '-' + self.end.text()


class Check(QWidget):
    def __init__(self):
        super().__init__()
        self.table = Table('Client')
        self.button = QPushButton('Формировать')
        self.orders_range = DateRange('Заказы за период:')
        self.payment_range = DateRange('Период оплаты:')
        self.button.clicked.connect(self.perform)
        self.table.table_widget.single_selection = True
        QVBoxLayout(self)
        self.layout().addWidget(self.orders_range)
        self.layout().addWidget(self.payment_range)
        self.layout().addWidget(self.table)
        self.layout().addWidget(self.button)

    def perform(self):
        clients = self.table.table_widget.selected
        if clients:
            path = QFileDialog().getSaveFileName(self, filter='(*.pdf);;(*.csv)')[0]
            if path:

                client = clients[0]
                lines = []
                if client.InsuranceId is None:
                    lines.append('Client name: ' + client.FullName)
                    lines.append('Client phone: ' + client.Phone)
                else:
                    lines.append('Insurance name: ' + client.insurance.Name)
                services = []
                for order in client.order_collection:
                    if self.orders_range.start.date() <= order.Date <= self.orders_range.end.date():
                        for service_to_order in order.servicetoorder_collection:
                            services.append(service_to_order.service)
                lines += [
                    'Pay period: ' + self.payment_range.text,
                    'Services codes and prices:']
                lines.extend([f'{service.Id} - {service.Price}' for service in services])
                lines.append('Total price: ' + str(sum([service.Price for service in services])))

                extension = path.split('.')[-1]
                if extension == 'pdf':
                    canvas = Canvas(path)
                    for i, line in enumerate(lines[::-1]):
                        canvas.drawString(0, i * 20, str(line))
                    canvas.save()
                else:
                    with open(path, 'w+') as file:
                        file.writelines('\n'.join(lines))
