from utils import *

class DataLoaderWorker(QObject):
    emit_measurements = Signal(list)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.measurements_raw:list[Measurement] = []
        self.measurements_edited:list[Measurement] = []
    
    @dispatch(str)
    def load(self, dirpath:str):
        self.measurements_raw.clear()
        files:list[str] = [str(file)for file in list(Path(dirpath).glob('*.txt'))]
        # must be sorted
        unsorted_values = [float(re.findall('\d+(?:\.\d+)?', filename.replace(',', '.'))[-1]) for filename in files]
        sorted_files = [filename for _, filename in sorted(zip(unsorted_values, files), reverse=True)]
        for file in sorted_files:
            measurement = Measurement(path=file, encoding="utf-16", separator="\t")
            self.measurements_raw.append(measurement)
            self.measurements_edited = copy.deepcopy(self.measurements_raw)
        self.emit_measurements.emit(self.measurements_edited)
        
    @dispatch(list)
    def load(self, measurements:list):
        self.measurements_edited = measurements
        self.emit_measurements.emit(self.measurements_edited)
        
    def get_measurements_raw(self)->list:
        return self.measurements_raw

    def get_measurements(self)->list:
        return self.measurements_edited