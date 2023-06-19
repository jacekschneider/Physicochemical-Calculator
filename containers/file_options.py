from utils import *

@dataclass
class FileOptions():
    
    encoding : str = 'UTF-16'
    separator : str = ','
    index_column_start : int = 1
    index_column_step : int = 2
    average : bool = False