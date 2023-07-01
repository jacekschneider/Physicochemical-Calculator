from utils import *

class WidgetConsole(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)

        sys.stdout = self

    def write(self, message):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)
        if len(message)>1:
            self.insertPlainText(f"{datetime.now():%Y-%m-%d %H:%M:%S} "+message)
        else:
            self.insertPlainText(message)