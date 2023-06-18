from utils import *

class ExportWorker(QObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.I1I3 = None
        
        
    @Slot(pd.DataFrame)
    def get_I1I3(self, I1I3:pd.DataFrame):
        self.I1I3:pd.DataFrame = I1I3
        
    def export_I1I3(self):
        if self.I1I3 is None:
            # !JSCH
            print("There is no I1/I3")
        else:
            file_path, selected_filter = QFileDialog.getSaveFileName(
                caption="Select a directory",
                directory=str(Path().absolute()),
                filter="CSV File (*.csv)"
            )
            if file_path:
                self.I1I3.to_csv(file_path)