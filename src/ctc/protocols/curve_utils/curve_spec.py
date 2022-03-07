"""
see https://github.com/curvefi/curve-pool-registry
"""
from __future__ import annotations

import typing
from typing_extensions import TypedDict

from ctc import spec


three_pool_lp = '0x6c3f90f043a72fa612cbac8115ee7e52bde6e490'
three_pool = '0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7'
three_pool_token_index = {
    'DAI': 0,
    'USDC': 1,
    'USDT': 2,
}
three_pool_coins = ['DAI', 'USDC', 'USDT']


class CurvePoolMetadata(TypedDict):
    token_addresses: list[spec.Address]
    token_symbols: list[str]
    token_decimals: list[int]
    A: int


class CurveTrade(TypedDict):
    token_sold: spec.Address
    token_bought: spec.Address
    amount_sold: typing.Union[int, float]
    amount_bought: typing.Union[int, float]

