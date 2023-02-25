import sys
import pandas as pd
import qdarktheme
import pyqtgraph as pg
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QLabel, QPushButton, QFileDialog, QLineEdit, QVBoxLayout, QHBoxLayout, QDial
from PyQt6.QtGui import QIcon
from pathlib import Path
import numpy as np
import math


class GraphWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path_data = ""
        self.x = []
        self.y = []
        self.dy = []
        self.points = []
        # Set options
        layout_main = QGridLayout(self)
        layout_main.setContentsMargins(20, 20, 0, 20)
        self.setMinimumSize(800, 600)
        self.setLayout(layout_main)
        
        # Prepare widgets
        self.widget_graph = pg.PlotWidget(self)
        self.widget_graph.setBackground('k')
        self.pen_white_2 = pg.mkPen(color=(255, 255, 255), width=2)
        self.pen_yellow_1 = pg.mkPen(color=(255, 255, 0), width=1)
        self.pen_red_2 = pg.mkPen(color=(255, 0, 0), width=2)

        self.widget_graph.setTitle("Example data", color="w", size="15pt")
        self.styles = {'color':'white', 'font-size':'15px'}
        self.widget_graph.setLabel('left', 'y', **self.styles)
        self.widget_graph.setLabel('bottom', 'x', **self.styles)
        self.widget_graph.showGrid(x=True, y=True)
        self.widget_graph.addLegend()
        
        # Add widgets to the layout
        layout_main.addWidget(self.widget_graph)
        
    def plot(self, x, y, pen, name):
        self.widget_graph.plot(x, y, pen=pen, name=name) 
    
    def plot_point(self, x:float, y:float):
        self.points.append(self.widget_graph.plot(x, y, pen=None, symbol='o', symbolPen=self.pen_red_2, clickable=True))

    def delete_points(self):
        while not len(self.points) == 0:
            self.widget_graph.removeItem(self.points.pop())
            
    def update(self, path:str):
        self.path_data = path
        data = pd.read_excel(self.path_data)
        columns = data.columns.values.tolist()
        self.widget_graph.setLabel('left', columns[1], **self.styles)
        self.widget_graph.setLabel('bottom', columns[0], **self.styles)
        self.x = data.iloc[:, 0]
        self.y = data.iloc[:, 1]
        x_prev = 0
        y_prev = 0
        for (x, y) in zip(self.x, self.y):
            try:
                self.dy.append((y - y_prev)/(x - x_prev))
            except ZeroDivisionError:
                self.dy.append(0)
            x_prev = x
            y_prev = y
        self.plot(self.x, self.y, self.pen_white_2, "y")
        self.plot(self.x, self.dy, self.pen_yellow_1, "dy")
        
    def get(self, option:str):
        if option == "x":
            return self.x
        elif option == "y":
            return self.y
        elif option == "dy":
            return self.dy
    
        

class PointSelectionWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        layout_main = QGridLayout()
        self.setLayout(layout_main)
        self.setMaximumSize(400, 200)
        
        self.widget_dial = QDial()
        self.widget_label_derrivative = QLabel("Derrivative value")
        self.widget_lineedit_derrivative = QLineEdit("1")
        self.widget_lineedit_derrivative.setMaximumWidth(100)
        
        layout_main.addWidget(self.widget_dial, 0,0)
        layout_main.addWidget(self.widget_label_derrivative, 1, 0)
        layout_main.addWidget(self.widget_lineedit_derrivative, 2, 0)
        
    def set_dial(self, min, max):
        self.widget_dial.setMinimum(min)
        self.widget_dial.setMaximum(max)
        
    def set(self, value):
        self.widget_dial.setValue(int(value))
        self.widget_lineedit_derrivative.setText(str(value))
        
        
class DataLoadWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        layout_main = QGridLayout()
        self.setLayout(layout_main)
        self.setMaximumSize(400, 100)

        # Widgets
        self.widget_button_fbrowse = QPushButton("Load data")
        self.widget_button_fbrowse.setFixedSize(80, 30)
        self.widget_label_filepath = QLabel('File: ')
        self.widget_label_filepath.setFixedHeight(20)
        self.widget_lineedit_filepath = QLineEdit()
        self.widget_lineedit_filepath.setFixedWidth(300)
        self.widget_lineedit_filepath.setReadOnly(True)
        
        layout_main.addWidget(self.widget_button_fbrowse, 0, 0, 1 , 1)
        layout_main.addWidget(self.widget_label_filepath, 2, 0)
        layout_main.addWidget(self.widget_lineedit_filepath, 3, 0 )
        
        
        
        
class CentralWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        layout_main = QGridLayout()
        self.setLayout(layout_main)
        
        self.widget_graph = GraphWidget()
        self.widget_load_data = DataLoadWidget()
        self.widget_point_selection = PointSelectionWidget()
        
        
        # Connections
        self.widget_load_data.widget_button_fbrowse.clicked.connect(self.open_file_dialog)
        self.widget_point_selection.widget_lineedit_derrivative.editingFinished.connect(self.line_edit_update)
        self.widget_point_selection.widget_dial.valueChanged.connect(self.dial_update)

        # Add widgets to the layout
        layout_main.addWidget(self.widget_graph, 0, 0, 6, 5)
        layout_main.addWidget(self.widget_load_data, 1, 6)
        layout_main.addWidget(self.widget_point_selection, 3, 6)

    #Data must be loaded!, Move Updates to Threads  
    
    def line_edit_update(self):
        derrivative_value = float(self.widget_point_selection.widget_lineedit_derrivative.text())
        self.update(derrivative_value)
        
    def dial_update(self):
        derrivative_value = self.widget_point_selection.widget_dial.value()
        self.update(derrivative_value)
    
    def update(self, derrivative_value):
        dy = self.widget_graph.get("dy")
        y = self.widget_graph.get("y")
        x = self.widget_graph.get("x")
        value = round(self.closest_value(dy, derrivative_value), 3)
        dy_np = np.round(np.array(dy), 3)
        dy_indices = np.where(dy_np == value)[0]
        
        self.widget_point_selection.set(value)
        self.widget_graph.delete_points()
        for dy_index in dy_indices:
            self.widget_graph.plot_point([x[dy_index]], [y[dy_index]])
        
    def closest_value(self, input_list, input_value):
        arr = np.asarray(input_list)
        i = (np.abs(arr - input_value)).argmin()
        return arr[i]

    def open_file_dialog(self):
        filename, ok = QFileDialog.getOpenFileName(
            self,
            caption="Select a File",
            # !JSCH -> change name
            filter="Some chemistry data (*.xlsx *.csv *.txt *.json)" 
        )
        if filename:
            path = Path(filename)
            self.widget_load_data.widget_lineedit_filepath.setText(str(path))
            self.widget_graph.update(str(path))
            
            value_min = math.floor(min(self.widget_graph.get("dy")))
            value_max = math.ceil(max(self.widget_graph.get("dy")))
            self.widget_point_selection.set_dial(value_min, value_max)
            
        

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set options
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowTitle("PBL Project")
        self.setWindowIcon(QIcon("icons/chemistry_1.png"))
        # qdarktheme.setup_theme()
        
        # Prepare Central Widget
        self.setCentralWidget(CentralWidget())

        self.show()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    sys.exit(app.exec())
    