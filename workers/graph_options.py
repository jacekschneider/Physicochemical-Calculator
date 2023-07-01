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
from containers.graph_options import GraphOptions

class GraphOptionsWorker(QObject):
    emit_go = Signal(GraphOptions)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.go_data = GraphOptions(id="DATA", label_left='Intensity', label_bottom='Wavelength, nm', title="Emission Spectrum")
        self.go_cac = GraphOptions(id="CAC", label_left='I1/I3', label_bottom='logC, mg/ml')
    
    def load(self, go:GraphOptions):
        if go.id=="CAC":
            self.go_cac = go
        elif go.id=="DATA":
            self.go_data = go
        self.emit_go.emit(go)
        
    def CAC(self) -> GraphOptions:
        return self.go_cac
    
    def DATA(self) -> GraphOptions:
        return self.go_data