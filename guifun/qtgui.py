#sudo apt-get install python3-tk
#pip install dearpygui numpy

import sys
import time

import numpy as np
from PySide6 import QtCore, QtWidgets, QtGui
import tests
import inspect
import importlib
import test_execution
import logging

#from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure


class TestLiveView(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout2 = QtWidgets.QGridLayout()

        # Ideally one would use self.addToolBar here, but it is slightly
        # incompatible between PyQt6 and other bindings, so we just add the
        # toolbar as a plain widget instead.
        dynamic_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(NavigationToolbar(dynamic_canvas, self))
        layout.addWidget(dynamic_canvas)
        self.l_3_3v = QtWidgets.QLabel('3.3v: 1.2')
        self.l_12v = QtWidgets.QLabel('12v: 1.2')
        self.l_inta = QtWidgets.QLabel('Inta: 1.2')
        self.l_v2mon = QtWidgets.QLabel('v2mon: 1.2')
        font = self.l_3_3v.font()
        font.setPointSize(30)
        self.l_3_3v.setFont(font)
        self.l_12v.setFont(font)
        self.l_inta.setFont(font)
        self.l_v2mon.setFont(font)
        layout.addLayout(layout2)
        layout2.addWidget(self.l_3_3v, 0, 0)
        layout2.addWidget(self.l_12v, 0, 1)
        layout2.addWidget(self.l_inta, 1, 0)
        layout2.addWidget(self.l_v2mon, 1, 1)

        colors = [("Red", "#FF0000"),
                ("Green", "#00FF00"),
                ("Blue", "#0000FF"),
                ("Black", "#000000"),
                ("White", "#FFFFFF"),
                ("Electric Green", "#41CD52"),
                ("Dark Blue", "#222840"),
                ("Yellow", "#F9E56d")]

        def get_rgb_from_hex(code):
            code_hex = code.replace("#", "")
            rgb = tuple(int(code_hex[i:i+2], 16) for i in (0, 2, 4))
            return QtGui.QColor.fromRgb(rgb[0], rgb[1], rgb[2])

        self.table = QtWidgets.QTableWidget()
        self.table.setHorizontalHeaderLabels(['Name', 'Hex Code', 'Color'])
        self.table.setRowCount(len(colors))
        self.table.setColumnCount(len(colors[0]) + 1)
        for i, (name, code) in enumerate(colors):
            item_name = QtWidgets.QTableWidgetItem(name)
            item_code = QtWidgets.QTableWidgetItem(code)
            item_color = QtWidgets.QTableWidgetItem()
            item_color.setBackground(get_rgb_from_hex(code))
            self.table.setItem(i, 0, item_name)
            self.table.setItem(i, 1, item_code)
            self.table.setItem(i, 2, item_color)
        
        self.table.insertRow(self.table.rowCount())
        self.table.setItem(self.table.rowCount()-1, 0, QtWidgets.QTableWidgetItem("one two three"))
        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        layout.addWidget(self.table)



        logTextBox = QPlainTextEditLogger(self)
        logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(logTextBox)
        # You can control the logging level
        logging.getLogger().setLevel(logging.DEBUG)
        layout.addWidget(logTextBox.widget)

        self._dynamic_ax = dynamic_canvas.figure.subplots()
        t = np.linspace(0, 10, 101)
        # Set up a Line2D.
        self._line, = self._dynamic_ax.plot(t, np.sin(t + time.time()))
        #self._timer = dynamic_canvas.new_timer(100)
        #self._timer.add_callback(self._update_canvas)
        #self._timer.start()
    
    @QtCore.Slot()
    def _update_canvas(self):
        t = np.linspace(0, 10, 101)
        # Shift the sinusoid as a function of time.
        self._line.set_data(t, np.sin(t + time.time()))
        self._line.figure.canvas.draw()
    
    def update_generic(self, someobj):
        t = np.linspace(0, 10, 101)
        # Shift the sinusoid as a function of time.
        self._line.set_data(t, someobj)
        self._line.figure.canvas.draw()
    
class QPlainTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)    

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)    



class TestSelection(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)
        layout2 = QtWidgets.QHBoxLayout()

        self.label1 = QtWidgets.QLabel("Operator Name:")
        self.label2 = QtWidgets.QLabel("Select a Test:")
        self.op_name = QtWidgets.QLineEdit()
        self.listbox = QtWidgets.QListWidget()
        self.refresh_tests = QtWidgets.QPushButton("Refresh Test List")
        self.refresh_tests.clicked.connect(self._refresh_tests)
        self.serial_label = QtWidgets.QLabel("UUT Serial:")
        self.serial_input = QtWidgets.QLineEdit()

        self.but0 = QtWidgets.QPushButton("Run Slot 0")
        self.but0.clicked.connect(lambda: self._slot_btn(0))
        self.but1 = QtWidgets.QPushButton("Run Slot 1")
        self.but1.clicked.connect(lambda: self._slot_btn(1))
        self.but2 = QtWidgets.QPushButton("Run Slot 2")
        self.but2.clicked.connect(lambda: self._slot_btn(2))
            
        self.listbox.addItems(list(tests.exported_tests.keys()))
        layout.addWidget(self.label1)
        layout.addWidget(self.op_name)
        layout.addWidget(self.label2)
        layout.addWidget(self.listbox)
        layout.addWidget(self.refresh_tests)
        layout.addWidget(self.serial_label)
        layout.addWidget(self.serial_input)
        layout.addLayout(layout2)
        layout2.addWidget(self.but0)
        layout2.addWidget(self.but1)
        layout2.addWidget(self.but2)

        # Maintain a list of running tasks/tests
        self.running_tests = [None, None, None]
    
    def _slot_btn(self, slot):
        selected_test = self.listbox.currentItem().text()
        rn = tests.exported_tests[selected_test]
        tlv = TestLiveView()
        tlv.show()
        tlv.activateWindow()
        tlv.raise_()
        te = test_execution.TestExecution(tlv,
                                          slot,
                                          self.serial_input.text(),
                                          rn(),
                                          self.op_name.text())
        te.run()
        self.running_tests[slot] = te
            
    
    def _refresh_tests(self):
        global tests
        tests = importlib.reload(tests)
        self.listbox.clear()
        self.listbox.addItems(list(tests.exported_tests.keys()))



if __name__ == "__main__":
    # Check whether there is already a running QApplication (e.g., if running
    # from an IDE).
    qapp = QtWidgets.QApplication.instance()
    if not qapp:
        qapp = QtWidgets.QApplication(sys.argv)

    app = TestSelection()
    app.show()
    app.activateWindow()
    app.raise_()

    qapp.exec()