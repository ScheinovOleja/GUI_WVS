import os


class DataGUI:

    def __init__(self, ui):
        self.ui = ui
        self.current_date = ''
        self.folder = os.getcwd() + "\\data"

    def parse(self, directory=None, prefix='', label=None):
        for item in os.listdir(self.folder + directory):
            if self.current_date.__add__(prefix) in item:
                with open(self.folder + f'{directory}\\{item}') as file:
                    for line in file:
                        try:
                            value = float(line.split(' ')[0])
                            if label == self.ui.label_5 and item.split('-bat')[0] == self.current_date:
                                self.ui.label_5.setText('Батарея: ' + str(value) + 'V')
                            elif label == self.ui.label_6 and item.split('-temp')[0] == self.current_date:
                                self.ui.label_6.setText('Температура: ' + str(value) + 'C')
                        except ValueError:
                            continue

    def temp_bat(self):
        self.parse(directory='\\battery', label=self.ui.label_5)
        self.parse(directory='\\IIS3DWB', prefix='-temperature.log', label=self.ui.label_6)

    def add_item_to_combo_box(self):
        for item in os.listdir(self.folder):
            if self.ui.comboBox_2.findText(item) == -1:
                self.ui.comboBox_2.addItem(item)
        for item in os.listdir(self.folder + '\\IIS3DWB'):
            if not item.startswith('.') and 'raw' in item:
                if self.ui.comboBox.findText(item) == -1:
                    self.ui.comboBox.addItem(item)
        self.current_date = self.ui.comboBox.currentText().split('-a')[0]

    def get_file_type(self):
        self.current_date = self.ui.comboBox.currentText().split('-a')[0]
        self.temp_bat()
        file_raw, file_fft = '', ''
        for items in os.listdir(self.folder + '\\IIS3DWB'):
            if items.split('-a')[0] == self.current_date:
                if 'raw' in items:
                    file_raw = 'data//IIS3DWB//' + items
                elif 'fft' in items:
                    file_fft = 'data//IIS3DWB//' + items
                else:
                    continue
        return file_raw, file_fft
