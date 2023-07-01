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
    
from utils import color_gen
from utils import *


@dataclass(frozen=True)
class Measurement():
    
    path : str
    encoding : str = 'UTF-16'
    separator : str = ','
    index_column_start : int = 1
    index_column_step : int = 2
    filename : str = field(init=False)
    concentration : float = field(init=False)
    data : pd.Series = field(init=False)
    
    peak1_raw : int = 373
    peak2_raw : int = 384
    window_width : int = 3
    peaks:dict = field(init=False)
    
    pen_color : list = field(default_factory=lambda:[0, 0, 0], init=False)
    pen_enabled : bool = field(default=False, init=False)
    symbol : str = field(default="o", init=False)
    symbol_brush_color : list = field(default_factory=lambda:[0, 0, 0], init=False)
    symbol_size : int = field(default=7, init=False)
    name : str = field(default="NoName", init=False,)
    displayed : bool = field(default=False, init=False)
    enabled : bool = field(default=False, init=False)
    
    def __post_init__(self):
        self.load_data()
        self.load_peaks()
        self.set_name("Concentration = {}".format(self.concentration))
        self.set_pen_color(color_gen())
        self.set_enabled(True)
        self.set_displayed(True)
    
    def load_data(self):

        filename = self.path.split('\\')[-1] # the last element should be the filename
        object.__setattr__(self, 'filename', filename)
        filename = filename.replace('.txt','').replace(',','.')
        # assuming there may be numbers in the filename, but not after the concentration
        con = re.findall('\d+(?:\.\d+)?', filename)[-1] # extracts floats and integers
        concentration= float(con)

        raw = pd.read_csv(self.path, encoding=self.encoding, sep=self.separator, engine='python')
        Yval = raw[raw.columns[raw.columns.str.startswith('Y')]]
        # filtering out Y values, excluding every other column because of bad data
        # may heve to be removed
        Yval = Yval[Yval.columns[self.index_column_start::self.index_column_step]]
        Yval = Yval.mean(axis=1)
        Xval = raw['X']
        data = pd.concat([Xval,Yval],axis=1, keys=['X','Y'])
        data.dropna(inplace=True)
        object.__setattr__(self, 'data', data.set_index('X'))
        object.__setattr__(self, 'concentration', concentration)
        
    def load_peaks(self):
        P1_window_low, P1_window_high = self.peak1_raw - self.window_width//2, self.peak1_raw + self.window_width//2
        P2_window_low, P2_window_high = self.peak2_raw - self.window_width//2, self.peak2_raw + self.window_width//2
        P1, P2 = self.data.loc[P1_window_low:P1_window_high], self.data.loc[P2_window_low:P2_window_high]
        
        peak1_max, peak2_max = P1.max(),P2.max()
        peak1_max_id, peak2_max_id = P1.idxmax(), P2.idxmax()
        # indexes of found values are needed for marking them on a plot
        # for data preview concentrations are saved in the column names
        peaks = {
                'Peak 1' : peak1_max,
                'Peak 2' : peak2_max,
                'Peak 1 ID' : peak1_max_id,
                'Peak 2 ID' : peak2_max_id
                }
        object.__setattr__(self, 'peaks', peaks)
    
    @dispatch(list)
    def set_pen_color(self, color:list):
        if len(color) == 3:
            object.__setattr__(self, 'pen_color', color)
            
    @dispatch(str)
    def set_pen_color(self, color:str):
        object.__setattr__(self, 'pen_color', color)
    
    def set_pen_enabled(self, state:bool):
        object.__setattr__(self, 'pen_enabled', state)
        
    def set_symbol(self, symbol:str):
        #JSCH! -> validate symbol
        object.__setattr__(self, 'symbol', symbol)
    
    def set_symbol_brush_color(self, color:list):
        if len(color) == 3:
            object.__setattr__(self, 'symbol_brush_color', color)
    
    def set_symbol_size(self, size:int):
        object.__setattr__(self, 'symbol_size', size)
    
    def set_name(self, name:str):
        object.__setattr__(self, 'name', name)
        
    def set_enabled(self, state:bool):
        object.__setattr__(self, 'enabled', state)
    
    def set_displayed(self, state:bool):
        object.__setattr__(self, 'displayed', state)
    
    def set_window_width(self, width:int):
        object.__setattr__(self, 'window_width', width)
        self.load_peaks()
    
    def set_peak1(self, peak:int):
        object.__setattr__(self, "peak1_raw", peak)
        self.load_peaks()
        
    def set_peak2(self, peak:int):
        object.__setattr__(self, "peak2_raw", peak)
        self.load_peaks()