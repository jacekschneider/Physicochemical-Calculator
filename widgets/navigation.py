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

class WidgetNavigation(QWidget):
    emit_dirpath = Signal(str)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        loadUi("ui/ui_navigation.ui", self)
        self.pb_load_data.clicked.connect(self.open_file_dialog)
        
        # view_files widget
        self.model = QFileSystemModel()
        icon_provider = QFileIconProvider()
        self.model.setIconProvider(icon_provider) 
        self.model.setRootPath("") 
        self.model.setNameFilters(["*.txt"])
        self.model.setNameFilterDisables(False)

        
        self.proxy_model = reSortProxyModel("\d+(?:\.\d+)?")
        self.proxy_model.setSourceModel(self.model)

        self.view_files.setSortingEnabled(True)

    def open_file_dialog(self):
        path_folder = QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            directory=str(pathlib.Path().absolute())
        )
        if path_folder != "":
            print("Loading Data...")
            self.emit_dirpath.emit(path_folder)
            self.le_path.setText(path_folder)
            self.view_files.setModel(self.proxy_model)
            root_index = self.model.index(QDir.cleanPath(path_folder))
            proxy_index = self.proxy_model.mapFromSource(root_index)
            self.view_files.setRootIndex(proxy_index)
            self.view_files.hideColumn(1)
            self.view_files.hideColumn(2)
            self.view_files.hideColumn(3)
            
        else:
            #!JSCH
            pass
    
    def clear(self):
        self.le_path.setText("")
        self.view_files.setModel(None)