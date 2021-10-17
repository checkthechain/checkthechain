import web3

from ctc import directory
from .. import block_utils
from . import token_calls
from . import token_metadata


@block_utils.parallelize_block_fetching()
def fetch_token_total_supply(
    token, block=None, contract=None, normalize=True, **contract_kwargs
):

    try:
        total_supply = token_calls.token_contract_call(
            function='totalSupply',
            token=token,
            contract=contract,
            block=block,
            **contract_kwargs
        )
    except web3.contract.BadFunctionCallOutput:
        # hack for nonexistent tokens/contracts
        return 0

    if normalize:
        token_n_decimals = directory.get_token_n_decimals(token)
        total_supply = total_supply / (10 ** token_n_decimals)

    return total_supply


@block_utils.parallelize_block_fetching()
def fetch_token_balance_of(
    address,
    token=None,
    block=None,
    contract=None,
    normalize=True,
    **contract_kwargs
):

    try:
        token_balance = token_calls.token_contract_call(
            function='balanceOf',
            token=token,
            contract=contract,
            block=block,
            args=[web3.Web3.toChecksumAddress(address)],
            **contract_kwargs
        )
    except web3.contract.BadFunctionCallOutput:
        # hack for nonexistent tokens/contracts
        return 0

    if normalize:
        if token is not None:
            token_n_decimals = directory.get_token_n_decimals(token)
        else:
            token_n_decimals = token_metadata.fetch_token_decimals(contract=contract)
        token_balance = token_balance / (10 ** token_n_decimals)

    return token_balance

