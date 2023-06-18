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