from utils import *
from containers.measurement import Measurement
from containers.file_options import FileOptions


class DataLoaderWorker(QObject):
    emit_measurements = Signal(list)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.measurements_raw:list[Measurement] = []
        self.measurements_edited:list[Measurement] = []
        self.fo:FileOptions = FileOptions(separator=r'\t')
    
    @dispatch(FileOptions)
    def load(self, fo:FileOptions):
        self.fo = fo
    
    @dispatch(str)
    def load(self, dirpath:str):
        self.measurements_raw.clear()
        files:list[str] = [str(file)for file in list(Path(dirpath).glob('*.txt'))]
        # must be sorted
        unsorted_values = [float(re.findall('\d+(?:\.\d+)?', filename.replace(',', '.'))[-1]) for filename in files]
        sorted_files = [filename for _, filename in sorted(zip(unsorted_values, files), reverse=True)]
        for file in sorted_files:
            measurement = Measurement(path=file, encoding=self.fo.encoding, separator=self.fo.separator,
                                      index_column_start=self.fo.index_column_start, index_column_step=self.fo.index_column_step)
            self.measurements_raw.append(measurement)
            self.measurements_edited = copy.deepcopy(self.measurements_raw)
        self.emit_measurements.emit(self.measurements_edited)
        print("Data loaded successfully")
        
    @dispatch(list)
    def load(self, measurements:list):
        self.measurements_edited = measurements
        self.emit_measurements.emit(self.measurements_edited)
        
    def get_measurements_raw(self)->list:
        return self.measurements_raw

    def get_measurements(self)->list:
        return self.measurements_edited