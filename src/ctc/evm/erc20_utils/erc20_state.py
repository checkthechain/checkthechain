from .. import rpc_utils
from . import erc20_metadata


def fetch_token_total_supply(
    token, block=None, blocks=None, normalize=True, **contract_kwargs
):
    contract_address = erc20_metadata.get_token_address(token)

    if block is None and blocks is None:
        block = 'latest'

    total_supply = rpc_utils.eth_call(
        to_address=contract_address,
        function_name='totalSupply',
        block_number=block,
        block_numbers=blocks,
        **contract_kwargs
    )

    if normalize:
        token_n_decimals = erc20_metadata.fetch_token_decimals(contract_address)

        if block is not None:
            total_supply = total_supply / (10 ** token_n_decimals)
        elif blocks is not None:
            total_supply = [
                item / (10 ** token_n_decimals)
                for item in total_supply
            ]
        else:
            raise Exception()

    return total_supply


def fetch_token_balance_of(
    address,
    token=None,
    block=None,
    blocks=None,
    normalize=True,
    **eth_call_kwargs
):

    contract_address = erc20_metadata.get_token_address(token)
    token_balance = rpc_utils.eth_call(
        to_address=contract_address,
        function_name='balanceOf',
        block_number=block,
        block_numbers=blocks,
        function_parameters=[address],
        **eth_call_kwargs
    )

    if normalize:
        token_n_decimals = erc20_metadata.fetch_token_decimals(contract_address)
        token_balance = token_balance / (10 ** token_n_decimals)

    return token_balance

