import numpy as np
from PyQt6.QtCore import QCoreApplication

def closest_value(input_list, input_value):
    arr = np.asarray(input_list)
    i = (np.abs(arr - input_value)).argmin()
    return arr[i]

def tr( text_to_translate):
    return QCoreApplication.translate("@default", text_to_translate)


