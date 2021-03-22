import sys
from data_gui import *
from PyQt5.Qt import *
from design import Ui_MainWindow
from widgets import PlotWidget


class MainWindow(QMainWindow):

    #  Инициализация основного окна
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.data = DataGUI(self.ui)
        self.current_date = ''
        self.timer_temp_bat = QTimer()
        self.timer_temp_bat.timeout.connect(self.data.temp_bat)
        self.timer_combobox = QTimer()
        self.timer_combobox.timeout.connect(self.data.add_item_to_combo_box)
        self.init_ui()

    def init_ui(self):
        self.ui.widget = PlotWidget()
        self.ui.verticalLayout.addWidget(self.ui.widget)
        self.ui.widget_2 = PlotWidget()
        self.ui.verticalLayout_2.addWidget(self.ui.widget_2)
        self.ui.widget_3 = PlotWidget()
        self.ui.verticalLayout_3.addWidget(self.ui.widget_3)
        # self.ui.widget_4 = PlotWidget()
        # self.ui.verticalLayout_4.addWidget(self.ui.widget_4)
        self.connect_ui()
        self.translate_ui()
        self.timer_temp_bat.start(200)
        self.timer_combobox.start(200)
        self.show()

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

    def connect_ui(self):
        self.ui.Update.clicked.connect(self.button_clicked_1)
        self.ui.Update.clicked.connect(self.button_clicked_2)
        self.ui.Update.clicked.connect(self.button_clicked_3)
        # self.ui.Update.clicked.connect(self.button_clicked_1)

    def button_clicked_1(self):
        file_raw, file_fft = self.data.get_file_type()
        self.ui.widget.plot(current_file=file_raw, option='raw')
        self.ui.widget.draw()

    def button_clicked_2(self):
        file_raw, file_fft = self.data.get_file_type()
        self.ui.widget_2.plot(current_file=file_fft, option='fft_spectra_full')
        self.ui.widget_2.draw()

    def button_clicked_3(self):
        file_raw, file_fft = self.data.get_file_type()
        self.ui.widget_3.plot(current_file=file_fft, option='fft_spectra_not_full')
        self.ui.widget_3.draw()


def run():
    app = QApplication(sys.argv)
    window = MainWindow()
    app.exec_()


if __name__ == '__main__':
    run()
