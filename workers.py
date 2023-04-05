import pathlib
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import pyqtSlot as Slot, pyqtSignal as Signal, QObject
from reportlab.pdfgen.canvas import Canvas


class ReportWorker(QObject):

    @Slot(list)
    def set_measurements(self, measurements:list):
        self.measurements = measurements
        
    def generate(self):
        file_path, selected_filter = QFileDialog.getSaveFileName(
            caption="Select a directory",
            directory=str(pathlib.Path().absolute()),
            filter="PDF File (*.pdf)"
        )
        if file_path:
            canvas = Canvas(file_path, pagesize=(652, 792))
            canvas.setFillColorRGB(1,0,1)
            canvas.rect(5, 5, 652-10, 792-10, fill=1)
            canvas.setFillColorRGB(1,1,1)
            canvas.rect(10, 10, 652-20, 792-20, fill=1)
            canvas.setFillColorRGB(0,0,0)
            canvas.setFontSize(18)
            canvas.drawString(100, 750, "Physicochemical-Calculator")
            canvas.setTitle("Physicochemical-Calculator")
            canvas.showPage()
            canvas.save()

class CalculatorWorker(QObject):
    
    @Slot(list)
    def set_measurements(self, measurements:list):
        self.measurements = measurements

    @Slot(str)
    def load(self, str):
        pass