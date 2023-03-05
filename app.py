import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QCoreApplication
from widgets import CentralWidget
from utils import tr

from PyQt6.QtCore import QTranslator


# TO DO LIST:

# Make points clickable
# Verify load data
# Make a load progress bar (Extra)
# Simplify language translation
# Validate derrivative value
# Interpolate data ?


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.trl = QTranslator()
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
        message = tr("Ready")
        self.status_bar.showMessage(message, 5000)
        
        # Prepare menu bar
        menu_bar = self.menuBar()
        menu_language = menu_bar.addMenu('&Language')
        
        action_en = QAction(QIcon("icons/us.png"), '&'+tr("English"), self)
        action_de = QAction(QIcon("icons/de.png"), '&'+tr("German"), self)
        action_pl = QAction(QIcon("icons/pl.png"), '&'+tr("Polish"), self)
        action_en.triggered.connect(self.set_en)
        action_de.triggered.connect(self.set_de)
        action_pl.triggered.connect(self.set_pl)
        menu_language.addAction(action_en)
        menu_language.addAction(action_de)
        menu_language.addAction(action_pl)

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
    
    def set_en(self):
        self.trl.load("")
        QCoreApplication.installTranslator(self.trl)
        self.widget_central.retranslate()
    
    def set_de(self):
        self.trl.load("translation.de.qm", "Languages")
        self.widget_central.widget_load_data.widget_button_fbrowse.setText(tr("Load data"))
        self.widget_central.retranslate()
        
    def set_pl(self):
        self.trl.load("translation.pl.qm", "Languages")
        self.widget_central.widget_load_data.widget_button_fbrowse.setText(tr("Load data"))
        self.widget_central.retranslate()
        
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    sys.exit(app.exec())
    