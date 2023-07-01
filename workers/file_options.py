from utils import *
from containers.file_options import FileOptions

class FileOptionsWorker(QObject):
    emit_fo = Signal(FileOptions)
    emit_avg = Signal(bool)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fo = FileOptions(separator=r'\t')
    
    def load(self, fo:FileOptions):
        self.fo = fo
        self.emit_fo.emit(self.fo)
        self.emit_avg.emit(self.fo.average)
        
    def Fo(self):
        return self.fo