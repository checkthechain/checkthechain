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
    token: spec.TokenReference,
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
    tokens: typing.Sequence[spec.TokenReference],
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
        total_supplies = await erc20_normalize.async_normalize_erc20_quantities(
            tokens=tokens, quantities=total_supplies, provider=provider
        )

    return total_supplies


async def async_get_erc20_total_supply_by_block(
    token: spec.TokenReference,
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
        total_supplies = await erc20_normalize.async_normalize_erc20_quantities(
            token=token, quantities=total_supplies, provider=provider
        )

    return total_supplies


#
# # balance of
#


async def async_get_erc20_balance_of(
    address: spec.Address,
    token: spec.TokenAddress,
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
        balance = erc20_normalize.async_normalize_erc20_quantity(
            quantity=balance, token=token, provider=provider, block=block
        )

    return balance


async def async_get_erc20_balance_of_addresses(
    addresses: typing.Sequence[spec.Address],
    token: spec.TokenAddress,
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
    tokens: typing.Sequence[spec.TokenAddress],
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
        balances = await erc20_normalize.async_normalize_erc20_quantities(
            quantities=balances, tokens=tokens, provider=provider, block=block
        )

    return balances


async def async_get_erc20_balance_of_by_block(
    address: spec.Address,
    token: spec.TokenReference,
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
        balances = await erc20_normalize.async_normalize_erc20_quantities(
            quantities=balances, token=token, provider=provider, blocks=blocks
        )

    return balances


# async def async_get_erc20_balance_of(
#     *,
#     address=None,
#     addresses=None,
#     token=None,
#     tokens=None,
#     block=None,
#     blocks=None,
#     normalize=True,
#     **rpc_kwargs
# ):

#     if address is None and addresses is None:
#         raise Exception('specify address or addresses')
#     if token is None and tokens is None:
#         raise Exception('specify token or tokens')
#     if [addresses, tokens, blocks].count(None) < 2:
#         raise NotImplementedError('specify only one batch parameter at once')

#     if addresses is None and blocks is None and tokens is None:
#         balance = await rpc.async_eth_call(
#             to_address=erc20_metadata.get_erc20_address(token),
#             function_name='balanceOf',
#             block_number=block,
#             function_parameters=[address],
#             **rpc_kwargs
#         )

#     elif blocks is not None:
#         balance = await rpc.async_batch_eth_call(
#             to_address=erc20_metadata.get_erc20_address(token),
#             function_name='balanceOf',
#             block_numbers=blocks,
#             function_parameters=[address],
#             **rpc_kwargs
#         )

#     elif addresses is not None:
#         balance = await rpc.async_batch_eth_call(
#             to_address=erc20_metadata.get_erc20_address(token),
#             function_name='balanceOf',
#             block_numbers=blocks,
#             function_parameter_list=[[address] for address in addresses],
#             **rpc_kwargs
#         )

#     elif tokens is not None:
#         to_addresses = [
#             erc20_metadata.get_erc20_address(token) for token in tokens
#         ]
#         balance = await rpc.async_batch_eth_call(
#             to_addresses=to_addresses,
#             function_name='balanceOf',
#             block_numbers=blocks,
#             function_parameters=[address],
#             **rpc_kwargs
#         )

#     else:
#         raise Exception('must specify block or blocks')

#     if normalize:
#         balance = await async_normalize_erc20_quantity(
#             token=token,
#             tokens=tokens,
#             quantity=balance,
#         )

#     return balance


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

