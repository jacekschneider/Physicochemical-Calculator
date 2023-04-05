import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.uic.load_ui import loadUi
from workers import ReportWorker, SettingsWorker


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        loadUi("UI/ui_main.ui", self)

        # Workers
        self.report_worker = ReportWorker()
        self.settings_worker = SettingsWorker()
        
        #Connections
        self.widget_navigation.emit_dirpath.connect(self.settings_worker.load)
        self.widget_navigation.emit_dirpath.connect(self.widget_cac.load)
        self.settings_worker.emit_measurements.connect(self.widget_data.load)
        self.widget_navigation.pb_clear_data.clicked.connect(self.widget_data.clear)
        self.action_generate.triggered.connect(self.report_worker.generate)

        self.show()
        
            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    sys.exit(app.exec())
    