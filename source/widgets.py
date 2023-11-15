import nltk
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QWidget, QTableWidgetItem, QLabel, QHBoxLayout, \
    QLineEdit, QPushButton, QFormLayout, QScrollArea
from sqlalchemy.orm import object_session

from source.constants import PROJECT_NAME
from source.database import DB


class Dialog(QDialog):
    def __init__(self, parent, *widgets):
        super().__init__(parent)
        self.setWindowTitle(PROJECT_NAME)
        QVBoxLayout(self)
        for widget in widgets:
            self.layout().addWidget(widget)


class ScrollDialog(Dialog):
    def __init__(self, parent, *widgets):
        widget = QWidget()
        QVBoxLayout(widget)
        for sub_widget in widgets:
            widget.layout().addWidget(sub_widget)
        scroll = QScrollArea()
        scroll.setWidget(widget)
        super().__init__(parent, scroll)


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
                    current_item = self.item(i, j)
                    if current_item:
                        current_item.setBackground(QColor('white'))

        row = item.row()
        for col in range(self.columnCount()):
            self.item(row, col).setBackground(QColor('green'))
            self.selected_rows.append(row)

    @property
    def selected(self):
        return [self.instances[i] for i in self.selected_rows]


class Table(QScrollArea):
    def __init__(self, table_name):
        super().__init__()
        self.setWidgetResizable(True)
        self.setWidget(QWidget())
        self.table_name = table_name
        self.table_widget = TableWidget(table_name)
        QVBoxLayout(self.widget())
        self.searches = []
        searches = QHBoxLayout()
        searches.setSpacing(0)
        for i in range(self.table_widget.columnCount()):
            search = QLineEdit()
            width = self.table_widget.columnWidth(i)
            search.setMinimumWidth(width)
            search.setMaximumWidth(width)
            search.textChanged.connect(self.search)
            self.searches.append(search)
            searches.addWidget(search)
        self.clear_button = QPushButton('Отчистить')
        self.clear_button.clicked.connect(self.clear)
        searches.addWidget(self.clear_button)
        self.widget().layout().addWidget(QLabel(table_name))
        self.widget().layout().addLayout(searches)
        self.widget().layout().addWidget(self.table_widget)

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
    def __init__(self, parent, table_name, *disable_columns):
        super().__init__(parent)
        self.inputs = []
        self.table = getattr(DB.tables, table_name).__table__
        self.instance = getattr(DB.tables, table_name)()
        QVBoxLayout(self)
        inputs = QFormLayout()
        for column in self.table.columns:
            input_widget = QLineEdit()
            self.inputs.append(input_widget)
            inputs.addRow(column.name, input_widget)
            if column.name in disable_columns:
                input_widget.setDisabled(True)
        self.layout().addLayout(inputs)
        self.button = QPushButton('Добавить')
        self.button.clicked.connect(self.perform)
        self.layout().addWidget(self.button)

    def perform(self):
        try:
            session = object_session(self.instance)
            if session is None:
                session = DB.get_session()
            for column, input_widget in zip(self.table.columns, self.inputs):
                value = input_widget.text()
                try:
                    value = column.type.python_type(value)
                except Exception:
                    pass
                setattr(self.instance, column.name, value)
            session.add(self.instance)
            session.commit()
            self.close()
        except Exception as ex:
            Dialog(self, QLabel('Неверные данные\n' + str(ex))).show()


class EditInstance(AddInstance):
    def __init__(self, parent, instance, *disable_columns):
        super().__init__(parent, instance.__class__.__name__, *disable_columns)
        self.instance = instance
        for input_widget, column in zip(self.inputs, self.table.columns):
            value = getattr(instance, column.name)
            input_widget.setText(str(value))
        self.button.setText('Сохранить изменения')


class EditTable(Table):
    def __init__(self, table_name, *disable_columns):
        super().__init__(table_name)
        self.disable_columns = disable_columns
        self.table_widget.single_selection = True
        self.table_widget.clicked.connect(self.edit)

    def edit(self):
        if self.table_widget.selected:
            client = self.table_widget.selected[0]
            EditInstance(self, client, *self.disable_columns).show()
