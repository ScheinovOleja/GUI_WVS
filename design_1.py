import sys
import os
from argparse import Namespace
import argparse
from PyQt5.Qt import *
from random import randint
import numpy as np  # Для вычислений
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas  # Область для черчения
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar  # Панель управления
from matplotlib.figure import Figure  # Фигура для черчений
from plots import Plots
import matplotlib.pyplot as plt


class PlotWidget(QWidget):

    functions = {
        1: np.sin,
        2: np.cos,
    }

    def __init__(self, current_file, type):
        super(PlotWidget, self).__init__()  # Инициализируем экземпляр

        #self.arguments = Namespace(input='data//IIS3DWB//' + current_file.currentText(), savefig=False, print=True,
        #                           name='', fmin=None, fmax=None, ylog=True)
        #self.arguments = Namespace(input='data//IIS3DWB//2021-03-08-19-05-51-accel_raw.log', savefig=False, print=True, name = '', fmin = None, fmax = None, ylog = True)
        self.arguments = Namespace(input=current_file, savefig=False, print=True,
                                   name='', fmin=None, fmax=None, ylog=True)
        self.plots = Plots(arguments=self.arguments, boolraw='True')
        self.main_layout = QVBoxLayout(self)
        #self.figure = Figure()
        #self.figure = self.plots.run('raw')
        self.figure = self.plots.run(type)
        self.canvas = FigureCanvas(self.figure)
        self.nav_tool_bar = NavigationToolbar(self.canvas, self)
        self.main_layout.addWidget(self.canvas)
        self.main_layout.addWidget(self.nav_tool_bar)

    def plot(self):

        #self.figure.clear()
        self.figure = self.plots.run('raw')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.draw()

class MainWindow(QMainWindow):

    #  Инициализация основного окна
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setObjectName("MainWindow")
        self.resize(1060, 680)
        self.central_widget = QWidget(self)
        self.central_widget.setObjectName("central_widget")

        self.grid_layout = QGridLayout(self.central_widget)
        self.grid_layout.setObjectName("gridLayout")

        self.check_box = QCheckBox(self.central_widget)
        self.check_box.setObjectName("checkBox")

        self.grid_layout.addWidget(self.check_box, 0, 0, 1, 1)

        self.horizontal_layout = QHBoxLayout()
        self.horizontal_layout.setObjectName("horizontalLayout")

        self.combo_box = QComboBox(self.central_widget)
        self.combo_box.setObjectName("ComboBox")

        self.update = QPushButton(self.central_widget)
        self.update.setObjectName("Update")

        self.horizontal_layout.addWidget(self.update)
        self.horizontal_layout.addWidget(self.combo_box)

        self.grid_layout.addLayout(self.horizontal_layout, 0, 1, 1, 1)

        self.label = QLabel(self.central_widget)
        self.label.setObjectName("label")

        self.label_2 = QLabel(self.central_widget)
        self.label_2.setObjectName("label_2")

        self.label_3 = QLabel(self.central_widget)
        self.label_3.setObjectName("label_3")

        self.label_4 = QLabel(self.central_widget)
        self.label_4.setObjectName("label_4")

        self.vertical_layout = QVBoxLayout()
        self.vertical_layout.setObjectName("verticalLayout")

        self.add_item_to_combo_box()

        #self.widget = PlotWidget(current_file=self.combo_box)
        self.widget = PlotWidget(current_file='data//IIS3DWB//2021-03-08-19-05-51-accel_raw.log', type='raw')
        self.widget.setObjectName("widget")

        self.vertical_layout.addWidget(self.label)
        self.vertical_layout.addWidget(self.widget)

        self.grid_layout.addLayout(self.vertical_layout, 1, 0, 1, 1)

        self.vertical_layout_2 = QVBoxLayout()
        self.vertical_layout_2.setObjectName("verticalLayout_2")

        #self.widget_2 = PlotWidget(current_file=self.combo_box)
        self.widget_2 = PlotWidget(current_file='data//IIS3DWB//2021-03-08-19-05-51-accel_fft.log', type='fft_spectra')
        self.widget_2.setObjectName("widget_2")

        self.vertical_layout_2.addWidget(self.label_2)
        self.vertical_layout_2.addWidget(self.widget_2)

        self.grid_layout.addLayout(self.vertical_layout_2, 1, 1, 1, 1)

        self.vertical_layout_3 = QVBoxLayout()
        self.vertical_layout_3.setObjectName("verticalLayout_3")

        #self.widget_3 = PlotWidget(current_file=self.combo_box)
        self.widget_3 = PlotWidget(current_file='data//IIS3DWB//2021-03-08-19-05-51-accel_fft.log', type='Fourier_spectra')
        self.widget_3.setObjectName("widget_3")

        self.vertical_layout_3.addWidget(self.label_3)
        self.vertical_layout_3.addWidget(self.widget_3)

        self.grid_layout.addLayout(self.vertical_layout_3, 3, 0, 1, 1)

        # self.vertica_layout_4 = QLCDNumber()
        # self.vertica_layout_4.setObjectName("verticalLayout_4")
        #
        # #self.widget_4 = PlotWidget(current_file=self.combo_box)
        # self.widget_4 = PlotWidget(current_file='',type='')
        #self.widget_4.setObjectName("widget_4")
        #
        # self.vertica_layout_4.value = '5.000'
        # self.vertica_layout_4.
        # self.vertica_layout_4.addWidget(self.label_4)
        #self.vertica_layout_4.addWidget(self.widget_4)
        #
        # self.grid_layout.addLayout(self.vertica_layout_4, 3, 1, 1, 1)

        self.setCentralWidget(self.central_widget)

        self.menu_bar = QMenuBar(self)
        self.menu_bar.setGeometry(QRect(0, 0, 1060, 20))
        self.menu_bar.setObjectName("menubar")

        self.setMenuBar(self.menu_bar)
        self.status_bar = QStatusBar(self)
        self.status_bar.setObjectName("statusbar")
        self.setStatusBar(self.status_bar)

        self.translate_ui()
        self.connect_ui()

    def add_item_to_combo_box(self):
        folder = os.getcwd() + "\\data\\IIS3DWB"
        for item in os.listdir(folder):
            if not item.startswith('.') and os.path.isfile(os.path.join(folder, item)):
                self.combo_box.addItem(item)

    def translate_ui(self):
        _translate = QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.check_box.setText(_translate("MainWindow", "AutoUpdate"))
        self.label.setText(_translate("MainWindow", "Спектр сигнала"))
        self.label_2.setText(_translate("MainWindow", "Спектр огибающей"))
        self.label_3.setText(_translate("MainWindow", "Полный спектр"))
        #self.label_4.setText(_translate("MainWindow", "Сигнал с представлением"))
        self.label_4.setText(_translate("MainWindow", "Батарея"))
        self.update.setText(_translate("MainWindow", "Update"))

    def connect_ui(self):
        self.update.clicked.connect(self.widget.plot)
        self.update.clicked.connect(self.widget_2.plot)
        self.update.clicked.connect(self.widget_3.plot)
        #self.update.clicked.connect(self.widget_4.plot)

    def clear(self):
        self.widget.figure.clear()
        self.widget.canvas.draw()
        self.widget_2.figure.clear()
        self.widget_2.canvas.draw()
        self.widget_3.figure.clear()
        self.widget_3.canvas.draw()
        self.widget_4.figure.clear()
        self.widget_4.canvas.draw()


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
