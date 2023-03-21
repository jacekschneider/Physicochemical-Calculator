import numpy as np
import pandas as pd
import pyqtgraph as pg
import re
from PyQt6.QtCore import QCoreApplication
from pathlib import Path

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

colors = "rgbwymc"
pens = []
for color in colors:
    pens.append(pg.mkPen(color))