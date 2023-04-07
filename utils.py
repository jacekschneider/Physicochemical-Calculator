import numpy as np
import pandas as pd
import pyqtgraph as pg
import re
from PyQt6.QtCore import QCoreApplication
from pathlib import Path
from sklearn.linear_model import LinearRegression ## pip install numpy scikit-learn statsmodels
from math import log10
from dataclasses import dataclass, field

def closest_value(input_list, input_value):
    arr = np.asarray(input_list)
    i = (np.abs(arr - input_value)).argmin()
    return arr[i]

def tr(text_to_translate):
    return QCoreApplication.translate("@default", text_to_translate)

def verify(data:pd.DataFrame):
    assert not data.empty
    for column, dtype in data.dtypes.items():
        dtype_str = str(dtype)
        assert ("int" in dtype_str) | ("float" in str(dtype))
    return data
    

def read_single_file(path: str, encoding: str = 'UTF-16', separator: str = '\t', ignore_X: bool = True) -> pd.DataFrame:
    raw = pd.read_csv(path, encoding=encoding, sep=separator)
    Yval = raw[raw.columns[raw.columns.str.startswith('Y')]]
    # filtering out Y values, excluding every other column because of bad data
    # may heve to be removed
    Yval = Yval[Yval.columns[1::2]]
    Yval = Yval.mean(axis=1)
    if ignore_X:
        return Yval
    Xval = raw['X']
    combined = pd.concat([Xval,Yval],axis=1, keys=['X','Y'])
    return combined

def get_concentrations(files:list) -> list:
    concentrations = []
    for file in files:
        filename = file.split('\\')[-1] # the last element should be the filename
        filename = filename.replace('.txt','').replace(',','.')
        # assuming there may be numbers in the filename, but not after the concentration
        con = re.findall('\d+(?:\.\d+)?', filename)[-1] # extracts floats and integers
        concentrations.append(float(con))
    return concentrations


def get_data(dirpath: str, encoding: str = 'UTF-16', separator: str = '\t')-> pd.DataFrame:
    files:list[str] = [str(file)for file in list(Path(dirpath).glob('*.txt'))]
    concentrations: list[float] = get_concentrations(files)
    files = [name for name,_ in sorted(zip(files,concentrations), key= lambda key: key[1], reverse=False)]
    concentrations.sort(reverse=False)
    data = read_single_file(files.pop(0),encoding=encoding, separator=separator, ignore_X=False)
    for file in files:
        data = pd.concat([data,read_single_file(file,encoding,separator,ignore_X=True)], axis=1)
    data.index = data['X']
    data = data.drop('X',axis=1)
    names = [str(i) for i in concentrations]
    data.columns = names
    return data

def get_peaks(data: pd.DataFrame, peak1: int = 373, peak2: int = 384, window: int = 3) -> pd.DataFrame:
    P1_window_low, P1_window_high = peak1 - window//2, peak1 + window//2
    P2_window_low, P2_window_high = peak2 - window//2, peak2 + window//2
    P1, P2 = data.loc[P1_window_low:P1_window_high], data.loc[P2_window_low:P2_window_high]

    peak1_max, peak2_max = P1.max(),P2.max()
    peak1_max_id, peak2_max_id = P1.idxmax(), P2.idxmax()
    # indexes of found values are needed for marking them on a plot
    # for data preview concentrations are saved in the column names
    peaks = pd.DataFrame({'Peak 1' : peak1_max,
                          'Peak 2' : peak2_max,
                          'Peak 1 ID' : peak1_max_id,
                          'Peak 2 ID' : peak2_max_id})

    return peaks.T

def prepare_regression_data(data: pd.DataFrame) -> pd.DataFrame:
    concentrations: list[float] = [log10(float(i)) for i in data.columns]
    relatives = data.loc['Peak 1']/data.loc['Peak 2']
    regression_data = pd.DataFrame({'Y': relatives,
                                    'X': concentrations})
    return regression_data.T

def CAC(model1: LinearRegression,model2: LinearRegression):
    '''Calculates CAC based on the parameters of two linear models\n
    Important! returns CAC in log10 scale'''
    b1, b2 = model1.intercept_, model2.intercept_
    a1, a2 = model1.coef_, model2.coef_
    return (b2-b1)/(a1-a2)

def get_models(data: pd.DataFrame) -> pd.DataFrame:
    def RMSE(y,ypredict):
        mse = np.square(np.subtract(y,ypredict))
        rmse = np.sqrt(np.sum(mse)/len(y))
        return rmse
    
    X = data.loc['X'].to_numpy().reshape((-1, 1)) # the reshape is required
    Y = data.loc['Y'].to_numpy()
    model_data = {}
    for i in range(2,len(X)-2): # covers all possible models
        x1,x2 = X[:i],X[i:]
        y1,y2 = Y[:i],Y[i:]
        model1, model2 = LinearRegression().fit(x1,y1), LinearRegression().fit(x2,y2)
        prediction1, prediction2 = model1.predict(x1), model2.predict(x2)
        rmse1, rmse2 = RMSE(y1,prediction1), RMSE(y2,prediction2)
        rsq1, rsq2 = model1.score(x1,y1), model2.score(x2,y2) # coeficient of determination R^2
        model_data[i] = {'RMSE':rmse1+rmse2, 'R2':rsq1+rsq2, 'model1':model1, 'model2':model2}
        # model_data[i] = {'RMSE':rmse1+rmse2, 'R2':rsq1+rsq2, 'models':(model1, model2)} # Potentialy easier to manage
    model_data = pd.DataFrame(model_data).T # swapping the usual conversion because of needing columns to be numeric
    model_data = model_data.astype({'R2': 'Float64', 'RMSE': 'Float64'})
    return model_data 

def choose_models_frame_id(model_data: pd.DataFrame) -> tuple[int,int]:
    '''Finds the best models and returns the row id as a tuple\n
    Made this way to be easily able to both find the models in a dataframe and split the point'''
    best_R2 = model_data['R2'].idxmax()
    best_RMSE = model_data['RMSE'].idxmin()
    return best_R2,best_RMSE

def example_plot(regdata: pd.DataFrame, model_frame_id: int, model1: LinearRegression, model2: LinearRegression):
    def abline(slope, intercept):
        """Plot a line from slope and intercept"""
        axes = plt.gca()
        x_vals = np.array(axes.get_xlim())
        y_vals = intercept + slope * x_vals
        plt.plot(x_vals, y_vals, '--')

    ## data plots
    X = regdata.loc['X'].to_numpy()
    Y = regdata.loc['Y'].to_numpy()
    M1b0, M1b1 = model1.intercept_,model1.coef_
    M2b0, M2b1 = model2.intercept_,model2.coef_

    x1,x2 = X[:model_frame_id], X[model_frame_id:]
    y1,y2 = Y[:model_frame_id], Y[model_frame_id:]
    plt.plot(x1,y1,'bo')
    plt.plot(x2,y2,'ro')
    abline(M1b1,M1b0)
    abline(M2b1,M2b0)
    ## CAC
    xcor = CAC(model1, model2)
    ycor = M1b1*xcor + M1b0
    plt.plot(xcor, ycor, 'g*')
    ## The plot is not scaled properly
    plt.show()

colors = "rgbwymc"
pens = []
for color in colors:
    pens.append(pg.mkPen(color))

@dataclass
class Measurement:
    path : str
    peak1 : int = 373
    peak2 : int = 384
    window_width : int = 3
    encoding : str = 'UTF-16'
    separator : str = '\t'
    method : str = 'RMSE'

    data : pd.DataFrame = field(init=False)
    concentrations : list = field(init = False)
    peaks : pd.DataFrame = field(init=False)
    regdata : pd.DataFrame = field(init=False)
    modeldata : pd.DataFrame = field(init=False)
    R2_index : int = field(init=False)
    RMSE_index : int = field(init=False)

    bestmodels : tuple[LinearRegression] = field(init=False)
    CAC : float = field(init=False)
    

    pen_color : list = field(default_factory = lambda:[255, 255, 255])
    symbol : str = "o"
    symbol_pen_color : list = field(default_factory = lambda:[255, 255, 255])
    symbol_brush_color : list = field(default_factory = lambda:[255, 255, 255])
    symbol_size : int = 7
    name : str = field(init=False, default="NoName")

    @staticmethod
    def read_single_file(path : str, encoding : str = 'UTF-16', separator : str = '\t', ignore_X : bool = True) -> pd.DataFrame:
        raw = pd.read_csv(path, encoding=encoding, sep=separator)
        Yval = raw[raw.columns[raw.columns.str.startswith('Y')]]
        # filtering out Y values, excluding every other column because of bad data
        # may heve to be removed
        Yval = Yval[Yval.columns[1::2]]
        Yval = Yval.mean(axis=1)
        if ignore_X:
            return Yval
        Xval = raw['X']
        combined = pd.concat([Xval,Yval],axis=1, keys=['X','Y'])
        return combined

    @staticmethod
    def get_concentrations(files : list) -> list:
        concentrations = []
        for file in files:
            filename = file.split('\\')[-1] # the last element should be the filename
            filename = filename.replace('.txt','').replace(',','.')
            # assuming there may be numbers in the filename, but not after the concentration
            con = re.findall('\d+(?:\.\d+)?', filename)[-1] # extracts floats and integers
            concentrations.append(float(con))
        return concentrations

    def load_data(self)-> pd.DataFrame:
        files:list[str] = [str(file)for file in list(Path(self.path).glob('*.txt'))]
        concentrations: list[float] = self.get_concentrations(files)
        files = [name for name,_ in sorted(zip(files,concentrations), key= lambda key: key[1], reverse=False)]
        concentrations.sort(reverse=False)
        data = read_single_file(files.pop(0),encoding=self.encoding, separator=self.separator, ignore_X=False)
        for file in files:
            data = pd.concat([data, self.read_single_file(file,self.encoding,self.separator,ignore_X=True)], axis=1)
        data.index = data['X']
        data = data.drop('X', axis=1)
        names = [str(i) for i in concentrations]
        data.columns = names

        self.data = data
        self.concentrations = concentrations

    def get_peaks(self):
        P1_window_low, P1_window_high = self.peak1 - self.window_width//2, self.peak1 + self.window_width//2
        P2_window_low, P2_window_high = self.peak2 - self.window_width//2, self.peak2 + self.window_width//2
        P1, P2 = self.data.loc[P1_window_low:P1_window_high], self.data.loc[P2_window_low:P2_window_high]

        peak1_max, peak2_max = P1.max(), P2.max()
        peak1_max_id, peak2_max_id = P1.idxmax(), P2.idxmax()
        # indexes of found values are needed for marking them on a plot
        # for data preview concentrations are saved in the column names
        peaks = pd.DataFrame({'Peak 1' : peak1_max,
                              'Peak 2' : peak2_max,
                              'Peak 1 ID' : peak1_max_id,
                              'Peak 2 ID' : peak2_max_id})
        self.peaks = peaks.T

    def prepare_regression_data(self):
        concentrations: list = [log10(float(i)) for i in self.concentrations]
        relatives = self.peaks.loc['Peak 1']/self.peaks.loc['Peak 2']
        regression_data = pd.DataFrame({'Y': relatives,
                                        'X': concentrations})
        self.regdata =  regression_data.T
        
    def get_models(self):
        def RMSE(y,ypredict):
            mse = np.square(np.subtract(y,ypredict))
            rmse = np.sqrt(np.sum(mse)/len(y))
            return rmse
        
        X = self.regdata.loc['X'].to_numpy().reshape((-1, 1)) # the reshape is required
        Y = self.regdata.loc['Y'].to_numpy()

        model_data = {}
        for i in range(2,len(X)-2): # covers all possible models
            x1,x2 = X[:i],X[i:]
            y1,y2 = Y[:i],Y[i:]
            model1, model2 = LinearRegression().fit(x1,y1), LinearRegression().fit(x2,y2)
            prediction1, prediction2 = model1.predict(x1), model2.predict(x2)
            rmse1, rmse2 = RMSE(y1,prediction1), RMSE(y2,prediction2)
            rsq1, rsq2 = model1.score(x1,y1), model2.score(x2,y2) # coeficient of determination R^2
            model_data[i] = {'RMSE':rmse1+rmse2, 'R2':rsq1+rsq2, 'model1': model1, 'model2': model2}
            # model_data[i] = {'RMSE':rmse1+rmse2, 'R2':rsq1+rsq2, 'models':(model1, model2)} # Potentialy easier to manage
        model_data = pd.DataFrame(model_data).T # swapping the usual conversion because of needing columns to be numeric
        model_data = model_data.astype({'R2': 'Float64', 'RMSE': 'Float64'})
        self.modeldata =  model_data

    def choose_models_frame_id(self):
        '''Finds the best models and returns the row id as a tuple\n
        Made this way to be easily able to both find the models in a dataframe and split the point'''
        self.R2_index = self.modeldata['R2'].idxmax()
        self.RMSE_index = self.modeldata['RMSE'].idxmin()

    def choose_best_model(self):
        match self.method:
            case 'RMSE':
                self.bestmodels = self.modeldata.loc[self.RMSE_index ,['model1','model2']]
            case 'R2':
                self.bestmodels = self.modeldata.loc[self.R2_index ,['model1','model2']]
            case _:
                raise Exception("Incorrect model fit method")
            
    def get_CAC(self):
        '''Calculates CAC based on the parameters of two linear models\n
        Important! returns CAC in log10 scale'''
        model1 = self.bestmodels[0]
        model2 = self.bestmodels[1]
        
        b1, b2 = model1.intercept_, model2.intercept_
        a1, a2 = model1.coef_, model2.coef_
        return (b2-b1)/(a1-a2)
        

    def example_plot(self):
        def abline(slope, intercept):
            """Plot a line from slope and intercept"""
            axes = plt.gca()
            x_vals = np.array(axes.get_xlim())
            y_vals = intercept + slope * x_vals
            plt.plot(x_vals, y_vals, '--')

        ## data plots
        X = self.regdata.loc['X'].to_numpy()
        Y = self.regdata.loc['Y'].to_numpy()
        match self.method:
            case 'RMSE':
                model_frame_id = self.RMSE_index
            case 'R2':
                model_frame_id = self.R2_index
            case _:
                raise Exception("Incorrect model fit method")

        model1 = self.bestmodels[0]
        model2 = self.bestmodels[1]

        M1b0, M1b1 = model1.intercept_,model1.coef_
        M2b0, M2b1 = model2.intercept_,model2.coef_

        x1,x2 = X[:model_frame_id], X[model_frame_id:]
        y1,y2 = Y[:model_frame_id], Y[model_frame_id:]

        plt.plot(x1,y1,'bo')
        plt.plot(x2,y2,'ro')
        abline(M1b1,M1b0)
        abline(M2b1,M2b0)
        ## CAC
        xcor = self.CAC
        ycor = M1b1*xcor + M1b0
        plt.plot(xcor, ycor, 'g*')
        ## The plot is not scaled properly
        plt.show()
        
    def calculate(self):
        self.load_data()
        self.get_peaks()
        self.prepare_regression_data()
        self.get_models()
        self.choose_models_frame_id()
        self.choose_best_model()
        self.CAC = self.get_CAC()

    def __post_init__(self):
        self.calculate()


    
if __name__ == '__main__': # for testing purposes
    import matplotlib.pyplot as plt
    uno = Measurement('Data\\pomiar1')
    uno.example_plot()

    duo = Measurement('Data\\pomiar2')
    duo.example_plot()
    
    # data = get_data('Data\\pomiar1')
    # peaks = get_peaks(data)
    # regdata = prepare_regression_data(peaks) # this can be plotted
    # model_data = get_models(regdata)
    # R2val, RMSEval = choose_models_frame_id(model_data)
    # model1,model2 = model_data.loc[RMSEval,['model1','model2']]
    # example_plot(regdata, RMSEval, model1,model2)