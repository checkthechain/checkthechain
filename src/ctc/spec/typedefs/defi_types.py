from __future__ import annotations

import typing
from typing_extensions import TypedDict, NotRequired

from . import external_types


class RawDexTrades(TypedDict):
    # each should be  series indexed by block number
    timestamp: NotRequired[external_types.Series | typing.Sequence[int] | None]
    transaction_hash: external_types.Series
    recipient: NotRequired[external_types.Series | None]
    bought_id: external_types.Series
    sold_id: external_types.Series
    bought_amount: external_types.Series
    sold_amount: external_types.Series
