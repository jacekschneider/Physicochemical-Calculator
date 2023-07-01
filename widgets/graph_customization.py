from utils import *
from containers.measurement import Measurement


class SettingsRow(QObject):
    emit_update = Signal(list)
    def __init__(self, measurement:Measurement, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Prepare widgets according to the measurement data
        self.measurement = copy.deepcopy(measurement)
        self.le_title = QLineEdit("titlex")
        self.le_title.setReadOnly(True)
        
        self.le_window_width = QLineEdit("3")
        self.window_width_validator = QIntValidator(1, 10)
        self.le_window_width.setValidator(self.window_width_validator)
        
        self.le_peak1 = QLineEdit("373")
        self.le_peak1_validator = QIntValidator(360, 380)
        self.le_peak1.setValidator(self.le_peak1_validator)      
        self.le_peak2 = QLineEdit("384")
        self.le_peak2_validator = QIntValidator(370, 390)
        self.le_peak2.setValidator(self.le_peak2_validator)
        
        self.button_pen = QPushButton()
        self.chb_pen_enable = QCheckBox()
        
        self.cob_symbol = QComboBox()
        self.cob_symbol.addItems(symbols)
        
        self.button_symbol_fill = QPushButton()
        
        self.le_symbol_size = QLineEdit("7")
        self.le_symbol_size_validator = QIntValidator(3, 12)
        self.le_symbol_size.setValidator(self.le_symbol_size_validator)
        self.chb_display = QCheckBox()
        self.chb_enable = QCheckBox()
        
        
        # Prepare connections
        self.le_title.editingFinished.connect(self.change_title)
        self.le_window_width.editingFinished.connect(self.change_window_width)
        self.le_window_width.textEdited.connect(self.validate_window_width)
        self.le_peak1.editingFinished.connect(self.change_peak1)
        self.le_peak2.editingFinished.connect(self.change_peak2)
        self.le_peak1.textEdited.connect(self.validate_peak1)
        self.le_peak2.textEdited.connect(self.validate_peak2)
        self.button_pen.clicked.connect(self.change_pen_colour)
        self.chb_pen_enable.toggled.connect(self.change_pen_enable)
        self.cob_symbol.activated.connect(self.change_symbol)
        self.button_symbol_fill.clicked.connect(self.change_symbol_colour)
        self.le_symbol_size.editingFinished.connect(self.change_symbol_size)
        self.le_symbol_size.textEdited.connect(self.validate_symbol_size)
        self.chb_display.toggled.connect(self.change_display)
        self.chb_enable.toggled.connect(self.change_enable)
        # Inject measurement data into widgets
        self.refresh()

    
    def change_title(self) ->None:
        self.measurement.set_name(self.le_title.text())
    
    def change_window_width(self)->None:
        self.measurement.set_window_width(int(self.le_window_width.text()))
        self.emit_update.emit(["width", self.le_window_width.text()])
    
    def change_window_width_ex(self, value:str):
        self.measurement.set_window_width(int(value))
        self.refresh()
        
    def change_peak1(self)->None:
        self.measurement.set_peak1(int(self.le_peak1.text()))
        self.emit_update.emit(["peak1", self.le_peak1.text()])

    def change_peak1_ex(self, value:str)->None:
        self.measurement.set_peak1(int(value))
        self.refresh()

    def change_peak2(self)->None:
        self.measurement.set_peak2(int(self.le_peak2.text()))
        self.emit_update.emit(["peak2", self.le_peak2.text()])

    def change_peak2_ex(self, value:str)->None:
        self.measurement.set_peak2(int(value))
        self.refresh()   
    
    def change_pen_enable(self)->None:
        self.measurement.set_pen_enabled(self.chb_pen_enable.isChecked())
        self.emit_update.emit(["pen_enable", self.chb_pen_enable.isChecked()])
        
    def change_pen_enable_ex(self, value:bool)->None:
        self.measurement.set_pen_enabled(value)
        self.refresh()
    
    def change_symbol(self)->None:
        self.measurement.set_symbol(self.cob_symbol.currentText())
        self.emit_update.emit(["symbol", self.cob_symbol.currentText()])
        
    def change_symbol_ex(self, symbol:str):
        self.measurement.set_symbol(symbol)
        self.refresh()

    def change_pen_colour(self):
        colour = QColorDialog.getColor()
        rgb = [colour.red(), colour.green(), colour.blue()]
        self.measurement.set_pen_color(rgb)
        self.button_pen.setStyleSheet("background-color:rgb({},{},{})".format(rgb[0],rgb[1],rgb[2]))
        self.emit_update.emit(["pen_colour", rgb])
    
    @dispatch(list)
    def change_pen_colour_ex(self, rgb:list):
        self.measurement.set_pen_color(rgb)
        self.refresh()
    
    def change_symbol_colour(self):
        colour = QColorDialog.getColor()
        rgb = [colour.red(), colour.green(), colour.blue()]
        self.measurement.set_symbol_brush_color(rgb)
        self.button_symbol_fill.setStyleSheet("background-color:rgb({},{},{})".format(rgb[0],rgb[1],rgb[2]))
        self.emit_update.emit(["symbol_colour", rgb])
        
    @dispatch(list)
    def change_symbol_colour_ex(self, rgb:list):
        self.measurement.set_symbol_brush_color(rgb)
        self.refresh()

    def change_symbol_size(self):
        self.measurement.set_symbol_size(int(self.le_symbol_size.text()))
        self.emit_update.emit(["symbol_size", self.le_symbol_size.text()])
        
    def change_symbol_size_ex(self, value:str):
        self.measurement.set_symbol_size(int(value))
        self.refresh()
        
    def change_display(self):
        self.measurement.set_displayed(self.chb_display.isChecked())
        self.emit_update.emit(["display", self.chb_display.isChecked()])
        
    def change_display_ex(self, value:bool):
        self.measurement.set_displayed(value)
        self.refresh()
    
    def change_enable(self):
        self.measurement.set_enabled(self.chb_enable.isChecked())
        self.emit_update.emit(["enable", self.chb_enable.isChecked()])
    
    def change_enable_ex(self, value:bool):
        self.measurement.set_enabled(value)
        self.refresh()
        
    def validate_window_width(self)->None:
        state, _, __ = self.window_width_validator.validate(self.le_window_width.text(), 0)
        if state == QValidator.State.Intermediate:
            self.le_window_width.setStyleSheet("background-color:rgb({},{},{})".format(255,0,0))
        else:
            self.le_window_width.setStyleSheet("")
            
    def validate_peak1(self)->None:
        state, _, __ = self.le_peak1_validator.validate(self.le_peak1.text(), 0)
        if state == QValidator.State.Intermediate:
            self.le_peak1.setStyleSheet("background-color:rgb({},{},{})".format(255,0,0))
        else:
            self.le_peak1.setStyleSheet("")

    def validate_peak2(self)->None:
        state, _, __ = self.le_peak2_validator.validate(self.le_peak2.text(), 0)
        if state == QValidator.State.Intermediate:
            self.le_peak2.setStyleSheet("background-color:rgb({},{},{})".format(255,0,0))
        else:
            self.le_peak2.setStyleSheet("")
        
    def validate_symbol_size(self)->None:
        state, _, __ = self.le_symbol_size_validator.validate(self.le_symbol_size.text(), 0)
        if state == QValidator.State.Intermediate:
            self.le_symbol_size.setStyleSheet("background-color:rgb({},{},{})".format(255,0,0))
        else:
            self.le_symbol_size.setStyleSheet("")
        
    def get_widgets(self) -> list:
        list_widget = []
        list_widget.append(self.le_title)
        list_widget.append(self.chb_enable)
        list_widget.append(self.chb_display)
        list_widget.append(self.le_window_width)
        list_widget.append(self.le_peak1)
        list_widget.append(self.le_peak2)
        list_widget.append(self.button_pen)
        list_widget.append(self.chb_pen_enable)
        list_widget.append(self.cob_symbol)
        list_widget.append(self.button_symbol_fill)
        list_widget.append(self.le_symbol_size)

        return list_widget
    
    def get_measurement(self) -> Measurement:
        return self.measurement
    
    def get_pen_color(self) -> list:
        return self.measurement.pen_color
    
    def get_symbol_color(self) -> list:
        return self.measurement.symbol_brush_color
    
    def set_measurement(self, measurement:Measurement):
        self.measurement = copy.deepcopy(measurement)
        self.refresh()
    
    def refresh(self):
        self.le_title.setText(self.measurement.name.split(' ')[-1])
        self.le_window_width.setText(str(self.measurement.window_width))
        self.le_peak1.setText(str(self.measurement.peak1_raw))
        self.le_peak2.setText(str(self.measurement.peak2_raw))
        pen_color = self.measurement.pen_color
        self.button_pen.setStyleSheet("background-color:rgb({},{},{})".format(pen_color[0],pen_color[1],pen_color[2]))
        self.chb_pen_enable.setChecked(self.measurement.pen_enabled)
        for (index, symbol) in enumerate(symbols):
            if symbol == self.measurement.symbol:    
                self.cob_symbol.setCurrentIndex(index)
        symbol_color = self.measurement.symbol_brush_color
        self.button_symbol_fill.setStyleSheet("background-color:rgb({},{},{})".format(symbol_color[0],symbol_color[1],symbol_color[2]))
        self.le_symbol_size.setText(str(self.measurement.symbol_size))
        self.chb_display.setChecked(self.measurement.displayed)
        self.chb_enable.setChecked(self.measurement.enabled)

class WidgetGraphCustomization(QWidget):
    emit_measurements = Signal(list)
    
    def __init__(self, measurements_default:list, measurements:list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        loadUi("ui/ui_settings_graph_data.ui", self)
        
        self.measurements_default:list[Measurement] = measurements_default
        self.measurements_raw:list[Measurement] = measurements
        self.settings_rows:list[SettingsRow] = []
        self.model = QStandardItemModel()
        self.labels = ["concentration","enable", "display", "window width (1-10)", "peak1 (360-380)", "peak2 (370-390)", 
                       "pen color", "pen enable", "symbol", "symbol color", "symbol size (3-12)" ]
        self.model.setHorizontalHeaderLabels(self.labels)
        self.tree.setModel(self.model)
        for (index, measurement) in enumerate(self.measurements_raw):
            self.create_row(index_row = index, measurement=measurement)  
            self.tree.resizeColumnToContents(index)
            
        self.pb_apply.clicked.connect(self.apply)
        self.pb_cancel.clicked.connect(self.cancel)
        self.pb_reset.clicked.connect(self.reset)
        self.pb_restore_default.clicked.connect(self.restore_default)
        self.cb_stylesheet.activated.connect(self.change_stylesheet)
        for row in self.settings_rows:
            row.emit_update.connect(self.update_column)
        
    def create_row(self, index_row, measurement:Measurement):
        self.model.appendRow([QStandardItem() for i in self.labels])
        
        self.measurement = measurement
        # Passing self as an argument was a crucial condition for all the connections
        self.row = SettingsRow(self.measurement, self)
        self.settings_rows.append(self.row)
        self.row_list = self.row.get_widgets()
        
        for (index_widget, widget) in enumerate(self.row_list):
            self.tree.setIndexWidget(self.model.index(index_row, index_widget), widget)
            
    def apply(self):
        measurements_list=[]
        for row in self.settings_rows:
            measurements_list.append(row.get_measurement())
        self.emit_measurements.emit(measurements_list)
        print("Graph Customization applied")
        self.close()
    
    def update_column(self, uinfo:list):
        option = uinfo[0]
        value = uinfo[1]
        if self.chb_applycolumn.isChecked():
            for row in self.settings_rows:
                if option == "symbol":
                    row.change_symbol_ex(value)
                elif option == "width":
                    row.change_window_width_ex(value)
                elif option == "peak1":
                    row.change_peak1_ex(value)
                elif option == "peak2":
                    row.change_peak2_ex(value)
                elif option == "pen_enable":
                    row.change_pen_enable_ex(value)
                elif option == "pen_colour":
                    row.change_pen_colour_ex(value)
                elif option == "symbol_colour":
                    row.change_symbol_colour_ex(value)
                elif option == "symbol_size":
                    row.change_symbol_size_ex(value)
                elif option == "display":
                    row.change_display_ex(value)
                elif option == "enable":
                    # enable not available for column
                    # row.change_enable_ex(value)
                    pass
            
    def cancel(self):
        self.close()
        
    def reset(self):
        for (index, measurement) in enumerate(self.measurements_raw):
            self.settings_rows[index].set_measurement(measurement)

    def restore_default(self):
        for (index, measurement) in enumerate(self.measurements_default):
            self.settings_rows[index].set_measurement(measurement)
            
    def change_stylesheet(self):
        stylesheet_idx = self.cb_stylesheet.currentIndex()
        fill_symbol = self.chb_fillsymbol.isChecked()
        for (index,  row) in enumerate(self.settings_rows):
            if stylesheet_idx == 0:
                color = color_gen()
            if stylesheet_idx == 1:
                color = gray_color_gen(index, len(self.settings_rows))
            try:
                row.change_pen_colour_ex(color)
                row.change_symbol_colour_ex(color) if fill_symbol else None
            except:
                return