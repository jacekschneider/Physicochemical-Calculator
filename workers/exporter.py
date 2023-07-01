''' Physicochemical Calculator - calculate automatically CMC value with emission spectrum data
    Copyright (C) 2023  Jacek Schneider, Konrad Wesenfeld

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.'''
    
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