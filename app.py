import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QIcon
from PyQt6.uic.load_ui import loadUi
import pyqtgraph as pg


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        loadUi("UI/ui_main.ui", self)
        self.show()
        
        self.widget_navigation.emit_path_folder.connect(self.widget_data.load)
        self.widget_navigation.pb_clear_data.clicked.connect(self.widget_data.clear)
        
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    sys.exit(app.exec())
    