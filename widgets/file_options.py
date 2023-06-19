from utils import *
from containers.file_options import FileOptions


class WidgetFileOptions(QWidget):
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        loadUi("ui/ui_fileoptions.ui", self)