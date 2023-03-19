import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QIcon



class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set options
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowTitle("Physicochemical Calculator")
        self.setWindowIcon(QIcon("icons/chemistry_1.png"))
        self.show()
        
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    sys.exit(app.exec())
    