from __future__ import annotations

import typing

from ctc import evm
from ctc import rpc
from ctc import spec

from . import aave_spec


async def async_get_underlying_asset(
    pool_token: spec.Address,
    provider: spec.ProviderReference = None,
) -> spec.Address:
    function_abi: spec.FunctionABI = {
        'name': 'UNDERLYING_ASSET_ADDRESS',
        'inputs': [],
        'outputs': [{'type': 'address'}],
    }
    result = await rpc.async_eth_call(
        to_address=pool_token,
        function_abi=function_abi,
        provider=provider,
    )
    if not isinstance(result, str):
        raise Exception('invalid rpc result')
    return result


async def async_get_reserves_list(
    *,
    block: spec.BlockNumberReference | None = None,
    provider: spec.ProviderReference = None,
) -> typing.Sequence[spec.Address]:

    network = rpc.get_provider_network(provider)
    address = aave_spec.get_aave_address('LendingPool', network=network)

    if block is not None:
        block = evm.standardize_block_number(block)

    reserves: typing.Sequence[spec.Address] = await rpc.async_eth_call(
        to_address=address,
        function_name='getReservesList',
        provider=provider,
        block_number=block,
    )

    return reserves
