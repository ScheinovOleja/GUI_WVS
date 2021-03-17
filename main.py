import sys
import os
from multiprocessing import Process
import time
from argparse import Namespace
from PyQt5.Qt import *
import numpy as np  # Для вычислений
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas  # Область для черчения
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar  # Панель управления
from design import Ui_MainWindow
from plots import Plots
from PyQt5 import QtCore, QtGui, QtWidgets
from threading import Thread
#from matplotlib.widgets import Cursor
class PlotWidget(QWidget):
    functions = {
        1: np.sin,
        2: np.cos,
    }

    def __init__(self):
        super(PlotWidget, self).__init__()  # Инициализируем экземпляр
        self.figure = None
        self.main_layout = QVBoxLayout(self)
        self.canvas = None
        self.count = 0
        self.arguments = Namespace()
        self.plots = None
        self.nav_tool_bar = None

    def plot(self, current_file, option):
        self.arguments = Namespace(input=current_file, savefig=False, print=True,
                                   name='', fmin=None, fmax=None, ylog=True)
        self.plots = Plots(arguments=self.arguments, boolraw='True')
        self.figure = self.plots.run(option)
        self.canvas = FigureCanvas(self.figure)
        self.nav_tool_bar = NavigationToolbar(self.canvas, self)
        # if self.count == 0:
        #     self.main_layout.addWidget(self.canvas)
        #     self.main_layout.addWidget(self.nav_tool_bar)
        # self.canvas.draw()
        #self.canvas.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        #self.canvas.cursor = self.plots.cursor
        #self.cursor = Cursor(self.plots.a, horizOn=True, vertOn=True, color='green', linewidth=2.0)
        # self.count += 1

    def draw(self):
        if self.count == 0:
            self.main_layout.addWidget(self.canvas)
            self.main_layout.addWidget(self.nav_tool_bar)
        self.canvas.draw()
        self.count += 1

class MainWindow(QMainWindow):

    #  Инициализация основного окна
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.current_date = ''
        self.folder = os.getcwd() + "\\data"
        self.init_ui()

    def init_ui(self):
        self.add_item_to_combo_box()
        self.current_date = self.ui.comboBox.currentText().split('-a')[0]
        self.ui.widget = PlotWidget()
        self.ui.verticalLayout.addWidget(self.ui.widget)
        self.ui.widget_2 = PlotWidget()
        self.ui.verticalLayout_2.addWidget(self.ui.widget_2)
        self.ui.widget_3 = PlotWidget()
        self.ui.verticalLayout_3.addWidget(self.ui.widget_3)
        # self.widget_4 = PlotWidget()
        # self.vertica_layout_4.addWidget(self.widget_4)
        self.connect_ui()
        self.translate_ui()
        self.temp_bat()

    def parse(self, directory=None, prefix='', label=None):
        for item in os.listdir(self.folder + directory):
            if self.current_date.__add__(prefix) in item:
                with open(self.folder + f'{directory}\\{item}') as file:
                    for line in file:
                        try:
                            value = float(line.split(' ')[0])
                            if label == self.ui.label_5:
                                self.ui.label_5.setText('Батарея: ' + str(value) + 'V')
                            elif label == self.ui.label_6:
                                self.ui.label_6.setText('Температура: ' + str(value) + 'C')
                        except ValueError:
                            continue

    def temp_bat(self):
        self.parse(directory='\\battery', label=self.ui.label_5)
        self.parse(directory='\\IIS3DWB', prefix='-temperature.log', label=self.ui.label_6)

    def translate_ui(self):
        _translate = QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.ui.checkBox.setText(_translate("MainWindow", "AutoUpdate"))
        self.ui.label.setText(_translate("MainWindow", "Сырой сигнал"))
        self.ui.label_2.setText(_translate("MainWindow", "Спектр (ограничен)"))
        self.ui.label_3.setText(_translate("MainWindow", "Полный спектр"))
        # self.ui.label_4.setText(_translate("MainWindow", "Батарея"))
        self.ui.label_5.setText(_translate("MainWindow", "Батарея:"))
        self.ui.label_6.setText(_translate("MainWindow", "Температура:"))
        self.ui.label_7.setText(_translate("MainWindow", "Директория:"))
        self.ui.label_8.setText(_translate("MainWindow", "Файл:"))
        self.ui.Update.setText(_translate("MainWindow", "Update"))

    def add_item_to_combo_box(self):
        for item in os.listdir(self.folder):
            self.ui.comboBox_2.addItem(item)
        for item in os.listdir(self.folder + '\\IIS3DWB'):
            if not item.startswith('.') and 'raw' in item:
                self.ui.comboBox.addItem(item)

    def connect_ui(self):
        ui1 = Thread(target=self.connect_ui1, args=())
        ui2 = Thread(target=self.connect_ui2, args=())
        ui3 = Thread(target=self.connect_ui3, args=())

        ui1.start()
        ui2.start()
        ui3.start()

        ui1.join()
        ui2.join()
        ui3.join()

        #self.ui.Update.clicked.connect(self.button_clicked)

    def connect_ui1(self):
        self.ui.Update.clicked.connect(self.button_clicked1)
    def connect_ui2(self):
        self.ui.Update.clicked.connect(self.button_clicked2)
    def connect_ui3(self):
        self.ui.Update.clicked.connect(self.button_clicked3)

    def get_file_type(self):
        self.current_date = self.ui.comboBox.currentText().split('-a')[0]
        self.temp_bat()
        file_raw = ''
        file_fft = ''
        for items in os.listdir(self.folder + '\\IIS3DWB'):
            if items.split('-a')[0] == self.current_date:
                if 'raw' in items:
                    file_raw = 'data//IIS3DWB//' + items
                elif 'fft' in items:
                    file_fft = 'data//IIS3DWB//' + items
                else:
                    continue
        return file_raw, file_fft

    # def button_clicked(self):
    #     file_raw, file_fft = self.get_file_type()
    #     print(f"started at {time.strftime('%X')}")
    #     self.ui.widget.plot(current_file=file_raw, option='raw')
    #     sh = Thread(target=self.ui.widget.draw, args=())
    #     sh.start()
    #     sh.join()
    #     self.ui.widget_2.plot(current_file=file_fft, option='fft_spectra_not_full')
    #     sh2 = Thread(target=self.ui.widget_2.draw, args=())
    #     sh2.start()
    #     sh2.join()
    #     self.ui.widget_3.plot(current_file=file_fft, option='fft_spectra_full')
    #     sh3 = Thread(target=self.ui.widget_3.draw, args=())
    #     sh3.start()
    #     sh3.join()
    #     print(f"started at 2 {time.strftime('%X')}")

    def button_clicked1(self):
        file_raw, file_fft = self.get_file_type()
        print(f"started at {time.strftime('%X')}")
        self.ui.widget.plot(current_file=file_raw, option='raw')
        self.ui.widget.draw()

    def button_clicked2(self):
        file_raw, file_fft = self.get_file_type()
        self.ui.widget_2.plot(current_file=file_fft, option='fft_spectra_not_full')
        self.ui.widget_2.draw()

    def button_clicked3(self):
        file_raw, file_fft = self.get_file_type()
        self.ui.widget_3.plot(current_file=file_fft, option='fft_spectra_full')
        self.ui.widget_3.draw()
        print(f"started at 2 {time.strftime('%X')}")



if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
