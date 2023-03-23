import math
import numpy as np
import pyqtgraph as pg
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QGridLayout, QDial, QLineEdit, QLabel, QPushButton, QFileDialog
from PyQt6.QtCore import pyqtSignal as Signal, QThread
from PyQt6.QtGui import QIntValidator
from PyQt6.uic.load_ui import loadUi
from workers import LoadWorker
from utils import get_data, pens

        
            
class WidgetNavigation(QWidget):
    emit_path_folder = Signal(str)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        loadUi("UI/ui_navigation.ui", self)
        self.pb_load_data.clicked.connect(self.open_file_dialog)
        
    def open_file_dialog(self):
        path_folder = QFileDialog.getExistingDirectory(
            self,
            "Select Directory"
        )
        self.emit_path_folder.emit(path_folder)
        self.le_path.setText(path_folder)
        
class WidgetCAC(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        loadUi("UI/ui_cac.ui", self)
        self.graph.showGrid(x=True, y=True)
        
class WidgetData(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        loadUi("UI/ui_data.ui", self)
        
        #Graph Items
        self.items_plot = []
        
        self.graph.showGrid(x=True, y=True)
        self.legend = self.graph.addLegend(labelTextColor="w", labelTextSize="12")
        self.legend.anchor((0,0),(0.7,0.1))
        self.styles = {'color':'white', 'font-size':'15px'}
        self.graph.setLabel('bottom', 'Wavelength, nm', **self.styles)
        self.graph.setLabel('left', 'Intensity', **self.styles)

    def load(self, path:str):
        data = get_data(path)
        data.dropna(how="all", axis="index", inplace=True)
        x = data.index.values
        for (index, column) in enumerate(data):
            title = column
            y= data[column].values
            self.draw(x, y, title, pen_index=index)
              
    def draw(self, x:np.array, y:np.array, title:str, pen_index:int=0):
        item_plot = self.graph.plot(x,y,pen=None, symbol='o', symbolPen=pens[pen_index%len(pens)],symbolBrush=pg.mkBrush(0,0,0),  symbolSize=7, name=f"concentration = {title}")
        self.items_plot.append(item_plot)
        
    def clear(self):
        for item in self.items_plot:
            self.graph.removeItem(item)
        while len(self.items_plot):
            self.items_plot.pop()