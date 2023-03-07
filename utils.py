import numpy as np
import pandas as pd
from PyQt6.QtCore import QCoreApplication

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
    

data = pd.read_excel("Data/polimer_data.xlsx")
verify(data)


