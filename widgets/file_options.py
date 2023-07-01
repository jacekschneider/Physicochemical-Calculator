''' Physicochemical Calculator - calculate automatically CMC value with emission spectrum data
    Copyright (C) 2023  Jacek Schneider, Konrad Wesenfeld

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.'''
    
from utils import *
from containers.file_options import FileOptions


class WidgetFileOptions(QWidget):
    emit_average = Signal(bool)
    emit_fo = Signal(FileOptions)
    def __init__(self, fo:FileOptions, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        loadUi("ui/ui_fileoptions.ui", self)
        
        self.fo = fo
        self.pb_apply.clicked.connect(self.apply)
        self.pb_cancel.clicked.connect(self.cancel)
        self.load()
        
    def load(self):
        self.cb_separator.setCurrentIndex(self.cb_separator.findText(self.fo.separator))
        self.cb_encoding.setCurrentIndex(self.cb_encoding.findText(self.fo.encoding))
        self.sb_beginwithindex.setValue(self.fo.index_column_start)
        self.sb_indexstep.setValue(self.fo.index_column_step)
        self.cb_average.setChecked(self.fo.average)
        
    def cancel(self):
        self.close()
        
    def apply(self):
        self.fo.separator = self.cb_separator.currentText()
        self.fo.encoding = self.cb_encoding.currentText()
        self.fo.index_column_start = self.sb_beginwithindex.value()
        self.fo.index_column_step = self.sb_indexstep.value()
        self.fo.average = self.cb_average.isChecked()
        self.emit_fo.emit(self.fo)
        print("File options applied")
        self.close()