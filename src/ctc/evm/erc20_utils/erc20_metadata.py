from __future__ import annotations

import typing

from ctc import spec
from . import erc20_generic


#
# # decimals
#


async def async_get_erc20_decimals(
    token: spec.ERC20Reference,
    block: spec.BlockNumberReference = 'latest',
    **rpc_kwargs
) -> int:
    """get decimals of an erc20"""
    return await erc20_generic.async_erc20_eth_call(
        function_name='decimals', token=token, block=block, **rpc_kwargs
    )


async def async_get_erc20s_decimals(
    tokens: typing.Iterable[spec.ERC20Reference],
    block: spec.BlockNumberReference = 'latest',
    **rpc_kwargs
) -> list[int]:
    """get decimals of multiple erc20s"""
    return await erc20_generic.async_erc20s_eth_calls(
        function_name='decimals', tokens=tokens, block=block, **rpc_kwargs
    )


async def async_get_erc20_decimals_by_block(
    token: spec.ERC20Reference, blocks=None, **rpc_kwargs
) -> list[int]:
    """get decimals of an erc20 across multiple blocks"""
    return await erc20_generic.async_erc20_eth_call_by_block(
        function_name='decimals', token=token, blocks=blocks, **rpc_kwargs
    )


#
# # name
#


async def async_get_erc20_name(
    token: spec.ERC20Reference,
    block: spec.BlockNumberReference = 'latest',
    **rpc_kwargs
) -> str:
    """get name of an erc20"""
    return await erc20_generic.async_erc20_eth_call(
        function_name='name', token=token, block=block, **rpc_kwargs
    )


async def async_get_erc20s_names(
    tokens: typing.Iterable[spec.ERC20Reference],
    block: spec.BlockNumberReference = 'latest',
    **rpc_kwargs
) -> list[str]:
    """get name of multiple erc20s"""
    return await erc20_generic.async_erc20s_eth_calls(
        function_name='name', tokens=tokens, block=block, **rpc_kwargs
    )


async def async_get_erc20_name_by_block(
    token: spec.ERC20Reference,
    blocks: typing.Iterable[spec.BlockNumberReference],
    **rpc_kwargs
) -> list[str]:
    """get name of an erc20 across multiple blocks"""
    return await erc20_generic.async_erc20_eth_call_by_block(
        function_name='name', token=token, blocks=blocks, **rpc_kwargs
    )


#
# # symbol
#


async def async_get_erc20_symbol(
    token: spec.ERC20Reference,
    block: spec.BlockNumberReference = 'latest',
    **rpc_kwargs
):
    """get symbol of an erc20"""
    return await erc20_generic.async_erc20_eth_call(
        function_name='symbol', token=token, block=block, **rpc_kwargs
    )


async def async_get_erc20s_symbols(
    tokens: typing.Iterable[spec.ERC20Reference],
    block: spec.BlockNumberReference = 'latest',
    **rpc_kwargs
):
    """get symbol of multiple erc20s"""
    return await erc20_generic.async_erc20s_eth_calls(
        function_name='symbol', tokens=tokens, block=block, **rpc_kwargs
    )


async def async_get_erc20_symbol_by_block(
    token: spec.ERC20Reference,
    blocks: typing.Iterable[spec.BlockNumberReference],
    **rpc_kwargs
):
    """get symbol of an erc20 across multiple blocks"""
    return await erc20_generic.async_erc20_eth_call_by_block(
        function_name='symbol', token=token, blocks=blocks, **rpc_kwargs
    )

