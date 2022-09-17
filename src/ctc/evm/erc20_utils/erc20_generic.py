from __future__ import annotations

import typing

from ctc import spec
from . import erc20_spec
from . import erc20_metadata


async def async_erc20_eth_call(
    function_name: str,
    token: spec.ERC20Reference,
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    **rpc_kwargs: typing.Any,
) -> typing.Any:
    """perform eth_call for an erc20"""

    from ctc import rpc

    address = await erc20_metadata.async_get_erc20_address(token)
    return await rpc.async_eth_call(
        to_address=address,
        function_abi=erc20_spec.erc20_function_abis[function_name],
        block_number=block,
        **rpc_kwargs,
    )


async def async_erc20s_eth_calls(
    function_name: str,
    tokens: typing.Iterable[spec.ERC20Reference],
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    **rpc_kwargs: typing.Any,
) -> list[typing.Any]:
    """perform eth_call for multiple erc20s"""

    import asyncio
    from ctc import rpc

    coroutines = [
        erc20_metadata.async_get_erc20_address(token) for token in tokens
    ]
    addresses = await asyncio.gather(*coroutines)
    return await rpc.async_batch_eth_call(
        to_addresses=addresses,
        function_abi=erc20_spec.erc20_function_abis[function_name],
        block_number=block,
        **rpc_kwargs,
    )


async def async_erc20_eth_call_by_block(
    function_name: str,
    token: spec.ERC20Reference,
    *,
    blocks: typing.Iterable[spec.BlockNumberReference],
    **rpc_kwargs: typing.Any,
) -> list[typing.Any]:
    """perform eth_call for an erc20 across multiple blocks"""

    from ctc import rpc

    address = await erc20_metadata.async_get_erc20_address(token)
    return await rpc.async_batch_eth_call(
        to_address=address,
        function_abi=erc20_spec.erc20_function_abis[function_name],
        block_numbers=blocks,
        **rpc_kwargs,
    )
