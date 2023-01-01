from __future__ import annotations

import typing

from ctc import spec
from . import erc4626_spec


async def async_get_erc4626_asset(
    token: spec.Address,
    *,
    context: spec.Context = None,
    block: spec.BlockNumberReference | None = None,
) -> spec.Address:
    """get asset address of ERC-4626 vault"""
    from ctc import rpc

    asset: spec.Address = await rpc.async_eth_call(
        to_address=token,
        context=context,
        function_abi=erc4626_spec.erc4626_function_abis['asset'],
        block_number=block,
    )
    return asset


async def async_get_erc4626s_assets(
    tokens: typing.Sequence[spec.Address],
    *,
    context: spec.Context = None,
    block: spec.BlockNumberReference | None = None,
) -> typing.Sequence[spec.Address]:
    """get asset addresses of ERC-4626 vaults"""
    from ctc import rpc

    assets: typing.Sequence[spec.Address] = await rpc.async_batch_eth_call(
        to_addresses=tokens,
        context=context,
        function_abi=erc4626_spec.erc4626_function_abis['asset'],
        block_number=block,
    )
    return assets
