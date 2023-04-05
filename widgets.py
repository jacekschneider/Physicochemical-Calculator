import numpy as np
import pyqtgraph as pg
import pathlib
from PyQt6.QtWidgets import QWidget, QFileDialog, QFileIconProvider
from PyQt6.QtCore import pyqtSignal as Signal, QDir
from PyQt6.QtGui import  QFileSystemModel
from PyQt6.uic.load_ui import loadUi
from utils import get_data, pens, read_single_file, get_concentrations
import utils as us

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
        
        self.graph.showGrid(x=True, y=True)
        # self.legend = self.graph.addLegend(labelTextColor="w", labelTextSize="12")
        # self.legend.anchor((0,0),(0.7,0.1))
        self.styles = {'color':'white', 'font-size':'15px'}
        self.graph.setLabel('bottom', 'logC, mg/ml', **self.styles)
        self.graph.setLabel('left', 'I1/I3', **self.styles)
    
    def load(self, path:str):
        self.clear()
        data = us.get_data(path)
        peaks = us.get_peaks(data)
        regdata = us.prepare_regression_data(peaks) # this can be plotted
        model_data = us.get_models(regdata)
        R2val, RMSEval = us.choose_models_frame_id(model_data)
        model1,model2 = model_data.loc[RMSEval,['model1','model2']]
        
        self.draw(regdata, RMSEval, model1, model2)
        
    def draw(self, regdata: pd.DataFrame, model_frame_id: int, model1: LinearRegression, model2: LinearRegression):

        ## data plots
        X = regdata.loc['X'].to_numpy()
        Y = regdata.loc['Y'].to_numpy()
        M1b0, M1b1 = model1.intercept_,model1.coef_
        M2b0, M2b1 = model2.intercept_,model2.coef_

        x1,x2 = X[:model_frame_id], X[model_frame_id:]
        y1,y2 = Y[:model_frame_id], Y[model_frame_id:]
        
        self.items_plot.append(self.graph.plot(x1, y1, pen=None, symbol='o', symbolPen=pg.mkPen("b"),symbolBrush=pg.mkBrush("b"),  symbolSize=7))
        self.items_plot.append(self.graph.plot(x2, y2, pen=None, symbol='o', symbolPen=pg.mkPen("r"),symbolBrush=pg.mkBrush("r"),  symbolSize=7))
        self.abline(M1b1,M1b0)
        self.abline(M2b1,M2b0)
        ## CAC
        xcor = us.CAC(model1, model2)
        ycor = M1b1*xcor + M1b0
        self.items_plot.append(self.graph.plot(xcor, ycor, pen=None, symbol='d', symbolPen=pg.mkPen("g"),symbolBrush=pg.mkBrush("g"),  symbolSize=9))
        pos_x = round(xcor[0], 3)
        pos_y = round(ycor[0], 3)
        item_text = pg.TextItem(text="CAC = [{}, {}]".format(pos_x, pos_y), color=(0, 0, 0), border=pg.mkPen((0, 0, 0)), fill=pg.mkBrush("g"), anchor=(0, 0))
        item_text.setPos(xcor[0], ycor[0])
        self.items_text.append(item_text)
        self.graph.addItem(item_text)
        
        
        
    def abline(self, slope, intercept):
        axes = self.graph.getAxis('bottom')
        x_vals = np.array(axes.range)
        y_vals = intercept + slope * x_vals
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