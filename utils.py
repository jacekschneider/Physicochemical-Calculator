import numpy as np
import pandas as pd
import pyqtgraph as pg
import re
from PyQt6.QtCore import QCoreApplication
from pathlib import Path
from sklearn.linear_model import LinearRegression ## pip install numpy scikit-learn statsmodels

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

dirpath = 'C:/Users/kwese/Desktop/Engineering thesis/Współpraca Artur Bal/przykładowy pomiar'
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
    concentrations: list[float] = [float(i) for i in data.columns]
    relatives = data.loc['Peak 1']/data.loc['Peak 2']
    regression_data = pd.DataFrame({'Y': relatives,
                                    'X': concentrations})
    return regression_data.T

def choose_model(data: pd.DataFrame):
    def RMSE(y,ypredict):
        mse = np.square(np.subtract(y,ypredict))
        rmse = np.sqrt(mse)
        return rmse
    X = data.loc['X'].to_numpy().reshape((-1, 1)) # the reshape is required
    Y = data.loc['Y'].to_numpy()
    for i in range(2,len(X)-2): # covers all possible models
        x1,x2 = X[:i],X[i:]
        y1,y2 = Y[:i],Y[i:]
        model1, model2 = LinearRegression().fit(x1,y1), LinearRegression().fit(x2,y2)
        prediction1, prediction2 = model1.predict(x1), model2.predict(x2)
        rmse1, rmse2 = RMSE(y1,prediction1), RMSE(y2,prediction2)
        rsq1, rsq2 = model1.score(), model2.score()
        ...
        # TODO finish this
        # model evaluation and returning the best fit one
        # maybe think about the crossing test

colors = "rgbwymc"
pens = []
for color in colors:
    pens.append(pg.mkPen(color))

if __name__ == '__main__': # for testing purposes
    data = get_data("Data\pomiar1")
    peaks = get_peaks(data)
    regdata = prepare_regression_data(peaks)
    choose_model(regdata)