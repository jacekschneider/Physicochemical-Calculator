import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QCoreApplication
from PyQt6.uic.load_ui import loadUi

from PyQt6.QtCore import QTranslator


# TO DO LIST:

# Make points clickable
# Add another file formats to load
# Verify load data
# Make a load progress bar (Extra)
# Interpolate data ?


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.trl = QTranslator()
        QCoreApplication.installTranslator(self.trl)
        
        # Set options
        self.setWindowTitle("PBL Project")
        self.setWindowIcon(QIcon("icons/chemistry_1.png"))
        loadUi("mainwindow.ui", self)
        
        self.show()

        
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    sys.exit(app.exec())
    