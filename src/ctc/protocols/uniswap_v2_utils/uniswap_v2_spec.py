import typing

from ctc import spec


trade_fee = 0.003


class PoolTokensMetadata(typing.TypedDict):
    x_address: spec.Address
    y_address: spec.Address
    x_symbol: str
    y_symbol: str
    x_decimals: int
    y_decimals: int


class PoolState(typing.TypedDict):
    x_reserves: typing.Union[int, float]
    y_reserves: typing.Union[int, float]
    lp_total_supply: typing.Union[int, float]


class PoolStateByBlock(typing.TypedDict):
    x_reserves: list[typing.Union[int, float]]
    y_reserves: list[typing.Union[int, float]]
    lp_total_supply: list[typing.Union[int, float]]

# class PoolState(typing.TypedDict):
#     x_reserves: int
#     y_reserves: int
#     lp_total_supply: int


# class PoolStateNormalized(typing.TypedDict):
#     x_reserves: float
#     y_reserves: float
#     lp_total_supply: float


# class PoolStateByBlock(typing.TypedDict):
#     x_reserves: list[int]
#     y_reserves: list[int]
#     lp_total_supply: list[int]


# class PoolStateNormalizedByBock(typing.TypedDict):
#     x_reserves: list[float]
#     y_reserves: list[float]
#     lp_total_supply: list[float]

