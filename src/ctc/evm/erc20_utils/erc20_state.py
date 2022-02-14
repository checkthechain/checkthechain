from __future__ import annotations

import typing

from ctc import spec
from ctc import rpc

from .. import evm_spec
from . import erc20_normalize
from . import erc20_generic


#
# # total supply
#


async def async_get_erc20_total_supply(
    token: spec.ERC20Reference,
    block: spec.BlockNumberReference = 'latest',
    normalize: bool = True,
    provider: spec.ProviderSpec = None,
    **rpc_kwargs,
) -> typing.Union[int, float]:
    """"""

    total_supply = await erc20_generic.async_erc20_eth_call(
        token=token,
        function_name='totalSupply',
        block=block,
        provider=provider,
        **rpc_kwargs,
    )

    if normalize:
        total_supply = await erc20_normalize.async_normalize_erc20_quantity(
            quantity=total_supply, token=token, provider=provider
        )

    return total_supply


async def async_get_erc20s_total_supplies(
    tokens: typing.Sequence[spec.ERC20Reference],
    block: spec.BlockNumberReference = 'latest',
    normalize: bool = True,
    provider: spec.ProviderSpec = None,
    **rpc_kwargs,
) -> typing.Union[list[int], list[float]]:
    """"""

    total_supplies = await erc20_generic.async_erc20s_eth_calls(
        tokens=tokens, function_name='totalSupply', block=block, **rpc_kwargs
    )

    if normalize:
        total_supplies = (
            await erc20_normalize.async_normalize_erc20s_quantities(
                tokens=tokens, quantities=total_supplies, provider=provider
            )
        )

    return total_supplies


async def async_get_erc20_total_supply_by_block(
    token: spec.ERC20Reference,
    blocks: typing.Sequence[spec.BlockNumberReference],
    normalize: bool = True,
    provider: spec.ProviderSpec = None,
    **rpc_kwargs,
) -> typing.Union[list[int], list[float]]:

    total_supplies = await erc20_generic.async_erc20_eth_call_by_block(
        token=token,
        function_name='totalSupply',
        blocks=blocks,
        provider=provider,
        **rpc_kwargs,
    )

    if normalize:
        total_supplies = (
            await erc20_normalize.async_normalize_erc20_quantities_by_block(
                token=token,
                quantities=total_supplies,
                provider=provider,
                blocks=blocks,
            )
        )

    return total_supplies


#
# # balance of
#


async def async_get_erc20_balance_of(
    address: spec.Address,
    token: spec.ERC20Address,
    block: spec.BlockNumberReference = 'latest',
    normalize: bool = True,
    provider: spec.ProviderSpec = None,
    **rpc_kwargs,
) -> typing.Union[int, float]:

    balance = await erc20_generic.async_erc20_eth_call(
        token=token,
        function_name='balanceOf',
        block=block,
        function_parameters=[address],
        provider=provider,
        **rpc_kwargs,
    )

    if normalize:
        balance = await erc20_normalize.async_normalize_erc20_quantity(
            quantity=balance, token=token, provider=provider, block=block
        )

    return balance


async def async_get_erc20_balance_of_addresses(
    addresses: typing.Sequence[spec.Address],
    token: spec.ERC20Address,
    block: spec.BlockNumberReference = 'latest',
    normalize: bool = True,
    provider: spec.ProviderSpec = None,
    **rpc_kwargs,
) -> typing.Union[list[int], list[float]]:

    balances = await rpc.async_batch_eth_call(
        to_address=token,
        block_number=block,
        function_abi=evm_spec.erc20_abis['balanceOf'],
        function_parameter_list=[[address] for address in addresses],
        provider=provider,
        **rpc_kwargs,
    )

    if normalize:
        balances = await erc20_normalize.async_normalize_erc20_quantities(
            quantities=balances, token=token, provider=provider, block=block
        )

    return balances


async def async_get_erc20s_balance_of(
    address: spec.Address,
    tokens: typing.Sequence[spec.ERC20Address],
    block: spec.BlockNumberReference = 'latest',
    normalize: bool = True,
    provider: spec.ProviderSpec = None,
    **rpc_kwargs,
) -> typing.Union[list[int], list[float]]:
    """"""

    balances = await erc20_generic.async_erc20s_eth_calls(
        tokens=tokens,
        function_name='balanceOf',
        block=block,
        function_parameters=[address],
        provider=provider,
        **rpc_kwargs,
    )

    if normalize:
        balances = await erc20_normalize.async_normalize_erc20s_quantities(
            quantities=balances, tokens=tokens, provider=provider, block=block,
        )

    return balances


async def async_get_erc20_balance_of_by_block(
    address: spec.Address,
    token: spec.ERC20Reference,
    blocks: typing.Sequence[spec.BlockNumberReference],
    normalize=True,
    provider: spec.ProviderSpec = None,
    empty_token=0,
    **rpc_kwargs,
) -> typing.Union[list[int], list[float]]:
    """"""

    balances = await erc20_generic.async_erc20_eth_call_by_block(
        token=token,
        function_name='balanceOf',
        blocks=blocks,
        function_parameters=[address],
        provider=provider,
        empty_token=empty_token,
        **rpc_kwargs,
    )

    if normalize:
        balances = (
            await erc20_normalize.async_normalize_erc20_quantities_by_block(
                quantities=balances,
                token=token,
                provider=provider,
                blocks=blocks,
            )
        )

    return balances


#
# # allowance
#


async def async_get_erc20_allowance(
    token: spec.ERC20Reference,
    address: spec.Address,
    block: spec.BlockNumberReference,
    normalize: bool = True,
    provider: spec.ProviderSpec = None,
) -> typing.Union[int, float]:

    allowance = await erc20_generic.async_erc20_eth_call(
        token=token,
        function_name='allowance',
        block=block,
        function_parameters=[address],
        provider=provider,
    )

    if normalize:
        allowance = await erc20_normalize.async_normalize_erc20_quantity(
            quantity=allowance, token=token, provider=provider, block=block
        )

    return allowance


async def async_get_erc20_allowance_by_block(
    token: spec.ERC20Reference,
    address: spec.Address,
    blocks: typing.Sequence[spec.BlockNumberReference],
    normalize: bool = True,
    provider: spec.ProviderSpec = None,
) -> typing.Union[list[int], list[float]]:

    allowances = await erc20_generic.async_erc20_eth_call_by_block(
        token=token,
        function_name='allowance',
        blocks=blocks,
        function_parameters=[address],
        provider=provider,
    )

    if normalize:
        allowances = (
            await erc20_normalize.async_normalize_erc20_quantities_by_block(
                quantities=allowances,
                token=token,
                provider=provider,
                blocks=blocks,
            )
        )

    return allowances


async def async_get_erc20s_allowances(
    tokens: typing.Sequence[spec.ERC20Reference],
    address: spec.Address,
    block: spec.BlockNumberReference,
    normalize: bool = True,
    provider: spec.ProviderSpec = None,
) -> typing.Union[list[int], list[float]]:

    allowances = await erc20_generic.async_erc20s_eth_calls(
        tokens=tokens,
        function_name='allowance',
        block=block,
        function_parameters=[address],
        provider=provider,
    )

    if normalize:
        allowances = await erc20_normalize.async_normalize_erc20s_quantities(
            quantities=allowances, tokens=tokens, provider=provider, block=block
        )

    return allowances


async def async_get_erc20s_allowances_by_address(
    token: spec.ERC20Reference,
    addresses: typing.Sequence[spec.Address],
    block: spec.BlockNumberReference,
    normalize: bool = True,
    provider: spec.ProviderSpec = None,
):

    allowances = await rpc.async_batch_eth_call(
        to_address=token,
        block_number=block,
        function_abi=evm_spec.erc20_abis['allowance'],
        function_parameter_list=[[address] for address in addresses],
        provider=provider,
    )

    if normalize:
        allowances = await erc20_normalize.async_normalize_erc20_quantities(
            quantities=allowances, token=token, provider=provider, block=block
        )

    return allowances

