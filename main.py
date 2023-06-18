from utils import *
from widgets.main_window import MainWindow

 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    sys.exit(app.exec())
    