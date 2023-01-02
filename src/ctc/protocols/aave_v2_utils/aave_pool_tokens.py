from __future__ import annotations

import typing

from ctc import evm
from ctc import rpc
from ctc import spec

from . import aave_spec


async def async_get_underlying_asset(
    pool_token: spec.Address,
    *,
    context: spec.Context = None,
) -> spec.Address:
    function_abi: spec.FunctionABI = {
        'name': 'UNDERLYING_ASSET_ADDRESS',
        'inputs': [],
        'outputs': [{'type': 'address'}],
    }
    result = await rpc.async_eth_call(
        to_address=pool_token,
        function_abi=function_abi,
        context=context,
    )
    if not isinstance(result, str):
        raise Exception('invalid rpc result')
    return result


async def async_get_reserves_list(
    *,
    block: spec.BlockNumberReference | None = None,
    context: spec.Context = None,
) -> typing.Sequence[spec.Address]:

    address = aave_spec.get_aave_address('LendingPool', context=context)

    if block is not None:
        block = evm.standardize_block_number(block)

    reserves: typing.Sequence[spec.Address] = await rpc.async_eth_call(
        to_address=address,
        function_name='getReservesList',
        block_number=block,
        context=context,
    )

    return reserves

