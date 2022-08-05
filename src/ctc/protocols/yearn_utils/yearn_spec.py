from __future__ import annotations

import typing

from ctc import spec

if typing.TYPE_CHECKING:
    from typing_extensions import TypedDict

    RawAssetTvlBreakdown = tuple[
        spec.Address,
        spec.Address,
        int,
        int,
        int,
        int,
        int,
    ]

    class AssetTvlBreakdown(TypedDict):
        asset: spec.Address
        token: spec.Address
        token_price: int
        underlying_balance: int
        delegated_balance: int
        adjusted_balance: int
        tvl: int

    class ApiVault(TypedDict):
        address: str
        inception: int
        symbol: str
        name: str
        display_name: str
        icon: str
        token: typing.Mapping[str, typing.Any]
        # token.name
        # token.symbol
        # token.address
        # token.decimals
        # token.display_name
        # token.icon
        tvl: typing.Mapping[str, typing.Any]
        # tvl.total_assets
        # tvl.price
        # tvl.tvl
        apy: typing.Mapping[str, typing.Any]
        # apy.type
        # apy.gross_apr
        # apy.net_apy
        # apy.fees
        # apy.fees.performance
        # apy.fees.withdrawal
        # apy.fees.management
        # apy.fees.keep_crv
        # apy.fees.cvx_keep_crv
        # apy.points
        # apy.points.week_ago
        # apy.points.month_ago
        # apy.points.month_ago
        # apy.composite
        # apy.composite.boost
        # apy.composite.pool_apy
        # apy.composite.base_apr
        # apy.composite.boosted_apr
        # apy.composite.cvx_apr
        # apy.composite.rewards_apr
        strategies: typing.Sequence[typing.Mapping[str, str]]
        # strategies[idx].address
        # strategies[idx].name
        endorsed: bool
        version: str
        decimals: int
        type: str
        emergency_shutdown: bool
        updated: int
