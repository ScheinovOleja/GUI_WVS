import sys
import random  # Для рандомного выбора функций

import numpy as np  # Для вычислений

# Область для черчения
# Панель управления
# Фигура для черчений
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

# Импортирование необходимых виджетов
from PyQt5.Qt import *


def tg(data):
    return np.tan(data)


def ctg(data):
    return 1 / tg(data)


class PlotWidget(QWidget):
    functions = {
        1: np.sin,
        2: np.cos,
        3: tg,
        4: ctg
    }

    def __init__(self, parent=None):
        super(PlotWidget, self).__init__(parent)  # Инициализируем экземпляр

        self.main_layout = QVBoxLayout(self)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.nav_tool_bar = NavigationToolbar(self.canvas, self)
        self.main_layout.addWidget(self.canvas)
        self.main_layout.addWidget(self.nav_tool_bar)

    def plot(self):
        function_index = random.randint(1, 4)

        function = PlotWidget.functions[function_index]

        x = np.linspace(-10, 10, 2000)

        y = function(x)

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#DCDCDC')

        ax.axhline(y=0, xmin=-10.25, xmax=10.25, color='#000000')
        ax.axvline(x=0, ymin=-2, ymax=2, color='#000000')

        ax.set_ylim([-2, 2])
        ax.set_xlim([-10.25, 10.25])

        if function == np.sin or function == np.cos:
            ax.axhline(y=1, xmin=-10.25, xmax=10.25, color='b', linestyle='--')
            ax.axhline(y=-1, xmin=-10.25, xmax=10.25, color='b', linestyle='--')

        ax.plot(x, y, linestyle='-.', color='#008000', label=function.__name__)
        ax.legend(loc='upper right')
        self.canvas.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.central_widget = QWidget(self)
        # self.centralWidget2 = QWidget(self)
        self.l = QVBoxLayout(self.central_widget)
        self.bl = QHBoxLayout(self.central_widget)
        self.plot_widget = PlotWidget()
        self.plot_widget_2 = PlotWidget()
        self.battery_voltage = QPushButton('Update')
        # self.temperature = QPushButton('Temperature')
        # self.measurements = QPushButton('Measurements')
        # self.MaMs = QPushButton('min/avg/max/stde')
        # self.Fourier = QPushButton('Fourier spectre')
        self.clear_button = QPushButton('Clear')
        self.battery_voltage.setStyleSheet('font-size: 12pt; font-weight: 530;')
        # self.temperature.setStyleSheet('font-size: 12pt; font-weight: 530;')
        # self.measurements.setStyleSheet('font-size: 12pt; font-weight: 530;')
        # self.MaMs.setStyleSheet('font-size: 12pt; font-weight: 530;')
        # self.Fourier.setStyleSheet('font-size: 12pt; font-weight: 530;')
        self.clear_button.setStyleSheet('font-size: 12pt; font-weight: 530;')
        self.bl.addWidget(self.battery_voltage)
        # self.bl.addWidget(self.temperature)
        # self.bl.addWidget(self.measurements)
        # self.bl.addWidget(self.MaMs)
        # self.bl.addWidget(self.Fourier)
        self.bl.addWidget(self.clear_button)
        self.l.addLayout(self.bl)
        self.l.addWidget(self.plot_widget)
        self.l.addWidget(self.plot_widget_2)
        self.setCentralWidget(self.central_widget)
        # self.setCentralWidget(self.centralWidget2)
        self.connect_ui()

    def connect_ui(self):
        self.battery_voltage.clicked.connect(self.plot_widget.plot)
        self.battery_voltage.clicked.connect(self.plot_widget_2.plot)
        self.clear_button.clicked.connect(self.clear)

    def clear(self):
        self.plot_widget.figure.clear()
        self.plot_widget.canvas.draw()
        self.plot_widget_2.figure.clear()
        self.plot_widget_2.canvas.draw()


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
