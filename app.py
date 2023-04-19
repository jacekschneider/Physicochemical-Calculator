import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.uic.load_ui import loadUi
from workers import ReportWorker, SettingsWorker, CalculatorWorker
from widgets import WidgetGraphCustomization

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        loadUi("UI/ui_main.ui", self)

        # Workers
        self.report_worker = ReportWorker()
        self.settings_worker = SettingsWorker()
        self.calculator_worker = CalculatorWorker()

        
        #Connections
        self.widget_navigation.emit_dirpath.connect(self.settings_worker.load)
        self.settings_worker.emit_measurements.connect(self.widget_data.load)
        self.settings_worker.emit_measurements.connect(self.calculator_worker.load)
        self.settings_worker.emit_measurements.connect(self.report_worker.set_measurements)
        self.calculator_worker.emit_RMSE.connect(self.widget_cac.load)
        self.widget_navigation.pb_clear_data.clicked.connect(self.widget_data.clear)
        self.action_generate.triggered.connect(self.report_worker.generate)
        self.action_graph_customization.triggered.connect(self.show_customization)

        self.show()
        
    def show_customization(self):
        self.widget_customization = WidgetGraphCustomization(self.settings_worker.get_measurements())
        self.widget_customization.show()
            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    sys.exit(app.exec())
    