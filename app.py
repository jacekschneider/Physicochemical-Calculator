import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QIcon
from widgets import CentralWidget


# TO DO LIST:

# Make points clickable
# Validate load data
# Make status bar
# Make a load progress bar (Extra)
# Languages
# Interpolate data ?


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set options
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowTitle("PBL Project")
        self.setWindowIcon(QIcon("icons/chemistry_1.png"))
        # qdarktheme.setup_theme()
        
        # Prepare Central Widget
        self.widget_central = CentralWidget()
        self.setCentralWidget(self.widget_central)

        self.show()
        
    def closeEvent(self, event):
        event.accept()
        self.widget_central.widget_graph.worker_load_thread.quit()
        self.widget_central.widget_graph.worker_load_thread.wait()
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    sys.exit(app.exec())
    