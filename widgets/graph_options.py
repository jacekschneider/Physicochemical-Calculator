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


class WidgetGraphOptions(QWidget):
    emit_go = Signal(GraphOptions)
    def __init__(self, go_cac, go_data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        loadUi("ui/ui_settings_graph_options.ui", self)

        self.go_cac = go_cac
        self.go_data = go_data
        self.go:GraphOptions
        self.load()
        
        self.cb_graph.currentIndexChanged.connect(self.load)
        self.pb_color.clicked.connect(self.change_colour)
        self.pb_cancel.clicked.connect(self.cancel)
        self.pb_apply.clicked.connect(self.apply)

    def load(self):
        option=self.cb_graph.currentIndex()
        if option == 1:
            self.go = self.go_cac
        elif option == 0:
            self.go = self.go_data
        else: return
        self.le_labelleft.setText(self.go.label_left)
        self.le_labelbottom.setText(self.go.label_bottom)
        self.sb_fontsize.setValue(self.go.fontsize)
        self.le_title.setText(self.go.title)
        self.sb_titlefontsize.setValue(self.go.title_size)
        self.sb_legendtextsize.setValue(self.go.legend_textsize)
        self.cb_legendon.setChecked(self.go.legend_on)
        self.pb_color.setStyleSheet("background-color:rgb({},{},{})".format(self.go.fontcolor[0],self.go.fontcolor[1],self.go.fontcolor[2]))
        
    def change_colour(self):
        colour = QColorDialog.getColor()
        rgb = [colour.red(), colour.green(), colour.blue()]
        self.go.fontcolor=rgb
        self.pb_color.setStyleSheet("background-color:rgb({},{},{})".format(self.go.fontcolor[0],self.go.fontcolor[1],self.go.fontcolor[2]))
        
    def cancel(self):
        self.close()
        
    def apply(self):
        self.go.label_left = self.le_labelleft.text()
        self.go.label_bottom = self.le_labelbottom.text()
        self.go.fontsize = self.sb_fontsize.value()
        self.go.legend_on = self.cb_legendon.isChecked()
        self.go.legend_textsize = self.sb_legendtextsize.value()
        self.go.title = self.le_title.text()
        self.go.title_size = self.sb_titlefontsize.value()
        self.emit_go.emit(self.go)
        print("Graph Options applied")
        self.close()