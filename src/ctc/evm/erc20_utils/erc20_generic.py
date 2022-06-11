from __future__ import annotations

import typing

from ctc import rpc
from ctc import spec
from .. import address_utils
from .. import evm_spec


async def async_get_erc20_address(
    token: spec.ERC20Reference,
    network: spec.NetworkReference = None,
) -> spec.ERC20Address:
    """return address of input token, input as either symbol or address"""

    if address_utils.is_address_str(token):
        return token
    elif isinstance(token, str):
        from ctc import db

        metadata = await db.async_query_erc20_metadata(
            symbol=token,
            network=network,
        )
        if metadata is not None:
            return metadata['address']

    raise Exception('could not get token address')


#
# # generic erc20 calls
#


async def async_erc20_eth_call(
    function_name: str,
    token: spec.ERC20Reference,
    block: typing.Optional[spec.BlockNumberReference] = None,
    **rpc_kwargs: typing.Any,
) -> typing.Any:
    """perform eth_call for an erc20"""
    address = await async_get_erc20_address(token)
    return await rpc.async_eth_call(
        to_address=address,
        function_abi=evm_spec.erc20_function_abis[function_name],
        block_number=block,
        **rpc_kwargs,
    )


async def async_erc20s_eth_calls(
    function_name: str,
    tokens: typing.Iterable[spec.ERC20Reference],
    block: typing.Optional[spec.BlockNumberReference] = None,
    **rpc_kwargs: typing.Any,
) -> list[typing.Any]:
    """perform eth_call for multiple erc20s"""

    import asyncio

    coroutines = [async_get_erc20_address(token) for token in tokens]
    addresses = await asyncio.gather(*coroutines)
    return await rpc.async_batch_eth_call(
        to_addresses=addresses,
        function_abi=evm_spec.erc20_function_abis[function_name],
        block_number=block,
        **rpc_kwargs,
    )


async def async_erc20_eth_call_by_block(
    function_name: str,
    token: spec.ERC20Reference,
    blocks: typing.Iterable[spec.BlockNumberReference],
    **rpc_kwargs: typing.Any,
) -> list[typing.Any]:
    """perform eth_call for an erc20 across multiple blocks"""

    address = await async_get_erc20_address(token)
    return await rpc.async_batch_eth_call(
        to_address=address,
        function_abi=evm_spec.erc20_function_abis[function_name],
        block_numbers=blocks,
        **rpc_kwargs,
    )
