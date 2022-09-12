from __future__ import annotations

import typing

import tooltime

from ctc import spec
from . import uniswap_v2_dex


class SushiDEX(uniswap_v2_dex.UniswapV2DEX):
    _pool_factories = {1: ['0xc0aee478e3658e2610c5f7a4a2e1777ce9e4f2ac']}

    # @classmethod
    # async def async_get_new_pools(
    #     cls,
    #     *,
    #     factory: spec.Address,
    #     start_block: spec.BlockNumberReference | None = None,
    #     end_block: spec.BlockNumberReference | None = None,
    #     start_time: tooltime.Timestamp | None = None,
    #     end_time: tooltime.Timestamp | None = None,
    # ) -> typing.Sequence[spec.DexPool]:

    #     return await uniswap_v2_dex.UniswapV2DEX.async_get_new_pools(
    #         factory=factory,
    #         start_block=start_block,
    #         end_block=end_block,
    #         start_time=start_time,
    #         end_time=end_time,
    #     )

    # @classmethod
    # async def _async_get_pool_assets_from_node(
    #     cls,
    #     pool: spec.Address,
    #     *,
    #     network: spec.NetworkReference | None = None,
    #     provider: spec.ProviderReference | None = None,
    #     block: spec.BlockNumberReference | None = None,
    # ) -> typing.Sequence[spec.Address]:
    #     return (
    #         await uniswap_v2_dex.UniswapV2DEX._async_get_pool_assets_from_node(
    #             pool=pool,
    #             network=network,
    #             provider=provider,
    #             block=block,
    #         )
    #     )

    # @classmethod
    # async def _async_get_pool_raw_trades(
    #     cls,
    #     pool: spec.Address,
    #     *,
    #     start_block: spec.BlockNumberReference | None = None,
    #     end_block: spec.BlockNumberReference | None = None,
    #     start_time: tooltime.Timestamp | None = None,
    #     end_time: tooltime.Timestamp | None = None,
    #     include_timestamps: bool = False,
    #     network: spec.NetworkReference | None = None,
    #     provider: spec.ProviderReference | None = None,
    #     verbose: bool = False,
    # ) -> spec.DataFrame:

    #     return await uniswap_v2_dex.UniswapV2DEX.async_get_pool_trades(
    #         pool=pool,
    #         start_block=start_block,
    #         end_block=end_block,
    #         start_time=start_time,
    #         end_time=end_time,
    #         include_timestamps=include_timestamps,
    #         network=network,
    #         provider=provider,
    #         verbose=verbose,
    #     )
