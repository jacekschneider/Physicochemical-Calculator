import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QCoreApplication
from widgets import CentralWidget
from utils import tr

from PyQt6.QtCore import QTranslator


# TO DO LIST:

# Make points clickable
# Validate load data
# Make a load progress bar (Extra)
# Languages
# Interpolate data ?


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.trl = QTranslator()
        self.trl.load("translation.de.qm", "Languages")
        QCoreApplication.installTranslator(self.trl)
        
        # Set options
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowTitle("PBL Project")
        self.setWindowIcon(QIcon("icons/chemistry_1.png"))
        
        # Prepare Central Widget
        self.widget_central = CentralWidget()
        self.setCentralWidget(self.widget_central)
        
        # Prepare status bar
        self.status_bar = self.statusBar()
        # !JSCH -> Text
        message = tr("Ready")
        self.status_bar.showMessage(message, 5000)
        
        # Connections
        self.widget_central.signal_status.connect(self.display)
        
        self.show()
        
    def closeEvent(self, event):
        event.accept()
        # Stop threads on exit
        self.widget_central.widget_graph.worker_load_thread.quit()
        self.widget_central.widget_graph.worker_load_thread.wait()
        
    def display(self, message:str, timeout:int):
        self.status_bar.showMessage(message, timeout)
        
        
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    sys.exit(app.exec())
    