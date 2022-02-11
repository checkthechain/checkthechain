from __future__ import annotations

import typing
from typing_extensions import TypedDict

from ctc import spec


#
# # types
#


class Timescale(TypedDict):
    window_size: str
    interval_size: str


TimescaleShorthand = str
TimescaleSpec = typing.Union[Timescale, TimescaleShorthand]


Timestamp = int
Timestamps = typing.List[int]

MetricName = str
MetricSeries = typing.List[float]


class TimeData(TypedDict):
    timestamps: list[int]
    block_numbers: list[int]
    n_samples: int
    window_size: str
    interval_size: str
    created_at_timestamp: int


class MetricData(TypedDict, total=False):
    values: typing.Union[list[float], list[int]]
    name: str
    link: str
    units: str


class MetricGroupStrict(TypedDict):
    name: str
    metrics: dict[str, MetricData]


class MetricGroup(MetricGroupStrict, total=False):
    order: list[str]


class AnalyticsPayload(TypedDict):

    # metadata
    version: str
    created_at_timestamp: Timestamp

    # timing data
    n_samples: int
    interval_size: str
    window_size: str
    timestamps: list[Timestamp]
    block_numbers: list[int]

    # metrics
    data: dict[str, MetricGroup]


MetricGroupCreator = typing.Callable[[typing.List[int], bool], MetricGroup]
MetricGroupCreatorCoroutine = typing.Callable[
    [typing.List[int], bool],
    typing.Coroutine[typing.Any, typing.Any, MetricGroup],
]
MultiMetricGroupCreator = typing.Callable[
    [typing.List[int], bool],
    typing.Dict[str, MetricGroup],
]
MultiMetricGroupCreatorCoroutine = typing.Callable[
    [typing.List[int], bool],
    typing.Coroutine[typing.Any, typing.Any, typing.Dict[str, MetricGroup]],
]


#
# # specific values
#

payload_timescales = [
    {'window_size': '1h', 'interval_size': '1 minute'},  # 60 datapoints
    {'window_size': '24h', 'interval_size': '10 minute'},  # 144 datapoints
    {'window_size': '7d', 'interval_size': '1 hour'},  # 168 datapoints
    {'window_size': '30d', 'interval_size': '1 day'},  # 30 datapoints
    {'window_size': '90d', 'interval_size': '1 day'},  # 90 datapoints
]


class DexPoolMetadata(TypedDict, total=False):
    platform: str
    address: spec.ContractAddress
    other_assets: list[str]
    fei_index: int
    event_name: str


dex_pools: dict[str, DexPoolMetadata] = {
    'uniswap_v2__fei_eth': {
        'platform': 'Uniswap V2',
        'address': '0x94b0a3d511b6ecdb17ebf877278ab030acb0a878',
        'other_assets': ['WETH'],
    },
    'uniswap_v2__fei_tribe': {
        'platform': 'Uniswap V2',
        'address': '0x9928e4046d7c6513326ccea028cd3e7a91c7590a',
        'other_assets': ['TRIBE'],
    },
    'uniswap_v3__fei_usdc_1': {
        'platform': 'Uniswap V3',
        'address': '0xdf50fbde8180c8785842c8e316ebe06f542d3443',
        'other_assets': ['USDC'],
    },
    'uniswap_v3__fei_usdc_5': {
        'platform': 'Uniswap V3',
        'address': '0x8c54aa2a32a779e6f6fbea568ad85a19e0109c26',
        'other_assets': ['USDC'],
    },
    'uniswap_v3__fei_usdc_30': {
        'platform': 'Uniswap V3',
        'address': '0x5180545835bd68810fb7e11c7160bb7ea4ae8744',
        'other_assets': ['USDC'],
    },
    'uniswap_v3__fei_dai_5': {
        'platform': 'Uniswap V3',
        'address': '0xbb2e5c2ff298fd96e166f90c8abacaf714df14f8',
        'other_assets': ['DAI'],
    },
    # 'balancer_v2': {
    #     'platform': 'Balancer',
    #     'address': '0xba12222222228d8ba445958a75a0704d566bf2c8',
    #     'other_assets': ['ETH', 'TRIBE'],
    # },
    'curve__fei_3crv': {
        'platform': 'Curve',
        'address': '0x06cb22615BA53E60D67Bf6C341a0fD5E718E1655',
        'other_assets': ['3crv'],
        'fei_index': 0,
        'event_name': 'TokenExchangeUnderlying',
    },
    'curve__d3': {
        'platform': 'Curve',
        'address': '0xBaaa1F5DbA42C3389bDbc2c9D2dE134F5cD0Dc89',
        'other_assets': ['FRAX', 'alUSD'],
        'fei_index': 1,
        'event_name': 'TokenExchange',
    },
    'saddle__d4': {
        'platform': 'Saddle',
        'address': '0xC69DDcd4DFeF25D8a793241834d4cc4b3668EAD6',
        'other_assets': ['alUSD', 'FRAX', 'LUSD'],
        'fei_index': 1,
    },
    'sushiswap__fei_dpi': {
        'platform': 'Sushi',
        'address': '0x8775aE5e83BC5D926b6277579c2B0d40c7D9b528',
        'other_assets': ['DPI'],
    },
}

