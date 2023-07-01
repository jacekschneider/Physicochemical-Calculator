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

@dataclass
class GraphOptions():
    id : str
    label_left : str
    label_bottom : str
    title : str = ""
    title_size : int = 18
    fontsize : int = 25
    fontcolor: list = field(default_factory=lambda:[255, 255, 255], init=False)
    legend_on : bool = True
    legend_textsize : int = 10