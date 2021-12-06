import typing

#
# # types
#


class Timescale(typing.TypedDict):
    window_size: str
    interval_size: str


Timestamp = int
Timestamps = list[int]

MetricGroupName = typing.Literal[
    # section: PCV
    'pcv_stats',  # entries = pcv total and CR
    'pcv_by_asset',  # entries = tokens
    'pcv_by_deployment',  # entries = deployments
    # section: FEI
    'prices',  # entry = FEI_USD chainlink
    'dex_volume',  # entries = dex pools
    'dex_tvls',  # entries = dex pools
    'circulating_fei',  # entries = uFEI and pFEI
    'pfei_by_deployment',  # entries = pFEI deployment
    # section: buybacks
    'buybacks',  # entry = FEI spent
]
MetricName = str
MetricSeries = list[typing.SupportsFloat]


class MetricData(typing.TypedDict, total=False):
    values: list[typing.SupportsFloat]
    name: str
    link: str
    units: str


MetricGroup = dict[MetricName, MetricData]


class AnalyticsPayload(typing.TypedDict):

    # metadata
    version: str
    created_at_timestamp: Timestamp

    # timing data
    n_samples: int
    sample_interval: str
    sample_window: str
    timestamps: list[Timestamp]
    block_numbers: list[int]

    # metrics
    metrics: dict[MetricGroupName, MetricGroup]


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


dex_pools = {
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
    'uniswap_v3__fei_usdc_5': {
        'platform': 'Uniswap V3',
        'address': '0x8c54aa2a32a779e6f6fbea568ad85a19e0109c26',
        'other_assets': ['USDC'],
    },
    'uniswap_v3__fei_dai_5': {
        'platform': 'Uniswap V3',
        'address': '0xbb2e5c2ff298fd96e166f90c8abacaf714df14f8',
        'other_assets': ['DAI'],
    },
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

