from __future__ import annotations

import typing
from typing_extensions import TypedDict

from ctc import spec


trade_fee = 0.003


class PoolTokensMetadata(TypedDict):
    x_address: spec.Address
    y_address: spec.Address
    x_symbol: str
    y_symbol: str
    x_decimals: int
    y_decimals: int


class PoolState(TypedDict):
    x_reserves: typing.Union[int, float]
    y_reserves: typing.Union[int, float]
    lp_total_supply: typing.Union[int, float]


class PoolStateByBlock(TypedDict):
    x_reserves: list[typing.Union[int, float]]
    y_reserves: list[typing.Union[int, float]]
    lp_total_supply: list[typing.Union[int, float]]

