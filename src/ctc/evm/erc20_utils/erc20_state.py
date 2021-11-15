from .. import rpc_utils
from . import erc20_metadata


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

