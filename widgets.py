import math
import numpy as np
import pyqtgraph as pg
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QGridLayout, QDial, QLineEdit, QLabel, QPushButton, QFileDialog
from PyQt6.QtCore import pyqtSignal as Signal, QThread
from PyQt6.QtGui import QIntValidator
from PyQt6.uic.load_ui import loadUi
from workers import LoadWorker
from utils import get_data

        
            
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
        self.graph.showGrid(x=True, y=True)
    
    def load_data(self, path:str):
        data = get_data(path)
        data.dropna(how="all", axis="index", inplace=True)
        x = data.index.values
        for column in data:
            title = column
            y= data[column].values
            self.draw(x, y, title)
              
    def draw(self, x:np.array, y:np.array, title:str):
        color = np.random.randint(255, size=(3))
        print(color)
        self.graph.plot(x,y, pen=None, symbol='o', symbolPen=pg.mkPen(color), symbolBursh=pg.mkBrush(180,180,180))