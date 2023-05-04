import numpy as np
import pandas as pd
import pyqtgraph as pg
import re
import colorsys
from multipledispatch import dispatch
from PyQt6.QtCore import QCoreApplication, QSortFilterProxyModel
from pathlib import Path
from sklearn.linear_model import LinearRegression ## pip install numpy scikit-learn statsmodels
from math import log10
from dataclasses import dataclass, field
from PyQt6.QtGui import  QFileSystemModel

symbols = ["o", "t", "t1", "t2", "t3", "s", "p", "h", "star", "+", "d", "x"]

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
    Yval = Yval[1::2]
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

def choose_models_frame_id(model_data: pd.DataFrame) -> tuple:
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
    print(xcor)
    print(ycor)
    plt.plot(xcor, ycor, 'g*')
    ## The plot is not scaled properly
    plt.show()

def color_gen()->list:
    colors = colorsys.hsv_to_rgb(np.random.random(), 1, 1)
    return [x*255 for x in colors]

# index starts with 0
def gray_color_gen(index:int, size:int)->list:
    minimum = 50
    maximum = 255
    delta = round((maximum-minimum)/size)
    value_gray = delta*(index+1)+minimum
    if index+1 >= size:
        return [maximum for i in range(3)]
    else:
        return [value_gray for i in range(3)]

@dataclass(frozen=True)
class Measurement():
    
    path : str
    encoding : str = 'utf-8'
    separator : str = ','
    filename : str = field(init=False)
    concentration : float = field(init=False)
    data : pd.Series = field(init=False)
    
    peak1_raw : int = 373
    peak2_raw : int = 384
    window_width : int = 3
    peaks:dict = field(init=False)
    
    pen_color : list = field(default_factory=lambda:[0, 0, 0], init=False)
    pen_enabled : bool = field(default=False, init=False)
    symbol : str = field(default="o", init=False)
    symbol_brush_color : list = field(default_factory=lambda:[0, 0, 0], init=False)
    symbol_size : int = field(default=7, init=False)
    name : str = field(default="NoName", init=False,)
    displayed : bool = field(default=False, init=False)
    enabled : bool = field(default=False, init=False)
    
    def __post_init__(self):
        self.load_data()
        self.load_peaks()
        self.set_name("Concentration = {}".format(self.concentration))
        self.set_pen_color(color_gen())
        self.set_enabled(True)
        self.set_displayed(True)
    
    def load_data(self):

        filename = self.path.split('\\')[-1] # the last element should be the filename
        object.__setattr__(self, 'filename', filename)
        filename = filename.replace('.txt','').replace(',','.')
        # assuming there may be numbers in the filename, but not after the concentration
        con = re.findall('\d+(?:\.\d+)?', filename)[-1] # extracts floats and integers
        concentration= float(con)

        raw = pd.read_csv(self.path, encoding=self.encoding, sep=self.separator)
        Yval = raw[raw.columns[raw.columns.str.startswith('Y')]]
        # filtering out Y values, excluding every other column because of bad data
        # may heve to be removed
        Yval = Yval[Yval.columns[1::2]]
        Yval = Yval.mean(axis=1)
        Xval = raw['X']
        data = pd.concat([Xval,Yval],axis=1, keys=['X','Y'])
        data.dropna(inplace=True)
        object.__setattr__(self, 'data', data.set_index('X'))
        object.__setattr__(self, 'concentration', concentration)
        
    def load_peaks(self):
        P1_window_low, P1_window_high = self.peak1_raw - self.window_width//2, self.peak1_raw + self.window_width//2
        P2_window_low, P2_window_high = self.peak2_raw - self.window_width//2, self.peak2_raw + self.window_width//2
        P1, P2 = self.data.loc[P1_window_low:P1_window_high], self.data.loc[P2_window_low:P2_window_high]
        
        peak1_max, peak2_max = P1.max(),P2.max()
        peak1_max_id, peak2_max_id = P1.idxmax(), P2.idxmax()
        # indexes of found values are needed for marking them on a plot
        # for data preview concentrations are saved in the column names
        peaks = {
                'Peak 1' : peak1_max,
                'Peak 2' : peak2_max,
                'Peak 1 ID' : peak1_max_id,
                'Peak 2 ID' : peak2_max_id
                }
        object.__setattr__(self, 'peaks', peaks)
    
    @dispatch(list)
    def set_pen_color(self, color:list):
        if len(color) == 3:
            object.__setattr__(self, 'pen_color', color)
            
    @dispatch(str)
    def set_pen_color(self, color:str):
        object.__setattr__(self, 'pen_color', color)
    
    def set_pen_enabled(self, state:bool):
        object.__setattr__(self, 'pen_enabled', state)
        
    def set_symbol(self, symbol:str):
        #JSCH! -> validate symbol
        object.__setattr__(self, 'symbol', symbol)
    
    def set_symbol_brush_color(self, color:list):
        if len(color) == 3:
            object.__setattr__(self, 'symbol_brush_color', color)
    
    def set_symbol_size(self, size:int):
        object.__setattr__(self, 'symbol_size', size)
    
    def set_name(self, name:str):
        object.__setattr__(self, 'name', name)
        
    def set_enabled(self, state:bool):
        object.__setattr__(self, 'enabled', state)
    
    def set_displayed(self, state:bool):
        object.__setattr__(self, 'displayed', state)
    
    def set_window_width(self, width:int):
        object.__setattr__(self, 'window_width', width)
        self.load_peaks()
    
    def set_peak1(self, peak:int):
        object.__setattr__(self, "peak1_raw", peak)
        self.load_peaks()
        
    def set_peak2(self, peak:int):
        object.__setattr__(self, "peak2_raw", peak)
        self.load_peaks()

@dataclass(frozen=True)
class RMSE():
    regdata : pd.DataFrame
    model_id : int
    cac_data : dict
    
if __name__ == '__main__': # for testing purposes
    import matplotlib.pyplot as plt
    data = get_data("Data\pomiar1")
    peaks = get_peaks(data)
    regdata = prepare_regression_data(peaks) # this can be plotted
    model_data = get_models(regdata)
    R2val, RMSEval = choose_models_frame_id(model_data)
    model1,model2 = model_data.loc[RMSEval,['model1','model2']]
    example_plot(regdata, RMSEval, model1,model2)
    
class reSortProxyModel(QSortFilterProxyModel):
    
    def __init__(self, expr:str="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expr = expr
        
    def lessThan(self, left, right):
        left_data = self.sourceModel().data(left)
        right_data = self.sourceModel().data(right)
        try:
            left_value = float(re.findall('\d+(?:\.\d+)?', left_data.replace(',', '.'))[-1])
            right_value = float(re.findall('\d+(?:\.\d+)?', right_data.replace(',', '.'))[-1])
        except IndexError:
            return False
        return left_value < right_value