import numpy as np
import pyqtgraph as pg
import pathlib
from multipledispatch import dispatch
from PyQt6.QtWidgets import QWidget, QFileDialog, QFileIconProvider, QLineEdit, QCheckBox, QComboBox, QColorDialog, QPushButton
from PyQt6.QtCore import pyqtSignal as Signal, QDir, QObject
from PyQt6.QtGui import  QFileSystemModel, QStandardItemModel, QStandardItem
from PyQt6.uic.load_ui import loadUi
import utils as us
from utils import Measurement, RMSE

import pandas as pd
from sklearn.linear_model import LinearRegression
        
          
class WidgetNavigation(QWidget):
    emit_dirpath = Signal(str)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        loadUi("UI/ui_navigation.ui", self)
        self.pb_load_data.clicked.connect(self.open_file_dialog)
        
        # view_files widget
        self.model = QFileSystemModel()
        icon_provider = QFileIconProvider()
        self.model.setIconProvider(icon_provider) 
        self.model.setRootPath("") 
        self.model.setNameFilters(["*.txt"])
        self.model.setNameFilterDisables(False)
        
    def open_file_dialog(self):
        path_folder = QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            directory=str(pathlib.Path().absolute())
        )
        if path_folder != "":
            self.emit_dirpath.emit(path_folder)
            self.le_path.setText(path_folder)
            self.view_files.setModel(self.model)
            root_index = self.model.index(QDir.cleanPath(path_folder))
            self.view_files.setRootIndex(root_index)
        else:
            #!JSCH
            pass
    
    def clear(self):
        self.le_path.setText("")
        self.view_files.setModel(None)
  
        
class WidgetCAC(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        loadUi("UI/ui_cac.ui", self)
        
        self.items_plot = []
        self.items_text = []
        self.rmse_data = None
        
        self.graph.showGrid(x=True, y=True)
        # self.legend = self.graph.addLegend(labelTextColor="w", labelTextSize="12")
        # self.legend.anchor((0,0),(0.7,0.1))
        self.styles = {'color':'white', 'font-size':'17px'}
        self.graph.setLabel('bottom', 'logC, mg/ml', **self.styles)
        self.graph.setLabel('left', 'I1/I3', **self.styles)
    
    def load(self, rmse_data:RMSE):
        self.clear()
        self.rmse_data = rmse_data
        self.draw()
        
    def draw(self):
        
        X = self.rmse_data.regdata.loc['X'].to_numpy()
        Y = self.rmse_data.regdata.loc['Y'].to_numpy()
        cac_x = self.rmse_data.cac_data["cac_x"]
        cac_y = self.rmse_data.cac_data["cac_y"]
        
        model_id = self.rmse_data.model_id
        x1,x2 = X[:model_id], X[model_id:]
        y1,y2 = Y[:model_id], Y[model_id:]
        
        self.items_plot.append(self.graph.plot(x1, y1, pen=None, symbol='o', symbolPen=pg.mkPen("b"),symbolBrush=pg.mkBrush("b"),  symbolSize=7))
        self.items_plot.append(self.graph.plot(x2, y2, pen=None, symbol='o', symbolPen=pg.mkPen("r"),symbolBrush=pg.mkBrush("r"),  symbolSize=7))
        self.abline(self.rmse_data.cac_data["a1"], self.rmse_data.cac_data["b1"], start=-3.1, stop=cac_x+0.1, step=0.05)
        self.abline(self.rmse_data.cac_data["a2"], self.rmse_data.cac_data["b2"], start=cac_x-0.1, stop=1.2, step=0.05)

        self.items_plot.append(self.graph.plot(cac_x, cac_y, pen=None, symbol='d', symbolPen=pg.mkPen("g"),symbolBrush=pg.mkBrush("g"),  symbolSize=9))
        pos_x = round(cac_x[0], 3)
        pos_y = round(cac_y[0], 3)
        item_text = pg.TextItem(text="CAC = [{}, {}]".format(pos_x, pos_y), color=(0, 0, 0), border=pg.mkPen((0, 0, 0)), fill=pg.mkBrush("g"), anchor=(0, 0))
        item_text.setPos(cac_x[0], cac_y[0])
        self.items_text.append(item_text)
        self.graph.addItem(item_text)
        
        
        
    def abline(self, a, b, start, stop, step):
        # axes = self.graph.getAxis('bottom')
        # x_vals = np.array(axes.range)
        x_vals = np.arange(start=start, stop=stop, step=step)
        y_vals = b + a * x_vals
        self.items_plot.append(self.graph.plot(x_vals, y_vals, pen=pg.mkPen("w")))
    
    def clear(self):
        for item in self.items_plot:
            self.graph.removeItem(item)
        for item in self.items_text:
            self.graph.removeItem(item)
        while len(self.items_plot):
            self.items_plot.pop()
        while len(self.items_text):
            self.items_text.pop()
        
        
class WidgetData(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        loadUi("UI/ui_data.ui", self)
        
        self.measurements:list[Measurement] = []
        #Graph Items
        self.items_plot = []
        
        self.graph.showGrid(x=True, y=True)
        self.legend = self.graph.addLegend(labelTextColor="w", labelTextSize="12")
        self.legend.anchor((0,0),(0.7,0.1))
        self.styles = {'color':'white', 'font-size':'17px'}
        self.graph.setLabel('bottom', 'Wavelength, nm', **self.styles)
        self.graph.setLabel('left', 'Intensity', **self.styles)

    def load(self, measurements:list):
        self.measurements = measurements
        self.draw()
        
    @dispatch(Measurement)                  
    def draw(self, measurement:Measurement):
        pen = pg.mkPen(measurement.pen_color) if measurement.pen_enabled else None
        item_plot = self.graph.plot(
            x=measurement.data.index.values,
            y=measurement.data['Y'].to_numpy(),
            pen=pen,
            symbol=measurement.symbol,
            symbolPen=pg.mkPen(measurement.pen_color),
            symbolBrush=pg.mkBrush(measurement.symbol_brush_color),
            symbolSize=measurement.symbol_size,
            name=measurement.name
        )
        self.items_plot.append(item_plot)
    
    @dispatch()
    def draw(self):
        self.clear()
        for (index, measurement) in enumerate(self.measurements):
            if measurement.enabled:
                pen_index = np.random.randint(0, 6)
                pen_color = us.colors[pen_index]
                self.measurements[index].set_pen_color(pen_color) 
                self.draw(measurement)
        
    def clear(self):
        for item in self.items_plot:
            self.graph.removeItem(item)
        while len(self.items_plot):
            self.items_plot.pop()
    
    def dragEnterEvent(self, e):
        e.accept()
    
    #!JSCH -> Accept txt only, otherwise do sth
    def dropEvent(self, e):
        view = e.source()
        self.clear()
        for (index, measurement) in enumerate(self.measurements):
            self.measurements[index].set_enabled(False)
        for item in view.selectedIndexes():
            path = view.model().filePath(item)
            path_ending = path.split('.')[-1]
            filename = path.split('/')[-1]
            if path_ending == 'txt':
                for (index, measurement) in enumerate(self.measurements):
                    if filename == measurement.filename:
                        self.measurements[index].set_enabled(True)
                    
        self.draw()
        e.accept()
        

class WidgetGraphCustomization(QWidget):
    
    def __init__(self, measurements:Measurement, *args, **kwargs):
        super().__init__(*args, **kwargs)
        loadUi("UI/ui_settings_graph_data.ui", self)
        
        self.raw_measurements = measurements
        print(self.raw_measurements[0])
        self.model = QStandardItemModel()
        self.labels = ["title", "window width", "peak1", "peak2", "pen", "pen_enable", "symbol", "symbol_fill_color", "symbol_size", "enable"]
        self.model.setHorizontalHeaderLabels(self.labels)
        
        self.tree.setModel(self.model)
        self.create_row(index_row = 0, measurement=Measurement(r"D:\Semestr10\PBL\Program\PBL\Data\pomiar1\CMK 9 - 1mg-ml.txt", encoding="utf-16", separator="\t"))
        
    def create_row(self, index_row, measurement:Measurement):
        self.button_pen = QPushButton()
        self.button_symbol_fill = QPushButton()
        self.model.appendRow([QStandardItem() for i in self.labels])
        
        self.measurement = measurement
        self.row = SettingsRow(self.measurement)
        self.row_list = self.row.get_widgets()
        
        for (index_widget, widget) in enumerate(self.row_list):
            self.tree.setIndexWidget(self.model.index(index_row, index_widget), widget)
            
        


class SettingsRow(QObject):
    
    def __init__(self, measurement:Measurement, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.le_title = QLineEdit("titlex")
        self.le_window_width = QLineEdit("3")
        self.le_peak1 = QLineEdit("373")
        self.le_peak2 = QLineEdit("384")
        self.button_pen = QPushButton()
        self.chb_pen_enable = QCheckBox()
        self.cob_symbol = QComboBox()
        self.button_symbol_fill = QPushButton()
        self.le_symbol_size = QLineEdit("7")
        self.chb_enable = QCheckBox()
        
        self.button_pen.clicked.connect(self.test)
    def test(self):
        print("test")
        
    def get_widgets(self) -> list:
        list_widget = []
        list_widget.append(self.le_title)
        list_widget.append(self.le_window_width)
        list_widget.append(self.le_peak1)
        list_widget.append(self.le_peak2)
        list_widget.append(self.button_pen)
        list_widget.append(self.chb_pen_enable)
        list_widget.append(self.cob_symbol)
        list_widget.append(self.button_symbol_fill)
        list_widget.append(self.le_symbol_size)
        list_widget.append(self.chb_enable)
        return list_widget
    

# Create objects as rows->widget_event=update object's measurement-> get all new measuremnts and emit new measurments list

        
        