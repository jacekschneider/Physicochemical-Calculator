import numpy as np
import pandas as pd
import os
import copy
from math import log10
from pathlib import Path
from multipledispatch import dispatch
from utils import Measurement, RMSE
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import pyqtSlot as Slot, pyqtSignal as Signal, QObject
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from sklearn.linear_model import LinearRegression
from tempfile import NamedTemporaryFile
import pyqtgraph.exporters

class ReportWorker(QObject):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.offset = -55
        # the colors chould be adjusted
        self.divider_banner_color = (0.1, 0.44, 0.69)
        self.divider_text_color = (1,1,1)
        self.base_text_color = (0,0,0)

    def set_measurements(self, measurements:list):
        self.measurements = measurements
        self.min_concentration = min([i.concentration for i in self.measurements])
        self.max_concentration = max([i.concentration for i in self.measurements])

    ## both plots will be required
    def set_CAC_plot(self, exported_image):
        self.CAC_plot = exported_image

    def set_dataview_plot(self, exported_image):
        self.dataview_plot = exported_image
        
    def generate(self):
        file_path, selected_filter = QFileDialog.getSaveFileName(
            caption="Select a directory",
            directory=str(Path().absolute()),
            filter="PDF File (*.pdf)"
        )
        if file_path:
            canvas = Canvas(file_path, pagesize = A4)
            page_width, page_height = A4
            plot_width, plot_height = 500, 300
            font = "Times-Roman"
            

            def divider(string: str):
                canvas.setFillColorRGB(*self.divider_banner_color)
                canvas.setStrokeColorRGB(*self.divider_banner_color)
                canvas.rect(40 , page_height + self.offset, width = page_width - 80, height = 15, fill=True)
                canvas.setFillColorRGB(*self.divider_text_color)
                canvas.setStrokeColorRGB(*self.base_text_color)
                text = canvas.beginText(page_width/6 - 35, page_height + self.offset + 4)
                text.setFont(font, 12)
                text.textLine(string)
                canvas.drawText(text)
                canvas.setFillColorRGB(*self.base_text_color)
                self.offset -= 14
                # canvas.stringWidth(string, font, 12)
            
            def paragraph(title: str, *args: str):
                if abs(self.offset - (14 + 14.6*len(args))) >= page_height:
                    canvas.showPage()
                    self.offset = -55
                divider(title)
                
                text = canvas.beginText(50, page_height + self.offset)
                for line in args:
                    text.textLine(line)
                self.offset -= 14.6*len(args) + 6
                canvas.drawText(text)
            
            def draw_plot(title: str, exported_plot):
                if abs(self.offset - (plot_height+10)) >= page_height:
                    canvas.showPage()
                    self.offset = -55
                with NamedTemporaryFile("r+b", delete=False, prefix="CAC_calculator", suffix='.png') as pl:
                    exported_plot.parameters()['width'] = plot_width
                    exported_plot.export(pl.name)
                    divider(title)
                    canvas.drawImage(pl.name, 50, page_height - plot_height + self.offset + 10, width=plot_width, height=plot_height)
                    self.offset -= (plot_height+10)
                    TEMP_FILENAME = pl.name
                # Using os.remove because the auto delete
                # caused OSError: Cannot open resource
                os.remove(TEMP_FILENAME)
                del TEMP_FILENAME

            # draw_plot("CAC plot", self.CAC_plot) # example usecase

            divider("CAC plot")
            canvas.drawImage("sampleplot.png", 50, page_height - plot_height + self.offset, width=plot_width, height=plot_height) 
            self.offset -= plot_height

            paragraph("Sample text",
                    f"CAC: {0.088}",
                    f"Mimimum concentration in the experiment: {self.min_concentration}",
                    f"Maximum concentration in the experiment: {self.max_concentration}")
            
            divider("CAC plot")
            canvas.drawImage("sampleplot.png", 50, page_height - plot_height + self.offset, width=plot_width, height=plot_height) 
            self.offset -= plot_height
            
            # canvas.setTitle("CAC analysis")

            paragraph("Chosen model metrics",
                    f"Model parameters (y = ax + b) a: {0.088} b: {0.000011}",
                    f"Model Root Mean Square Error: {0.001}",
                    f"Model coeffcient of determiantion (R\u00b2): {1}",
                    f"Model coeffcient of determiantion (R\u00b2): {1}",
                    f"Model coeffcient of determiantion (R\u00b2): {1}",
                    f"Model coeffcient of determiantion (R\u00b2): {1}",
                    f"Model coeffcient of determiantion (R\u00b2): {1}",)
            canvas.save()
            # reinitialising the offset
            # otherwise multiple report generation using
            # the same instance of the class would start the text generation lower
            self.offset = -55 


class SettingsWorker(QObject):
    emit_measurements = Signal(list)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.measurements_raw:list[Measurement] = []
        self.measurements_edited:list[Measurement] = []
    
    @dispatch(str)
    def load(self, dirpath:str):
        self.measurements_raw.clear()
        files:list[str] = [str(file)for file in list(Path(dirpath).glob('*.txt'))]
        for file in files:
            measurement = Measurement(path=file, encoding="utf-16", separator="\t")
            self.measurements_raw.append(measurement)
            self.measurements_edited = copy.deepcopy(self.measurements_raw)
        self.emit_measurements.emit(self.measurements_edited)
        
    @dispatch(list)
    def load(self, measurements:list):
        self.measurements_edited = measurements
        self.emit_measurements.emit(self.measurements_edited)
        
    def get_measurements_raw(self)->list:
        return self.measurements_raw

    def get_measurements(self)->list:
        return self.measurements_edited

            
class CalculatorWorker(QObject):
    emit_RMSE = Signal(RMSE)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.measurements:list[Measurement] = []

    def load(self, measurements:list):
        self.measurements = measurements
        regression_data = self.__prepare_regression_data()
        model_data = self.__prepare_models(regdata=regression_data)
        R2val, RMSEval = self.__define_best(model_data=model_data)
        model1, model2 = model_data.loc[RMSEval,['model1','model2']]
        cac_data = self.__calculate_cac(model1, model2)
        rmse_data = RMSE(regression_data, RMSEval, cac_data)
        self.emit_RMSE.emit(rmse_data)

    def __prepare_regression_data(self)->pd.DataFrame:
        concentrations: list[float] = [log10(measurement.concentration) for measurement in self.measurements if measurement.enabled]
        relatives:list[float] = [float(measurement.peaks["Peak 1"]/measurement.peaks["Peak 2"]) for measurement in self.measurements if measurement.enabled]
        regression_data = pd.DataFrame({'Y': relatives,'X': concentrations})
        regression_data.sort_values('X', inplace=True)
        return regression_data.T
    
    def __prepare_models(self, regdata:pd.DataFrame)->pd.DataFrame:
        X = regdata.loc['X'].to_numpy().reshape((-1, 1)) # the reshape is required
        Y = regdata.loc['Y'].to_numpy()
        model_data = {}
        for i in range(2,len(X)-2): # covers all possible models
            x1,x2 = X[:i],X[i:]
            y1,y2 = Y[:i],Y[i:]
            model1, model2 = LinearRegression().fit(x1,y1), LinearRegression().fit(x2,y2)
            prediction1, prediction2 = model1.predict(x1), model2.predict(x2)
            rmse1, rmse2 = self.__calculate_rmse(y1,prediction1), self.__calculate_rmse(y2,prediction2)
            rsq1, rsq2 = model1.score(x1,y1), model2.score(x2,y2) # coeficient of determination R^2
            model_data[i] = {'RMSE':rmse1+rmse2, 'R2':rsq1+rsq2, 'model1':model1, 'model2':model2}
            # model_data[i] = {'RMSE':rmse1+rmse2, 'R2':rsq1+rsq2, 'models':(model1, model2)} # Potentialy easier to manage
        model_data = pd.DataFrame(model_data).T # swapping the usual conversion because of needing columns to be numeric
        model_data = model_data.astype({'R2': 'Float64', 'RMSE': 'Float64'})
        return model_data

    def __define_best(self, model_data:pd.DataFrame)->tuple:
        '''Finds the best models and returns the row id as a tuple\n
        Made this way to be easily able to both find the models in a dataframe and split the point'''
        best_R2 = model_data['R2'].idxmax()
        best_RMSE = model_data['RMSE'].idxmin()
        return best_R2,best_RMSE
        
    def __calculate_rmse(self, y, ypredict):
        mse = np.square(np.subtract(y,ypredict))
        rmse = np.sqrt(np.sum(mse)/len(y))
        return rmse
    
    def __calculate_cac(self, model1:LinearRegression, model2:LinearRegression)->dict:
        cac_data = {}
        b1, b2 = model1.intercept_, model2.intercept_
        a1, a2 = model1.coef_, model2.coef_
    
        cac_data["b1"] = b1
        cac_data["b2"] = b2
        cac_data["a1"] = a1
        cac_data["a2"] = a2
        
        cac_x = (b2-b1)/(a1-a2)
        cac_y = a1*cac_x + b1
        
        cac_data["cac_x"] = cac_x
        cac_data["cac_y"] = cac_y
    
        return cac_data
    

        
        
        