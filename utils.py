import sys
import re
import os
import copy
import math
import pathlib
import colorsys
import pandas as pd
import numpy as np
import pyqtgraph as pg
from datetime import datetime

from dataclasses import dataclass, field
from multipledispatch import dispatch
from sklearn.linear_model import LinearRegression
from pathlib import Path
from math import log10
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from tempfile import NamedTemporaryFile
from pyqtgraph.exporters import ImageExporter

from PyQt6.QtWidgets import (QWidget, QFileDialog, QFileIconProvider, QLineEdit, QCheckBox,
                             QComboBox, QColorDialog, QPushButton, QListView, QMainWindow, QApplication, QTextEdit, QVBoxLayout)
from PyQt6.QtCore import QCoreApplication, QSortFilterProxyModel, QObject, pyqtSignal as Signal, pyqtSlot as Slot, QTranslator, QDir
from PyQt6.uic.load_ui import loadUi
from pyqtgraph.exporters import ImageExporter
from PyQt6.QtGui import  QFileSystemModel, QStandardItemModel, QStandardItem, QIntValidator, QValidator, QTextCursor


symbols = ["o", "t", "t1", "t2", "t3", "s", "p", "h", "star", "+", "d", "x"]

def closest_value(input_list, input_value):
    arr = np.asarray(input_list)
    i = (np.abs(arr - input_value)).argmin()
    return arr[i]

def tr(text_to_translate):
    return QCoreApplication.translate("@default", text_to_translate)

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
    
    
    
    
