from __future__ import annotations

import typing
from typing_extensions import Literal, TypedDict

from ctc import spec


FEI = '0x956f47f50a910163d8bf957cf5846d573e7f87ca'
TRIBE = '0xc7283b66eb1eb5fb86327f08e1b5816b0720212b'


class FeiYieldPayload(TypedDict):

    # metadata
    version: str
    name: str

    # time data
    n_samples: int
    interval_size: str
    window_size: str
    timestamps: list[int]
    block_numbers: typing.Sequence[int]
    created_at_timestamp: int

    # farms
    data: typing.Mapping[str, YieldSourceData]  # map of farm_name -> farm_data


class YieldSourceData(TypedDict):

    # metadata
    name: str  # name of farm
    url: str  # link to farm
    category: Literal['Lending', 'DEX']  # category of farm
    platform: str  # defi platform, e.g. 'Aave' or 'Rari'
    staked_tokens: list[spec.Address]  # list of token addresses that are staked
    reward_tokens: list[spec.Address]  # list of token addresses that are earned

    # metrics
    tvl_history: list[float]  # list of TVL values for farm
    tvl_history_units: str  # units of TVL values, usually "USD"
    current_yield: dict[str, float]  # map of "Spot", "7D", and "30D" to yield %
    current_yield_units: dict[str, str]  # either "APY" or "APR" for each entry
    yield_history: dict[str, list[float]]  # map of yield type name to % history
    yield_history_units: dict[str, str]  # either "APY" or "APR" for each entry
