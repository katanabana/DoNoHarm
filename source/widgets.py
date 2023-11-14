import nltk
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QWidget, QTableWidgetItem, QLabel, QHBoxLayout, \
    QLineEdit, QPushButton, QFormLayout

from source.constants import PROJECT_NAME
from source.database import DB


class Dialog(QDialog):
    def __init__(self, parent, *widgets):
        super().__init__(parent)
        self.setWindowTitle(PROJECT_NAME)
        QVBoxLayout(self)
        for widget in widgets:
            self.layout().addWidget(widget)


class TableWidget(QTableWidget):
    def __init__(self, table_name, single_selection=False):
        super().__init__()
        self.selected_rows = []
        self.single_selection = single_selection
        self.table = getattr(DB.tables, table_name).__table__
        self.setColumnCount(len(self.table.columns))
        self.setRowCount(10)
        self.setHorizontalHeaderLabels([col.name for col in self.table.columns])
        all_instances = DB.get(table_name)
        self.instances = list(all_instances)[:self.rowCount()]
        self.update_data(self.instances)
        self.itemClicked.connect(self.update_selection)

    def update_data(self, instances):
        self.instances = instances
        self.clearContents()
        for i, instance in enumerate(instances):
            for j, column in enumerate(self.table.columns):
                value = getattr(instance, column.name)
                self.setItem(i, j, QTableWidgetItem(str(value)))

    def update_selection(self, item):
        if self.single_selection:
            self.selected_rows = []
            for i in range(self.rowCount()):
                for j in range(self.columnCount()):
                    self.item(i, j).setBackground(QColor('white'))

        row = item.row()
        for col in range(self.columnCount()):
            self.item(row, col).setBackground(QColor('green'))
            self.selected_rows.append(row)

    @property
    def selected(self):
        return [self.instances[i] for i in self.selected_rows]


class Table(QWidget):
    def __init__(self, table_name):
        super().__init__()
        self.table_name = table_name
        self.table_widget = TableWidget(table_name)
        QVBoxLayout(self)
        self.searches = []
        searches = QHBoxLayout()
        for i in range(self.table_widget.columnCount()):
            search = QLineEdit()
            width = self.table_widget.columnWidth(i)
            search.setMinimumWidth(width)
            search.textChanged.connect(self.search)
            self.searches.append(search)
            searches.addWidget(search)
        self.clear_button = QPushButton('Отчистить')
        self.clear_button.clicked.connect(self.clear)
        searches.addWidget(self.clear_button)
        self.layout().addWidget(QLabel(table_name))
        self.layout().addLayout(searches)
        self.layout().addWidget(self.table_widget)

    def clear(self):
        for search in self.searches:
            search.setText('')

    def search(self):
        instances = []
        for instance in DB.get(self.table_name):
            for i, search in enumerate(self.searches):
                column = self.table_widget.horizontalHeaderItem(i).text()
                value = getattr(instance, column)
                string1, string2 = search.text(), str(value)
                if string1 not in string2:
                    break
            else:
                instances.append(instance)
                if len(instances) == self.table_widget.rowCount():
                    break
        self.table_widget.update_data(instances)


class AddInstance(Dialog):
    def __init__(self, parent, table_name):
        super().__init__(parent)
        self.inputs = []
        self.table = getattr(DB.tables, table_name).__table__
        QVBoxLayout(self)
        inputs = QFormLayout()
        for column in self.table.columns:
            input_widget = QLineEdit()
            self.inputs.append(input_widget)
            inputs.addRow(column.name, input_widget)
        self.layout().addLayout(inputs)
        self.button = QPushButton('Добавить')
        self.button.clicked.connect(self.add)
        self.layout().addWidget(self.button)

    def add(self):
        try:
            instance = getattr(DB.tables, self.table.name)()
            session = DB.get_session()
            for column, input_widget in zip(self.table.columns, self.inputs):
                value = input_widget.text()
                try:
                    value = column.type.python_type(value)
                except Exception:
                    pass
                setattr(instance, column.name, value)
            session.add(instance)
            session.commit()
        except Exception as ex:
            Dialog(self, QLabel('Неверные данные\n' + str(ex))).show()