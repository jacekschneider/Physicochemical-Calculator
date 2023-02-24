import sys
import pandas as pd
import qdarktheme
import pyqtgraph as pg
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QLabel, QPushButton, QFileDialog, QLineEdit, QVBoxLayout, QHBoxLayout, QDial
from PyQt6.QtGui import QIcon
from pathlib import Path



class GraphWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path_data = ""
        self.x = []
        self.y = []
        self.dy = []
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
        
        layout_main.addWidget(self.widget_button_fbrowse, 0, 0)
        layout_main.addWidget(self.widget_label_filepath, 1, 0)
        layout_main.addWidget(self.widget_lineedit_filepath, 2,0 )
        
        
class CentralWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        layout_main = QHBoxLayout()
        self.setLayout(layout_main)
        
        self.widget_graph = GraphWidget()
        self.widget_load_Data = DataLoadWidget()
        
        # Connections
        self.widget_load_Data.widget_button_fbrowse.clicked.connect(self.open_file_dialog)

        # Add widgets to the layout
        layout_main.addWidget(self.widget_graph)
        layout_main.addWidget(self.widget_load_Data)


    def open_file_dialog(self):
        filename, ok = QFileDialog.getOpenFileName(
            self,
            caption="Select a File",
            # !JSCH
            filter="Some chemistry data (*.xlsx *.csv *.txt *.json)" 
        )
        if filename:
            path = Path(filename)
            self.widget_load_Data.widget_lineedit_filepath.setText(str(path))
            self.widget_graph.update(str(path))
            
        

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
    