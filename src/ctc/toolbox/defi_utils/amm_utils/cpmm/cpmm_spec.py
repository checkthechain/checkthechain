from __future__ import annotations

from typing_extensions import TypedDict, NotRequired


class Trade(TypedDict):
    x_bought: int | float
    x_sold: int | float
    y_bought: int | float
    y_sold: int | float
    fee_rate: float
    new_pool: NewPoolState


class Mint(TypedDict):
    x_deposited: int | float
    y_deposited: int | float
    lp_minted: int | float
    new_pool: NewPoolState


class Burn(TypedDict):
    x_withdrawn: int | float
    y_withdrawn: int | float
    lp_burned: int | float
    new_pool: NewPoolState


class NewPoolState(TypedDict):
    x_reserves: int | float
    y_reserves: int | float
    lp_total_supply: NotRequired[int | float]


class TradeSummary(TypedDict):
    end_slippage_x_per_y: int | float
    end_slippage_y_per_x: int | float
    mean_slippage_x_per_y: int | float
    mean_slippage_y_per_x: int | float
    mean_x_per_y: int | float
    mean_y_per_x: int | float
    x_per_y_start: int | float
    y_per_x_start: int | float
    x_per_y_end: int | float
    y_per_x_end: int | float
    x_fees: int | float
    y_fees: int | float
    trade_results: Trade
