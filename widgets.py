from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas  # Область для черчения
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar  # Панель управления
from argparse import Namespace
from plots import Plots
from PyQt5.Qt import *


class PlotWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)  # Инициализируем экземпляр
        self.main_layout = QVBoxLayout(self)
        self.canvas = None
        self.count = 0
        self.nav_tool_bar = None
        self.arguments = None
        self.plots = None
        self.figure = None

    def plot(self, current_file, option):
        self.arguments = Namespace(input=current_file,
                                   savefig=False,
                                   print=True,
                                   name='',
                                   fmin=None,
                                   fmax=None,
                                   ylog=True)
        self.plots = Plots(arguments=self.arguments, boolraw='True')
        self.figure = self.plots.run(option)
        self.canvas = FigureCanvas(self.figure)
        self.nav_tool_bar = NavigationToolbar(self.canvas, self)

    def draw(self):
        if self.count == 0:
            self.main_layout.addWidget(self.canvas)
            self.main_layout.addWidget(self.nav_tool_bar)
        self.canvas.draw()
        self.count += 1
