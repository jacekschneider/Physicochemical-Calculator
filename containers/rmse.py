from utils import *


@dataclass(frozen=True)
class RMSE():
    regdata : pd.DataFrame
    model_id : int
    cac_data : dict