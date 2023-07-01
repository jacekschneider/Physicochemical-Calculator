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
from containers.rmse import RMSE
from containers.graph_options import GraphOptions

class WidgetCAC(QWidget):
    emit_plot = Signal(ImageExporter)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        loadUi("ui/ui_cac.ui", self)
        
        self.items_plot = []
        self.items_text = []
        self.rmse_data = None
        self.hide_text = True 
        self.graph.showGrid(x=True, y=True)
        self.update(GraphOptions(id="CAC", label_left='I1/I3', label_bottom='logC, mg/ml'))
        
        self.cb_logscale.stateChanged.connect(self.logscale_handler)
    
    def load(self, rmse_data:RMSE):
        self.clear()
        self.rmse_data = rmse_data
        self.draw()
        
    def draw(self):
        
        X = self.rmse_data.regdata.loc['X'].to_numpy()
        Y = self.rmse_data.regdata.loc['Y'].to_numpy()
        cac_x = self.rmse_data.cac_data["cac_x"]
        cac_y = self.rmse_data.cac_data["cac_y"]
        
        model_id = self.rmse_data.model_id
        x1,x2 = X[:model_id], X[model_id:]
        y1,y2 = Y[:model_id], Y[model_id:]
        
        if self.cb_logscale.isChecked():
            self.items_plot.append(self.graph.plot(x1, y1, pen=None, symbol='o', symbolPen=pg.mkPen("b"),symbolBrush=pg.mkBrush("b"),  symbolSize=7))
            self.items_plot.append(self.graph.plot(x2, y2, pen=None, symbol='o', symbolPen=pg.mkPen("r"),symbolBrush=pg.mkBrush("r"),  symbolSize=7))
            #JSCH! -> abline range upgrade
            self.abline(self.rmse_data.cac_data["a1"], self.rmse_data.cac_data["b1"], start=-3.1, stop=cac_x+0.1, step=0.01)
            self.abline(self.rmse_data.cac_data["a2"], self.rmse_data.cac_data["b2"], start=cac_x-0.1, stop=1.2, step=0.01)

            pos_x = round(cac_x[0], 3)
            pos_y = round(cac_y[0], 3)
            self.items_plot.append(self.graph.plot(cac_x, cac_y, pen=None, symbol='d',
                                                symbolPen=pg.mkPen("g"),symbolBrush=pg.mkBrush("g"),  symbolSize=9, name="CMC = [{}, {}]".format(pos_x, pos_y)))

            item_text = pg.TextItem(text=f"CMC = {np.round(10**pos_x, 6)} mg/ml", color=(0, 0, 0), border=pg.mkPen((0, 0, 0)), fill=pg.mkBrush("g"), anchor=(0, 0))
            item_text.setPos(cac_x[0], cac_y[0])
            self.items_text.append(item_text)
        else:
            self.items_plot.append(self.graph.plot(10**x1, y1, pen=None, symbol='o', symbolPen=pg.mkPen("b"),symbolBrush=pg.mkBrush("b"),  symbolSize=7))
            self.items_plot.append(self.graph.plot(10**x2, y2, pen=None, symbol='o', symbolPen=pg.mkPen("r"),symbolBrush=pg.mkBrush("r"),  symbolSize=7))
            pos_x = round(cac_x[0], 3)
            pos_y = round(cac_y[0], 3)
            self.items_plot.append(self.graph.plot(10**cac_x, cac_y, pen=None, symbol='d',
                                                symbolPen=pg.mkPen("g"),symbolBrush=pg.mkBrush("g"),  symbolSize=9, name="CMC = [{}, {}]".format(pos_x, pos_y)))

        self.le_CMC.setText(f"{np.round(10**pos_x, 6)}")
        
        imx = ImageExporter(self.graph.scene())
        self.emit_plot.emit(imx)
        
        
    def abline(self, a, b, start, stop, step):
        # axes = self.graph.getAxis('bottom')
        # x_vals = np.array(axes.range)
        x_vals = np.arange(start=start, stop=stop, step=step)
        y_vals = b + a * x_vals
        self.items_plot.append(self.graph.plot(x_vals, y_vals, pen=pg.mkPen("w")))
    
    def clear(self):
        for item in self.items_plot:
            self.graph.removeItem(item)
        for item in self.items_text:
            self.graph.removeItem(item)
        while len(self.items_plot):
            self.items_plot.pop()
        while len(self.items_text):
            self.items_text.pop()
            
    def mouseDoubleClickEvent(self, event) -> None:
        if len(self.items_text) > 0 and self.rmse_data is not None and self.hide_text:
            for text in self.items_text:
                self.graph.addItem(text)
            self.hide_text = False
        else:
            for text in self.items_text:
                self.graph.removeItem(text)
            self.hide_text = True
            
    def update(self, go:GraphOptions):
        if not go.id == "CAC": return
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
        
    def logscale_handler(self):
        self.clear()
        self.draw()