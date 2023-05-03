from __future__ import annotations

import typing

from ctc import spec

from .. import address_utils
from . import erc20_generic
from . import erc20_normalize
from . import erc20_spec


#
# # total supply
#


async def async_get_erc20_total_supply(
    token: spec.ERC20Reference,
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    normalize: bool = True,
    context: spec.Context = None,
    **rpc_kwargs: typing.Any,
) -> typing.Union[int, float] | None:
    """get total supply of ERC20"""

    if block is None:
        block = 'latest'

    result = await erc20_generic.async_erc20_eth_call(
        token=token,
        function_name='totalSupply',
        block=block,
        context=context,
        **rpc_kwargs,
    )
    if rpc_kwargs.get('convert_reverts_to_none') and result is None:
        return result
    total_supply: int | float = result

    if normalize:
        total_supply = await erc20_normalize.async_normalize_erc20_quantity(
            quantity=total_supply, token=token, context=context
        )

    return total_supply


async def async_get_erc20s_total_supplies(
    tokens: typing.Sequence[spec.ERC20Reference],
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    normalize: bool = True,
    context: spec.Context = None,
    **rpc_kwargs: typing.Any,
) -> typing.Union[typing.Sequence[int], typing.Sequence[float]]:
    """get total supplies of ERC20s"""

    if block is None:
        block = 'latest'

    total_supplies = await erc20_generic.async_erc20s_eth_calls(
        tokens=tokens, function_name='totalSupply', block=block, context=context, **rpc_kwargs
    )

    if normalize:
        total_supplies = (
            await erc20_normalize.async_normalize_erc20s_quantities(
                tokens=tokens, quantities=total_supplies, context=context
            )
        )

    return total_supplies


async def async_get_erc20_total_supply_by_block(
    token: spec.ERC20Reference,
    blocks: typing.Sequence[spec.BlockNumberReference],
    *,
    normalize: bool = True,
    context: spec.Context = None,
    **rpc_kwargs: typing.Any,
) -> typing.Union[typing.Sequence[int], typing.Sequence[float]]:
    """get historical total supply of ERC20 across multiple blocks"""

    total_supplies = await erc20_generic.async_erc20_eth_call_by_block(
        token=token,
        function_name='totalSupply',
        blocks=blocks,
        context=context,
        **rpc_kwargs,
    )

    if normalize:
        total_supplies = (
            await erc20_normalize.async_normalize_erc20_quantities_by_block(
                token=token,
                quantities=total_supplies,
                context=context,
                blocks=blocks,
            )
        )

    return total_supplies


#
# # balance of
#


async def async_get_erc20_balance(
    wallet: spec.Address,
    token: spec.ERC20Address,
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    normalize: bool = True,
    context: spec.Context = None,
    **rpc_kwargs: typing.Any,
) -> typing.Union[int, float] | None:
    """get ERC20 balance"""

    if block is None:
        block = 'latest'

    wallet = await address_utils.async_resolve_address(
        wallet,
        block=block,
        context=context,
    )

    result = await erc20_generic.async_erc20_eth_call(
        token=token,
        function_name='balanceOf',
        block=block,
        function_parameters=[wallet],
        context=context,
        **rpc_kwargs,
    )
    if result is None:
        if not rpc_kwargs.get('convert_reverts_to_none'):
            raise Exception('invalid result')
        return result
    balance: int | float = result

    if normalize:
        balance = await erc20_normalize.async_normalize_erc20_quantity(
            quantity=balance, token=token, context=context, block=block
        )

    return balance


async def async_get_erc20_balances_of_addresses(
    wallets: typing.Sequence[spec.Address],
    token: spec.ERC20Address,
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    normalize: bool = True,
    context: spec.Context = None,
    **rpc_kwargs: typing.Any,
) -> typing.Union[typing.Sequence[int], typing.Sequence[float]]:
    """get ERC20 balance of multiple addresses"""

    from ctc import rpc

    if block is None:
        block = 'latest'

    wallets = await address_utils.async_resolve_addresses(
        wallets,
        block=block,
        context=context,
    )

    balances = await rpc.async_batch_eth_call(
        to_address=token,
        block_number=block,
        function_abi=erc20_spec.erc20_function_abis['balanceOf'],
        function_parameter_list=[[wallet] for wallet in wallets],
        context=context,
        **rpc_kwargs,
    )

    if normalize:
        return await erc20_normalize.async_normalize_erc20_quantities(
            quantities=balances, token=token, context=context, block=block
        )
    else:
        return balances


async def async_get_erc20s_balances(
    wallet: spec.Address,
    tokens: typing.Sequence[spec.ERC20Address],
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    normalize: bool = True,
    context: spec.Context = None,
    **rpc_kwargs: typing.Any,
) -> typing.Union[typing.Sequence[int], typing.Sequence[float]]:
    """get ERC20 balance of wallet for multiple tokens"""

    from ctc import config

    if block is None:
        block = 'latest'

    wallet = await address_utils.async_resolve_address(
        wallet,
        block=block,
        context=context,
    )

    context = config.update_context(
        context=context,
        merge_provider={'chunk_size': 100},
    )
    balances = await erc20_generic.async_erc20s_eth_calls(
        tokens=tokens,
        function_name='balanceOf',
        block=block,
        function_parameters=[wallet],
        context=context,
        **rpc_kwargs,
    )

    if normalize:
        balances = await erc20_normalize.async_normalize_erc20s_quantities(
            quantities=balances,
            tokens=tokens,
            context=context,
            block=block,
        )

    return balances


async def async_get_erc20_balance_by_block(
    wallet: spec.Address,
    token: spec.ERC20Reference,
    *,
    blocks: typing.Sequence[spec.BlockNumberReference],
    normalize: bool = True,
    context: spec.Context = None,
    empty_token: typing.Any = 0,
    **rpc_kwargs: typing.Any,
) -> typing.Union[typing.Sequence[int], typing.Sequence[float]]:
    """get historical ERC20 balance over multiple blocks"""

    wallet = await address_utils.async_resolve_address(
        wallet,
        block=blocks[-1],
        context=context,
    )

    balances = await erc20_generic.async_erc20_eth_call_by_block(
        token=token,
        function_name='balanceOf',
        blocks=blocks,
        function_parameters=[wallet],
        context=context,
        empty_token=empty_token,
        **rpc_kwargs,
    )

    if normalize:
        balances = (
            await erc20_normalize.async_normalize_erc20_quantities_by_block(
                quantities=balances,
                token=token,
                context=context,
                blocks=blocks,
            )
        )

    return balances


#
# # allowance
#


async def async_get_erc20_allowance(
    token: spec.ERC20Reference,
    owner: spec.Address,
    *,
    spender: spec.Address,
    block: spec.BlockNumberReference | None = None,
    normalize: bool = True,
    context: spec.Context = None,
    **rpc_kwargs: typing.Any,
) -> typing.Union[int, float] | None:
    """get ERC20 allowance"""

    if block is None:
        block = 'latest'

    owner = await address_utils.async_resolve_address(
        owner,
        block=block,
        context=context,
    )

    result = await erc20_generic.async_erc20_eth_call(
        token=token,
        function_name='allowance',
        block=block,
        function_parameters=[owner, spender],
        context=context,
        **rpc_kwargs,
    )
    if result is None:
        if not rpc_kwargs.get('convert_reverts_to_none'):
            raise Exception('invalid result')
        return result

    allowance: int | float = result

    if normalize:
        allowance = await erc20_normalize.async_normalize_erc20_quantity(
            quantity=allowance, token=token, context=context, block=block
        )

    return allowance


async def async_get_erc20_allowance_by_block(
    token: spec.ERC20Reference,
    owner: spec.Address,
    *,
    spender: spec.Address,
    blocks: typing.Sequence[spec.BlockNumberReference],
    normalize: bool = True,
    context: spec.Context = None,
    **rpc_kwargs: typing.Any,
) -> typing.Union[typing.Sequence[int], typing.Sequence[float]]:
    """get historical ERC20 allowance over range of blocks"""

    owner = await address_utils.async_resolve_address(
        owner,
        block=blocks[-1],
        context=context,
    )

    allowances = await erc20_generic.async_erc20_eth_call_by_block(
        token=token,
        function_name='allowance',
        blocks=blocks,
        function_parameters=[owner, spender],
        context=context,
        **rpc_kwargs,
    )

    if normalize:
        allowances = (
            await erc20_normalize.async_normalize_erc20_quantities_by_block(
                quantities=allowances,
                token=token,
                context=context,
                blocks=blocks,
            )
        )

    return allowances


async def async_get_erc20s_allowances(
    tokens: typing.Sequence[spec.ERC20Reference],
    owner: spec.Address,
    *,
    spender: spec.Address,
    block: spec.BlockNumberReference | None = None,
    normalize: bool = True,
    context: spec.Context = None,
    **rpc_kwargs: typing.Any,
) -> typing.Union[typing.Sequence[int], typing.Sequence[float]]:
    """get ERC20 allowance of wallet for multiple tokens"""

    owner = await address_utils.async_resolve_address(
        owner,
        block=block,
        context=context,
    )

    allowances = await erc20_generic.async_erc20s_eth_calls(
        tokens=tokens,
        function_name='allowance',
        block=block,
        function_parameters=[owner, spender],
        context=context,
        **rpc_kwargs,
    )

    if normalize:
        allowances = await erc20_normalize.async_normalize_erc20s_quantities(
            quantities=allowances, tokens=tokens, context=context, block=block
        )

    return allowances


async def async_get_erc20_allowances_of_owners(
    token: spec.ERC20Reference,
    owners: typing.Sequence[spec.Address],
    *,
    spender: spec.Address,
    block: spec.BlockNumberReference | None = None,
    normalize: bool = True,
    context: spec.Context = None,
    **rpc_kwargs: typing.Any,
) -> typing.Sequence[int | float]:
    """get ERC20 allowance of multiple owners"""

    from ctc import rpc

    owners = await address_utils.async_resolve_addresses(
        owners,
        block=block,
        context=context,
    )

    allowances = await rpc.async_batch_eth_call(
        to_address=token,
        block_number=block,
        function_abi=erc20_spec.erc20_function_abis['allowance'],
        function_parameter_list=[[owner, spender] for owner in owners],
        context=context,
        **rpc_kwargs,
    )

    if normalize:
        return await erc20_normalize.async_normalize_erc20_quantities(
            quantities=allowances, token=token, context=context, block=block
        )
    else:
        return allowances


async def async_get_erc20_allowances_of_spenders(
    token: spec.ERC20Reference,
    owner: spec.Address,
    *,
    spenders: typing.Sequence[spec.Address],
    block: spec.BlockNumberReference | None = None,
    normalize: bool = True,
    context: spec.Context = None,
    **rpc_kwargs: typing.Any,
) -> typing.Sequence[int | float]:
    """get ERC20 allowance of multiple spenders"""

    from ctc import rpc

    owner = await address_utils.async_resolve_address(
        owner,
        block=block,
        context=context,
    )

    allowances = await rpc.async_batch_eth_call(
        to_address=token,
        block_number=block,
        function_abi=erc20_spec.erc20_function_abis['allowance'],
        function_parameter_list=[[owner, spender] for spender in spenders],
        context=context,
        **rpc_kwargs,
    )

    if normalize:
        return await erc20_normalize.async_normalize_erc20_quantities(
            quantities=allowances, token=token, context=context, block=block
        )
    else:
        return allowances

