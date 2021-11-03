from .. import block_utils
from .. import rpc_utils
from . import erc20_metadata


@block_utils.parallelize_block_fetching()
def fetch_token_total_supply(
    token, block=None, normalize=True, **contract_kwargs
):
    contract_address = erc20_metadata.get_token_address(token)

    total_supply = rpc_utils.eth_call(
        to_address=contract_address,
        function_name='totalSupply',
        block=block,
        **contract_kwargs
    )

    if normalize:
        token_n_decimals = erc20_metadata.fetch_token_decimals(contract_address)
        total_supply = total_supply / (10 ** token_n_decimals)

    return total_supply


@block_utils.parallelize_block_fetching()
def fetch_token_balance_of(
    address,
    token=None,
    block=None,
    normalize=True,
    **eth_call_kwargs
):

    contract_address = erc20_metadata.get_token_address(token)
    token_balance = rpc_utils.eth_call(
        to_address=contract_address,
        function_name='balanceOf',
        block=block,
        function_parameters=[address],
        **eth_call_kwargs
    )

    if normalize:
        token_n_decimals = erc20_metadata.fetch_token_decimals(contract_address)
        token_balance = token_balance / (10 ** token_n_decimals)

    return token_balance

