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