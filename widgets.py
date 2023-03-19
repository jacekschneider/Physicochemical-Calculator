import math
import numpy as np
import pyqtgraph as pg
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QGridLayout, QDial, QLineEdit, QLabel, QPushButton, QFileDialog
from PyQt6.QtCore import pyqtSignal as Signal, QThread
from PyQt6.QtGui import QIntValidator
from PyQt6.uic.load_ui import loadUi
from workers import LoadWorker
from utils import closest_value, tr

        
            
class WidgetNavigation(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        loadUi("UI/ui_navigation.ui", self)
        
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