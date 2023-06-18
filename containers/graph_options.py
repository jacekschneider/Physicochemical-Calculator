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