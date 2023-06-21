from utils import *
from containers.file_options import FileOptions


class WidgetFileOptions(QWidget):
    emit_average = Signal(bool)
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        loadUi("ui/ui_fileoptions.ui", self)
        
        self.pb_apply.clicked.connect(self.apply)
        
    def apply(self):
        self.emit_average.emit(self.cb_average.isChecked())
        self.close()