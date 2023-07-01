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
        self.close()