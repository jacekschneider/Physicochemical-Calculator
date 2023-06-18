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