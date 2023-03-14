import math
import numpy as np
import pyqtgraph as pg
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QGridLayout, QDial, QLineEdit, QLabel, QPushButton, QFileDialog
from PyQt6.QtCore import pyqtSignal as Signal, QThread
from PyQt6.QtGui import QIntValidator
from workers import LoadWorker
from utils import closest_value, tr


class GraphWidget(QWidget):
    signal_load_requested = Signal(str)
    signal_load_finished = Signal(bool)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path_data = ""
        self.x = []
        self.y = []
        self.dy = []
        self.points = []
        self.traces = []
        self.texts = []
        # Set options
        layout_main = QGridLayout(self)
        layout_main.setContentsMargins(0, 5, 0, 5)
        self.setLayout(layout_main)
        
 
        # Prepare widgets
        self.widget_graph = pg.PlotWidget(self)
        self.widget_graph.setBackground('k')
        self.pen_white_2 = pg.mkPen(color=(255, 255, 255), width=2)
        self.pen_yellow_1 = pg.mkPen(color=(255, 255, 0), width=1)
        self.pen_red_2 = pg.mkPen(color=(255, 0, 0), width=2)

        self.styles = {'color':'white', 'font-size':'15px'}
        self.widget_graph.setLabel('left', 'y', **self.styles)
        self.widget_graph.setLabel('bottom', 'x', **self.styles)
        self.widget_graph.showGrid(x=True, y=True)
        self.widget_graph.addLegend()
        
        # Threads
        self.worker_load = LoadWorker()
        self.worker_load_thread = QThread()
        
        self.worker_load.signal_data_plot.connect(self.update)
        
        self.signal_load_requested.connect(self.worker_load.load)
        
        self.worker_load.moveToThread(self.worker_load_thread)
        self.worker_load_thread.finished.connect(self.worker_load_thread.deleteLater)
        self.worker_load_thread.start()
        
        # Add widgets to the layout
        layout_main.addWidget(self.widget_graph)
        
        self.retranslate()
        
    def plot(self, x, y, pen, name):
        self.traces.append(self.widget_graph.plot(x, y, pen=pen, name=name)) 
    
    def plot_point(self, x:list, y:list):
        pos_x = round(x[0], 3)
        pos_y = round(y[0], 3)
        self.points.append(self.widget_graph.plot(x, y, pen=None, symbol='o', symbolPen=self.pen_red_2, clickable=True))
        text = pg.TextItem(text="[{}, {}]".format(pos_x, pos_y), color=(0, 0, 0), border=pg.mkPen((0, 0, 0)), fill=pg.mkBrush((255, 255 , 255)))
        text.setPos(pos_x, pos_y)
        self.texts.append(text)
        self.widget_graph.addItem(text)

    def delete_points(self):
        while not len(self.points) == 0:
            self.widget_graph.removeItem(self.points.pop())
        while not len(self.texts) == 0:
            self.widget_graph.removeItem(self.texts.pop())
            
    def delete_traces(self):
        while not len(self.traces) == 0:
            self.widget_graph.removeItem(self.traces.pop())
            
    def clear(self):
        self.delete_traces()
        self.delete_points()
        self.retranslate()
        self.widget_graph.setLabel('left', 'y', **self.styles)
        self.widget_graph.setLabel('bottom', 'x', **self.styles)
        
            
    def request(self, path:str):
        self.signal_load_requested.emit(path)
            
    def update(self, data:dict):
        self.clear()
        self.x_label = data["x_label"]
        self.y_label = data["y_label"]
        self.x = data["x"]
        self.y = data["y"]
        self.dy = data["dy"]
        self.title = data["title"]
        self.widget_graph.setTitle(self.title, color="w", size="15pt")
        self.widget_graph.setLabel('left', self.y_label, **self.styles)
        self.widget_graph.setLabel('bottom', self.x_label, **self.styles)
        self.plot(self.x, self.y, self.pen_white_2, "y")
        self.plot(self.x, self.dy, self.pen_yellow_1, "dy")
        
        self.signal_load_finished.emit(True)
        
    def get(self, option:str):
        if option == "x":
            return self.x
        elif option == "y":
            return self.y
        elif option == "dy":
            return self.dy
        
    def retranslate(self):
        self.widget_graph.setTitle(tr("Data not loaded"), color="w", size="15pt")
        
        
class PointSelectionWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        layout_main = QGridLayout()
        self.setLayout(layout_main)
        self.setMaximumSize(400, 200)
        
        self.widget_dial = QDial()
        self.widget_label_derrivative = QLabel()
        self.widget_lineedit_derrivative = QLineEdit("0")
        self.widget_lineedit_derrivative.setValidator(QIntValidator())
        self.widget_lineedit_derrivative.setMaximumWidth(100)
        
        layout_main.addWidget(self.widget_dial, 0,0)
        layout_main.addWidget(self.widget_label_derrivative, 1, 0)
        layout_main.addWidget(self.widget_lineedit_derrivative, 2, 0)
        
        self.retranslate()
        
    def set_dial(self, min, max):
        self.widget_dial.setMinimum(min)
        self.widget_dial.setMaximum(max)
        
    def set(self, value):
        self.widget_dial.setValue(int(value))
        self.widget_lineedit_derrivative.setText(str(value))
    
    def retranslate(self):
        self.widget_label_derrivative.setText(tr("Derrivative value"))
        
            
class DataLoadWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        layout_main = QGridLayout()
        self.setLayout(layout_main)
        self.setMaximumSize(400, 100)

        # Widgets
        self.widget_button_fbrowse = QPushButton()
        self.widget_button_fbrowse.setFixedSize(100, 30)
        self.widget_button_clear = QPushButton()
        self.widget_button_clear.setDisabled(True)
        self.widget_button_clear.setFixedSize(100, 30)
        self.widget_label_filepath = QLabel()
        self.widget_label_filepath.setFixedHeight(20)
        self.widget_lineedit_filepath = QLineEdit()
        self.widget_lineedit_filepath.setFixedWidth(300)
        self.widget_lineedit_filepath.setReadOnly(True)
        
        layout_main.addWidget(self.widget_button_fbrowse, 0, 0, 1 , 1)
        layout_main.addWidget(self.widget_button_clear, 0, 1, 1 , 2)
        layout_main.addWidget(self.widget_label_filepath, 1, 0, 2, 2)
        layout_main.addWidget(self.widget_lineedit_filepath, 3, 0 , 4, 2)
        
        self.retranslate()
        
    def retranslate(self):
        self.widget_button_fbrowse.setText(tr("Load data"))
        self.widget_button_clear.setText(tr("Clear data"))
        self.widget_label_filepath.setText(tr("File:"))
             
             
class CentralWidget(QWidget):
    signal_status = Signal(str, int)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        layout_main = QGridLayout()
        self.setLayout(layout_main)
        
        self.widget_graph = GraphWidget()
        self.widget_load_data = DataLoadWidget()
        self.widget_point_selection = PointSelectionWidget()
        self.widget_point_selection.setDisabled(True)
        
        # Connections
        self.widget_load_data.widget_button_fbrowse.clicked.connect(self.open_file_dialog)
        self.widget_load_data.widget_button_clear.clicked.connect(self.clear)
        self.widget_point_selection.widget_lineedit_derrivative.editingFinished.connect(self.line_edit_update)
        self.widget_point_selection.widget_dial.valueChanged.connect(self.dial_update)
        self.widget_graph.signal_load_finished.connect(self.afterload)

        # Add widgets to the layout
        layout_main.addWidget(self.widget_graph, 0, 0, 6, 5)
        layout_main.addWidget(self.widget_load_data, 1, 6)
        layout_main.addWidget(self.widget_point_selection, 3, 6)

    #!JSCH -> Move Point update to Thread  
    
    def line_edit_update(self):
        derrivative_value = float(self.widget_point_selection.widget_lineedit_derrivative.text())
        self.update(derrivative_value)
        
    def dial_update(self):
        derrivative_value = self.widget_point_selection.widget_dial.value()
        self.update(derrivative_value)
        self.signal_status.emit(tr("Dial updated."), 1000)
    
    def afterload(self):
        value_min = math.floor(min(self.widget_graph.get("dy")))
        value_max = math.ceil(max(self.widget_graph.get("dy")))
        self.widget_point_selection.set_dial(value_min, value_max)
        self.widget_point_selection.setDisabled(False)
        self.widget_load_data.widget_button_clear.setDisabled(False)
        self.signal_status.emit(tr("Data loaded successfully."), 3000)
    
    def update(self, derrivative_value):
        dy = self.widget_graph.get("dy")
        y = self.widget_graph.get("y")
        x = self.widget_graph.get("x")
        value = round(closest_value(dy, derrivative_value), 3)
        dy_np = np.array(dy)
        dy_indices = np.where(dy_np == value)[0]
        
        self.widget_point_selection.set(value)
        self.widget_graph.delete_points()
        for dy_index in dy_indices:
            self.widget_graph.plot_point([x[dy_index]], [y[dy_index]])
        
    def clear(self):
        self.widget_point_selection.setDisabled(True)
        self.widget_graph.clear() 
        self.widget_load_data.widget_lineedit_filepath.setText("")
        self.widget_load_data.widget_button_clear.setDisabled(True)
        self.signal_status.emit(tr("Data removed successfully."), 3000)


    def open_file_dialog(self):
        filename, ok = QFileDialog.getOpenFileName(
            self,
            caption=tr("Select a File"),
            # !JSCH -> change name
            filter=tr("Polimer data")+" (*.xlsx *.csv *.txt *.json)" 
        )
        if filename:
            path = Path(filename)
            self.widget_load_data.widget_lineedit_filepath.setText(str(path))
            self.widget_graph.request(str(path))
            
    def retranslate(self):
        self.widget_graph.retranslate()
        self.widget_load_data.retranslate()
        self.widget_point_selection.retranslate()
            
            
