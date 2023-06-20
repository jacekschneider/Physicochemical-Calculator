from utils import *
from containers.measurement import Measurement
from containers.graph_options import GraphOptions

class WidgetData(QWidget):
    emit_plot = Signal(ImageExporter)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        loadUi("ui/ui_data.ui", self)
        
        self.measurements:list[Measurement] = []
        #Graph Items
        self.items_plot = []
        
        self.graph.showGrid(x=True, y=True)
        self.update(GraphOptions(id="DATA", label_left='Intensity', label_bottom='Wavelength, nm', title="Emission Spectrum"))
        self.cb_measurements.activated.connect(self.display)

    def load(self, measurements:list):
        self.measurements:list[Measurement] = measurements
        self.cb_measurements.clear()
        self.cb_measurements.addItem('*')
        self.cb_measurements.addItems([measurement.name.split('= ')[-1] for measurement in self.measurements])
        self.draw()
        imx = ImageExporter(self.graph.scene())
        self.emit_plot.emit(imx)  
        
    @dispatch(Measurement, bool)                  
    def draw(self, measurement:Measurement, enable_peaks:bool=False):
        pen = pg.mkPen(measurement.pen_color) if measurement.pen_enabled else None
        item_plot = self.graph.plot(
            x=measurement.data.index.values,
            y=measurement.data['Y'].to_numpy(),
            pen=pen,
            symbol=measurement.symbol,
            symbolPen=pg.mkPen(measurement.pen_color),
            symbolBrush=pg.mkBrush(measurement.symbol_brush_color),
            symbolSize=measurement.symbol_size,
            name=measurement.name
        )
        self.items_plot.append(item_plot)
        
        if enable_peaks:
            self.draw(measurement.peaks, measurement.symbol_size)
            for i in range(self.cb_measurements.count()):
                if self.cb_measurements.itemText(i) in measurement.name:
                    self.cb_measurements.setCurrentIndex(i)
        else:
            self.cb_measurements.setCurrentIndex(0)
        
    @dispatch(dict, int)
    def draw(self, peaks:dict, size:int):
        peak1_x = peaks["Peak 1 ID"]
        peak2_x = peaks["Peak 2 ID"]
        peak1_y = round(peaks["Peak 1"], 3)
        peak2_y = round(peaks["Peak 2"], 3)
        self.le_I1.setText(str(float(peak1_y)))
        self.le_I3.setText(str(float(peak2_y)))
        self.items_plot.append(self.graph.plot(peak1_x, peak1_y, pen=None, symbol='star',
                                               symbolPen=pg.mkPen("w"),symbolBrush=pg.mkBrush("w"),  symbolSize=size+2, name="I1 = {}".format(int(peak1_y))))
        self.items_plot.append(self.graph.plot(peak2_x, peak2_y, pen=None, symbol='star',
                                               symbolPen=pg.mkPen("w"),symbolBrush=pg.mkBrush("w"),  symbolSize=size+2, name="I3 = {}".format(int(peak2_y))))
    
    @dispatch()
    def draw(self):
        self.clear()
        self.le_I1.setText("*")
        self.le_I3.setText("*")
        counter_displayed = 0
        for measurement in self.measurements:
            counter_displayed = counter_displayed + 1 if measurement.displayed else counter_displayed
        for (index, measurement) in enumerate(self.measurements):
            if measurement.displayed:
                self.draw(measurement, counter_displayed==1)
        
    def clear(self):
        for item in self.items_plot:
            self.graph.removeItem(item)
        while len(self.items_plot):
            self.items_plot.pop()
    
    def dragEnterEvent(self, e):
        e.accept()
    
    #!JSCH -> Accept txt only, otherwise do sth
    def dropEvent(self, e):
        view:QListView = e.source()
        self.clear()
        for (index, measurement) in enumerate(self.measurements):
            self.measurements[index].set_displayed(False)
        for item in view.selectedIndexes():
            source_index = view.model().mapToSource(item)
            index_item = view.model().sourceModel().index(source_index.row(), 0, source_index.parent())
            path = view.model().sourceModel().fileName(index_item)
            path_ending = path.split('.')[-1]
            filename = path.split('/')[-1]
            if path_ending == 'txt':
                for (index, measurement) in enumerate(self.measurements):
                    if filename == measurement.filename:
                        self.measurements[index].set_displayed(True)
                    
        self.draw()
        e.accept()
        
    def display(self):
        concentration = self.cb_measurements.currentText()
        for measurement in self.measurements:
            measurement.set_displayed(concentration in measurement.name.replace(',','.') or concentration == '*') 
        self.draw()
        
    def update(self, go:GraphOptions):

        if not go.id == "DATA": return
        self.legend = self.graph.addLegend(labelTextColor=go.fontcolor, labelTextSize="{}pt".format(go.legend_textsize))
        self.legend.anchor((0,0),(0.7,0.1))
        self.legend.setVisible(go.legend_on)
        self.styles = {'color':'rgb({},{},{})'.format(go.fontcolor[0],go.fontcolor[1],go.fontcolor[2]), 'font-size':'{}px'.format(go.fontsize)}
        self.graph.setLabel('bottom', go.label_bottom, **self.styles)
        self.graph.setLabel('left', go.label_left, **self.styles)
        if not go.title == "" :
            try:
                self.graph.setTitle(go.title, color=go.fontcolor, size="{}pt".format(go.title_size))
            except : self.graph.setTitle(None)
        else:
            self.graph.setTitle(None)