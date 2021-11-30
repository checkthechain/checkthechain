import typing

from ctc import spec
from ctc import rpc
from .. import rpc_utils
from . import erc20_metadata


T = typing.TypeVar('T')


async def async_normalize_erc20_quantity(
    quantity: T,
    token: spec.TokenReference = None,
    tokens: list[spec.TokenReference] = None,
) -> T:

    # TODO: work on pd.Series objects
    # TODO: return same type as input

    if token is None and tokens is None:
        raise Exception('specify token or tokens')

    if isinstance(quantity, typing.SupportsFloat):
        n_decimals = erc20_metadata.get_erc20_decimals(token)
        quantity = quantity / (10 ** n_decimals)
    else:
        n_decimals = erc20_metadata.get_erc20_decimals(token)
        quantity = [item / (10 ** n_decimals) for item in quantity]

    return quantity


async def async_get_erc20_total_supply(
    token: spec.TokenReference,
    block: typing.Optional[int] = None,
    blocks: typing.Optional[list[int]] = None,
    normalize: bool = True,
    **rpc_kwargs
) -> typing.SupportsFloat:

    contract_address = erc20_metadata.get_erc20_address(token)

    if blocks is None:
        total_supply = await rpc.async_eth_call(
            to_address=contract_address,
            function_name='totalSupply',
            block_number=block,
            **rpc_kwargs
        )
    else:
        total_supply = await rpc.async_batch_eth_call(
            to_address=contract_address,
            function_name='totalSupply',
            block_numbers=blocks,
            **rpc_kwargs
        )

    if normalize:
        total_supply = await async_normalize_erc20_quantity(
            token=contract_address,
            quantity=total_supply,
        )

    return total_supply


async def async_get_erc20_balance_of(
    *,
    address=None,
    addresses=None,
    token=None,
    tokens=None,
    block=None,
    blocks=None,
    normalize=True,
    **rpc_kwargs
):
    if address is None and addresses is None:
        raise Exception('specify address or addresses')
    if token is None and tokens is None:
        raise Exception('specify token or tokens')
    if [addresses, tokens, blocks].count(None) < 2:
        raise NotImplementedError('specify only one batch parameter at once')

    if addresses is None and blocks is None and tokens is None:
        balance = await rpc.async_eth_call(
            to_address=erc20_metadata.get_erc20_address(token),
            function_name='balanceOf',
            block_number=block,
            function_parameters=[address],
            **rpc_kwargs
        )

    elif blocks is not None:
        balance = await rpc.async_batch_eth_call(
            to_address=erc20_metadata.get_erc20_address(token),
            function_name='balanceOf',
            block_numbers=blocks,
            function_parameters=[address],
            **rpc_kwargs
        )

    elif addresses is not None:
        balance = await rpc.async_batch_eth_call(
            to_address=erc20_metadata.get_erc20_address(token),
            function_name='balanceOf',
            block_numbers=blocks,
            function_parameter_list=[[address] for address in addresses],
            **rpc_kwargs
        )

    elif tokens is not None:
        to_addresses = [
            erc20_metadata.get_erc20_address(token) for token in tokens
        ]
        balance = await rpc.async_batch_eth_call(
            to_addresses=to_addresses,
            function_name='balanceOf',
            block_numbers=blocks,
            function_parameters=[address],
            **rpc_kwargs
        )

    else:
        raise Exception('must specify block or blocks')

    if normalize:
        balance = await async_normalize_erc20_quantity(
            token=token,
            tokens=tokens,
            quantity=balance,
        )

    return balance


#
# # old sync functions
#


def get_erc20_total_supply(
    token, block=None, blocks=None, normalize=True, **contract_kwargs
):
    contract_address = erc20_metadata.get_erc20_address(token)

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

    contract_address = erc20_metadata.get_erc20_address(token)

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

