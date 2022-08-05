from __future__ import annotations

import typing

from ctc import rpc
from ctc import spec

from . import yearn_spec


async def async_get_tvl_adapter_assets(
    adapter: spec.Address,
) -> typing.Sequence[spec.Address]:

    addresses: typing.Sequence[spec.Address] = await rpc.async_eth_call(
        to_address=adapter,
        function_name='assetsAddresses',
        n_parameters=0,
    )
    return addresses


async def async_get_tvl_adapter_assets_data(
    adapter: spec.Address,
) -> typing.Sequence[yearn_spec.AssetTvlBreakdown]:
    data = await rpc.async_eth_call(
        to_address=adapter,
        function_name='assetsTvlBreakdown',
        n_parameters=0,
    )

    tvls: typing.Sequence[yearn_spec.AssetTvlBreakdown] = [
        {
            'asset': datum[0],
            'token': datum[1],
            'token_price': datum[2],
            'underlying_balance': datum[3],
            'delegated_balance': datum[4],
            'adjusted_balance': datum[5],
            'tvl': datum[6],
        }
        for datum in data
    ]

    return tvls
