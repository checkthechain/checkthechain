from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import pandas

    from typing_extensions import TypeGuard


def is_dataframe(candidate) -> TypeGuard['pandas.core.frame.DataFrame']:
    import pandas as pd
    return isinstance(candidate, pd.DataFrame)

