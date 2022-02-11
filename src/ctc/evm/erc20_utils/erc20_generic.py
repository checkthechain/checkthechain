from __future__ import annotations

import typing

from ctc import directory
from ctc import rpc
from ctc import spec
from .. import address_utils
from .. import evm_spec


def get_erc20_address(token: spec.ERC20Reference) -> spec.ERC20Address:
    """return address of input token, input as either symbol or address"""
    if address_utils.is_address_str(token):
        return token
    elif isinstance(token, str):
        return directory.get_erc20_address(token)
    else:
        raise Exception('could not get token address')


#
# # generic erc20 calls
#


async def async_erc20_eth_call(
    function_name: str,
    token: spec.ERC20Reference,
    block: spec.BlockNumberReference = 'latest',
    **rpc_kwargs
) -> typing.Any:
    """perform eth_call for an erc20"""

    return await rpc.async_eth_call(
        to_address=get_erc20_address(token),
        function_abi=evm_spec.erc20_abis[function_name],
        block_number=block,
        **rpc_kwargs
    )


async def async_erc20s_eth_calls(
    function_name: str,
    tokens: typing.Iterable[spec.ERC20Reference],
    block: spec.BlockNumberReference = 'latest',
    **rpc_kwargs
) -> list[typing.Any]:
    """perform eth_call for multiple erc20s"""

    return await rpc.async_batch_eth_call(
        to_addresses=[get_erc20_address(token) for token in tokens],
        function_abi=evm_spec.erc20_abis[function_name],
        block_number=block,
        **rpc_kwargs
    )


async def async_erc20_eth_call_by_block(
    function_name: str,
    token: spec.ERC20Reference,
    blocks: typing.Iterable[spec.BlockNumberReference],
    **rpc_kwargs
) -> list[typing.Any]:
    """perform eth_call for an erc20 across multiple blocks"""

    return await rpc.async_batch_eth_call(
        to_address=get_erc20_address(token),
        function_abi=evm_spec.erc20_abis[function_name],
        block_numbers=blocks,
        **rpc_kwargs
    )

