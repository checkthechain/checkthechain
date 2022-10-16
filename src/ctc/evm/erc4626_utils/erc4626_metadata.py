from __future__ import annotations

import typing

from ctc import rpc
from ctc import spec
from . import erc4626_spec


async def async_get_erc4626_asset(
    token: spec.Address,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> spec.Address:

    asset: spec.Address = await rpc.async_eth_call(
        to_address=token,
        provider=provider,
        function_abi=erc4626_spec.erc4626_function_abis['asset'],
        block_number=block,
    )
    return asset


async def async_get_erc4626s_assets(
    tokens: typing.Sequence[spec.Address],
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> typing.Sequence[spec.Address]:

    assets: typing.Sequence[spec.Address] = await rpc.async_batch_eth_call(
        to_addresses=tokens,
        provider=provider,
        function_abi=erc4626_spec.erc4626_function_abis['asset'],
        block_number=block,
    )
    return assets
