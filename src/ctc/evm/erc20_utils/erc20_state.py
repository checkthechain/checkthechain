import typing

from ctc import spec
from ctc import rpc
from .. import rpc_utils
from . import erc20_metadata
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
    **rpc_kwargs
) -> typing.Union[int, float]:
    """"""

    total_supply = await erc20_generic.async_erc20_eth_call(
        token=token,
        function_name='totalSupply',
        block=block,
        provider=provider,
        **rpc_kwargs
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
    **rpc_kwargs
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
    **rpc_kwargs
) -> typing.Union[list[int], list[float]]:

    total_supplies = await erc20_generic.async_erc20_eth_call_by_block(
        token=token,
        function_name='totalSupply',
        blocks=blocks,
        provider=provider,
        **rpc_kwargs
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
) -> typing.Union[int, float]:

    balance = await erc20_generic.async_erc20_eth_call(
        token=token,
        function_name='balanceOf',
        block=block,
        function_parameters=[address],
        provider=provider,
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
) -> typing.Union[list[int], list[float]]:

    balances = await rpc.async_batch_eth_call(
        to_address=token,
        function_name='balanceOf',
        block_number=block,
        function_parameter_list=[[address] for address in addresses],
        provider=provider,
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
) -> typing.Union[list[int], list[float]]:
    """"""

    balances = await erc20_generic.async_erc20s_eth_calls(
        tokens=tokens,
        function_name='balanceOf',
        block=block,
        function_parameters=[address],
        provider=provider,
    )

    if normalize:
        balances = await erc20_normalize.async_normalize_erc20s_quantities(
            quantities=balances, tokens=tokens, provider=provider, block=block
        )

    return balances


async def async_get_erc20_balance_of_by_block(
    address: spec.Address,
    token: spec.ERC20Reference,
    blocks: typing.Sequence[spec.BlockNumberReference],
    normalize=True,
    provider: spec.ProviderSpec = None,
) -> typing.Union[list[int], list[float]]:
    """"""

    balances = await erc20_generic.async_erc20_eth_call_by_block(
        token=token,
        function_name='balanceOf',
        blocks=blocks,
        function_parameters=[address],
        provider=provider,
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
        function_name='allowance',
        block_number=block,
        function_parameter_list=[[address] for address in addresses],
        provider=provider,
    )

    if normalize:
        allowances = await erc20_normalize.async_normalize_erc20_quantities(
            quantities=allowances, token=token, provider=provider, block=block
        )

    return allowances


#
# # old sync functions
#


def get_erc20_total_supply(
    token, block=None, blocks=None, normalize=True, **contract_kwargs
):
    contract_address = erc20_generic.get_erc20_address(token)

    if block is not None or (block is None and blocks is None):
        total_supply = rpc_utils.eth_call(
            to_address=contract_address,
            function_name='totalSupply',
            block_number=block,
            **contract_kwargs
        )

        if normalize:
            n_decimals = erc20_metadata.get_erc20_decimals(contract_address)
            total_supply = total_supply / (10 ** n_decimals)

        return total_supply

    elif blocks is not None:
        total_supply = rpc_utils.batch_eth_call(
            to_address=contract_address,
            function_name='totalSupply',
            block_numbers=blocks,
            **contract_kwargs
        )

        if normalize:
            n_decimals = erc20_metadata.get_erc20_decimals(contract_address)
            total_supply = [item / (10 ** n_decimals) for item in total_supply]

        return total_supply

    else:
        raise Exception('must specify block or blocks')


def get_erc20_balance_of(
    address,
    token=None,
    block=None,
    blocks=None,
    normalize=True,
    **eth_call_kwargs
):

    contract_address = erc20_generic.get_erc20_address(token)

    if block is not None or (block is None and blocks is None):
        balance = rpc_utils.eth_call(
            to_address=contract_address,
            function_name='balanceOf',
            block_number=block,
            function_parameters=[address],
            **eth_call_kwargs
        )

        if normalize:
            n_decimals = erc20_metadata.get_erc20_decimals(contract_address)
            balance = balance / (10 ** n_decimals)

        return balance

    elif blocks is not None:
        balance = rpc_utils.batch_eth_call(
            to_address=contract_address,
            function_name='balanceOf',
            block_numbers=blocks,
            function_parameters=[address],
            **eth_call_kwargs
        )

        if normalize:
            n_decimals = erc20_metadata.get_erc20_decimals(contract_address)
            balance = [entry / (10 ** n_decimals) for entry in balance]

        return balance

    else:
        raise Exception('must specify block or blocks')

