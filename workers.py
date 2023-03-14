import numpy as np
import pandas as pd
from PyQt6.QtCore import pyqtSlot as Slot, pyqtSignal as Signal, QObject
from utils import verify

# !JSCH -> upgrade with data interpolation 
class LoadWorker(QObject):
    signal_data_plot = Signal(dict)
    signal_data_error = Signal(bool)
    @Slot(str)
    def load(self, path):
        plot_data = {}
        data = pd.read_excel(path)
        try:
            verify(data)
        except AssertionError:
            pass #!JSCH
        columns = data.columns.values.tolist()
        x = data.iloc[:, 0]
        y = data.iloc[:, 1]
        x_prev = 0
        y_prev = 0
        dy = []
        for (x_temp, y_temp) in zip(x, y):
            try:
                dy.append((y_temp - y_prev)/(x_temp - x_prev))
            except ZeroDivisionError:
                dy.append(0)
            x_prev = x_temp
            y_prev = y_temp
        # extract file name
        title = path.split('\\')[-1].split('.')[0]
        plot_data["title"] = title
        plot_data["x_label"]=columns[0]
        plot_data["y_label"]=columns[1]
        plot_data["x"]=x
        plot_data["y"]=y
        plot_data["dy"]=np.round(dy, 3)
        self.signal_data_plot.emit(plot_data)