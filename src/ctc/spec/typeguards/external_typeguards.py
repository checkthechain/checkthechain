
import typing
from typing_extensions import TypeGuard

if typing.TYPE_CHECKING:
    import pandas


def is_dataframe(candidate) -> TypeGuard['pandas.core.frame.DataFrame']:
    import pandas as pd
    return isinstance(candidate, pd.DataFrame)

