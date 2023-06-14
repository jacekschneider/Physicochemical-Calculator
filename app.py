import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.uic.load_ui import loadUi
from workers import ReportWorker, SettingsWorker, CalculatorWorker, ExportWorker, GraphOptionsWorker
from widgets import WidgetGraphCustomization, WidgetGraphOptions

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        loadUi("UI/ui_main.ui", self)

        # Workers
        self.report_worker = ReportWorker()
        self.settings_worker = SettingsWorker()
        self.calculator_worker = CalculatorWorker()
        self.export_worker = ExportWorker()
        self.go_worker = GraphOptionsWorker()

        
        #Connections
        self.widget_navigation.emit_dirpath.connect(self.settings_worker.load)
        self.settings_worker.emit_measurements.connect(self.widget_data.load)
        self.settings_worker.emit_measurements.connect(self.calculator_worker.load)
        self.settings_worker.emit_measurements.connect(self.report_worker.set_measurements)
        self.calculator_worker.emit_RMSE.connect(self.widget_cac.load)
        self.widget_cac.emit_plot.connect(self.report_worker.set_CAC_plot)
        # self.widget_data.emit_plot.connect(self.report_worker.set_dataview_plot)
        self.widget_navigation.pb_clear_data.clicked.connect(self.widget_data.clear)
        self.action_generate.triggered.connect(self.report_worker.generate)
        self.action_graph_customization.triggered.connect(self.show_customization)
        self.action_graph_options.triggered.connect(self.show_graphoptions)
        self.calculator_worker.emit_I1I3.connect(self.export_worker.get_I1I3)
        self.widget_cac.pb_export.clicked.connect(self.export_worker.export_I1I3)
        self.go_worker.emit_go.connect(self.widget_data.update)
        self.go_worker.emit_go.connect(self.widget_cac.update)
        
        self.show()
        
    def show_customization(self):
        self.widget_customization = WidgetGraphCustomization(self.settings_worker.get_measurements_raw(), self.settings_worker.get_measurements())
        self.widget_customization.emit_measurements.connect(self.settings_worker.load)
        self.widget_customization.show()
        
    def show_graphoptions(self):
        self.widget_go = WidgetGraphOptions(go_cac=self.go_worker.CAC(), go_data=self.go_worker.DATA())
        self.widget_go.emit_go.connect(self.go_worker.load)
        self.widget_go.show()
            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    sys.exit(app.exec())
    