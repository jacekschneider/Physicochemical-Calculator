from utils import *
from workers.calculator import CalculatorWorker
from workers.data_loader import DataLoaderWorker
from workers.exporter import ExportWorker
from workers.graph_options import GraphOptionsWorker
from workers.report_generator import ReportGeneratorWorker
from workers.file_options import FileOptionsWorker
from widgets.graph_customization import WidgetGraphCustomization
from widgets.graph_options import WidgetGraphOptions
from widgets.file_options import WidgetFileOptions


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        loadUi("ui/ui_main.ui", self)
        
        self.trl = QTranslator()
        QCoreApplication.installTranslator(self.trl)

        # Workers
        self.report_worker = ReportGeneratorWorker()
        self.settings_worker = DataLoaderWorker()
        self.calculator_worker = CalculatorWorker()
        self.export_worker = ExportWorker()
        self.go_worker = GraphOptionsWorker()
        self.fo_worker = FileOptionsWorker()

        self.reinit()
        self.show()
        
    def reinit(self):
        #Connections
        self.action_de.triggered.connect(self.set_de)
        self.action_pl.triggered.connect(self.set_pl)
        self.action_en.triggered.connect(self.set_en)
        self.widget_navigation.emit_dirpath.connect(self.settings_worker.load)
        self.settings_worker.emit_measurements.connect(self.widget_data.load)
        self.settings_worker.emit_measurements.connect(self.calculator_worker.load)
        self.settings_worker.emit_measurements.connect(self.report_worker.set_measurements)
        self.calculator_worker.emit_RMSE.connect(self.widget_cac.load)
        self.calculator_worker.emit_RMSE.connect(self.report_worker.set_RMSE)
        self.calculator_worker.emit_models.connect(self.report_worker.set_model_data)
        self.calculator_worker.emit_model_fit.connect(self.report_worker.set_model_fit)
        self.widget_cac.emit_plot.connect(self.report_worker.set_CAC_plot)
        self.widget_data.emit_plot.connect(self.report_worker.set_dataview_plot)
        self.widget_navigation.pb_clear_data.clicked.connect(self.widget_data.clear)
        self.action_generate.triggered.connect(self.report_worker.generate)
        self.action_graph_customization.triggered.connect(self.show_customization)
        self.action_graph_options.triggered.connect(self.show_graphoptions)
        self.action_file_options.triggered.connect(self.show_fileoptions)
        self.calculator_worker.emit_I1I3.connect(self.export_worker.get_I1I3)
        self.widget_cac.pb_export.clicked.connect(self.export_worker.export_I1I3)
        self.go_worker.emit_go.connect(self.widget_data.update)
        self.go_worker.emit_go.connect(self.widget_cac.update)
        self.fo_worker.emit_fo.connect(self.settings_worker.load)
        self.fo_worker.emit_avg.connect(self.calculator_worker.set_average)
        
    def show_customization(self):
        self.widget_customization = WidgetGraphCustomization(self.settings_worker.get_measurements_raw(), self.settings_worker.get_measurements())
        self.widget_customization.emit_measurements.connect(self.settings_worker.load)
        self.widget_customization.show()
        
    def show_graphoptions(self):
        self.widget_go = WidgetGraphOptions(go_cac=self.go_worker.CAC(), go_data=self.go_worker.DATA())
        self.widget_go.emit_go.connect(self.go_worker.load)
        self.widget_go.show()
        
    def show_fileoptions(self):
        self.widget_fo = WidgetFileOptions(fo=self.fo_worker.Fo())
        self.widget_fo.emit_fo.connect(self.fo_worker.load)
        self.widget_fo.show()
        
    def set_de(self):
        self.trl.load("de.qm", "UI")
        self.retranslate()
        
    def set_pl(self):
        self.trl.load("pl.qm", "UI")
        self.retranslate()
        
    def set_en(self):
        self.trl.load("", "UI")
        self.retranslate()
    
    def retranslate(self):
        loadUi("UI/ui_main.ui", self)
        self.reinit()