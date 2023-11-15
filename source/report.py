import datetime
import os

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QComboBox
from matplotlib import pyplot
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Table

from source.check import DateRange
from source.database import DB


class Report(QWidget):
    def __init__(self):
        super().__init__()
        self.date_range = DateRange('Период')
        self.type = QComboBox()
        self.button = QPushButton('Формировать')
        self.button.clicked.connect(self.form)
        self.type.addItems(['Таблица и График', 'Таблица', 'График'])
        dates = []
        for name in ['Order', 'ServiceToOrder']:
            for instance in DB.get(name):
                dates.append(instance.Date)
        self.date_range.start.setDate(min(dates))
        self.date_range.end.setDate(max(dates))
        QVBoxLayout(self)
        self.layout().addWidget(self.date_range)
        self.layout().addWidget(self.type)
        self.layout().addWidget(self.button)

    def form(self):
        if self.end() > self.start():
            path = QFileDialog().getSaveFileName(self, filter='(*.pdf)')[0]
            if path:
                canvas = Canvas(path)
                data = self.get_data()
                if 'Таблица' in self.type.currentText():
                    self.write_table(canvas, data)
                if 'График' in self.type.currentText():
                    self.write_plot(canvas, data)
                canvas.save()

    def start(self):
        return self.date_range.start.date().toPyDate()

    def end(self):
        return self.date_range.end.date().toPyDate()

    def get_data(self):
        labels = ['services count', 'clients count', 'clients per day', 'average order result']
        data = {}
        days = int((self.end() - self.start()).days)
        for label in labels:
            data[label] = [0 for _ in range(days)]

        items = list(DB.get('ServiceToOrder'))
        start = self.start()
        for day in range(days):
            elapsed = datetime.timedelta(days=day)
            current_end = start + elapsed
            for service_to_order in items:
                if start <= service_to_order.Date <= current_end:
                    data['services count'][day] += 1

        items = list(DB.get('Order'))
        client_ids = set()
        for day in range(days):
            current_clients = set()
            current_end = self.start() + datetime.timedelta(days=day)
            total = 0
            performed = 0
            for order in items:
                if self.start() <= order.Date <= current_end:
                    client_ids.add(order.ClientId)
                if current_end - datetime.timedelta(days=1) <= order.Date <= current_end:
                    current_clients.add(order.ClientId)
                    total += 1
                    if order.Status:
                        performed += 1
            if total:
                data['average order result'][day] = round(performed / total, 2)
            data['clients per day'][day] = len(current_clients)
            data['clients count'][day] = len(client_ids)

        return data

    def write_table(self, canvas: Canvas, data):
        key = next(iter(data))
        days = len(data[key])
        table_data = [['Days from dates range start', *map(str, range(days))]]
        for key, values in data.items():
            table_data.append([key, *map(str, values)])
        table = Table(table_data)
        table.wrapOn(canvas, 0, 0)
        table.drawOn(canvas, 0, 100)

    def write_plot(self, canvas: Canvas, data):
        key = list(data.keys())[0]
        days = len(data[key])
        x = list(range(days))
        for label, values in data.items():
            pyplot.plot(x, values, label=label)
        pyplot.legend(loc='best')
        path = 'temp.png'
        pyplot.savefig(path)
        canvas.drawImage(path, 0, 400)
        os.remove(path)
