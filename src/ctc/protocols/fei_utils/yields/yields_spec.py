from __future__ import annotations

import typing
from typing_extensions import TypedDict

from ctc import spec


FEI = '0x956f47f50a910163d8bf957cf5846d573e7f87ca'


class FeiYieldPayload(TypedDict):

    # metadata
    version: str
    name: str

    # time data
    n_samples: int
    interval_size: str
    window_size: str
    timestamps: list[int]
    block_numbers: list[int]

    # farms
    data: typing.Mapping[str, YieldSourceData]


class YieldSourceData(TypedDict):

    # metadata
    name: str
    category: typing.Literal['lending', 'dex']
    platform: str
    staked_tokens: list[spec.Address]
    reward_tokens: list[spec.Address]

    # metrics
    tvl_history: list[float]
    tvl_history_units: str
    current_yield: dict[str, list[float]]
    current_yield_units = dict[str, str]
    yield_history: dict[str, list[float]]
    yield_history_units: dict[str, str]

