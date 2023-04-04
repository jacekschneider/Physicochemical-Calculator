import numpy as np
import pandas as pd
from PyQt6.QtCore import pyqtSlot as Slot, pyqtSignal as Signal, QObject
from utils import verify
from reportlab.pdfgen.canvas import Canvas
import reportlab.lib.pagesizes as pagesizes

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
        

class ReportWorker(QObject):

    @Slot(list)
    def set_measurements(self, measurements:list):
        self.measurements = measurements
        
    def generate(self):
        canvas = Canvas(r"D:\Semestr10\PBL\Program\report.pdf", pagesize=(652, 792))
        canvas.setFillColorRGB(1,0,1)
        canvas.rect(5, 5, 652-10, 792-10, fill=1)
        canvas.setFillColorRGB(1,1,1)
        canvas.rect(10, 10, 652-20, 792-20, fill=1)
        canvas.setFillColorRGB(0,0,0)
        canvas.setFontSize(18)
        canvas.drawString(100, 750, "Physicochemical-Calculator")
        canvas.drawImage(r"D:\Semestr10\PBL\screeny\heidi.jpg", x=50, y=200)
        canvas.setTitle("Physicochemical-Calculator")
        canvas.showPage()
        canvas.save()
        