import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QFileDialog, QFileIconProvider
from PyQt6.QtCore import pyqtSignal as Signal, QDir
from PyQt6.QtGui import  QFileSystemModel
from PyQt6.uic.load_ui import loadUi
from utils import get_data, pens, read_single_file, get_concentrations

        
          
class WidgetNavigation(QWidget):
    emit_path_folder = Signal(str)
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
            "Select Directory"
        )
        self.emit_path_folder.emit(path_folder)
        self.le_path.setText(path_folder)
        self.view_files.setModel(self.model)
        root_index = self.model.index(QDir.cleanPath(path_folder))
        self.view_files.setRootIndex(root_index)
    
    def clear(self):
        self.le_path.setText("")
        self.view_files.setModel(None)
  
        
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
        self.clear()
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
    
    def dragEnterEvent(self, e):
        e.accept()
    
    #!JSCH -> Accept txt only, otherwise do sth
    def dropEvent(self, e):
        view = e.source()
        self.clear()
        for item in view.selectedIndexes():
            path = view.model().filePath(item)
            path_ending = path.split('.')[-1]
            if path_ending == 'txt':
                data = read_single_file(path, ignore_X=False)
                data.set_index('X', inplace=True)
                data.dropna(inplace=True)
                x = data.index.values
                y = data['Y'].values
                title = get_concentrations([path])[0]
                # JSCH! -> upgrade pen selection
                pen_index = np.random.randint(0, 6)
                self.draw(x, y, title, pen_index)
        e.accept()