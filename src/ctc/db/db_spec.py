from __future__ import annotations

from typing_extensions import TypedDict

from ctc import spec


class ERC20Metadata(TypedDict):
    address: spec.Address
    symbol: str
    decimals: int

