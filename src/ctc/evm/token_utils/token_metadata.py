import web3

from ctc import directory
from .. import address_utils
from .. import block_utils
from . import token_calls


#
# # token metadata functions
#


def get_token_address(token):

    if address_utils.is_address_str(token):
        token_address = token
    elif isinstance(token, str):
        token_address = directory.token_addresses[token]
    else:
        raise Exception('could not get token address')

    token_address = web3.Web3.toChecksumAddress(token_address)

    return token_address


#
# # erc20 token functions
#

@block_utils.parallelize_block_fetching()
def fetch_token_decimals(
    token=None, block=None, contract=None, **contract_kwargs
):
    return token_calls.token_contract_call(
        function='decimals',
        token=token,
        contract=contract,
        block=block,
        **contract_kwargs
    )


@block_utils.parallelize_block_fetching()
def fetch_token_name(token=None, block=None, contract=None, **contract_kwargs):
    return token_calls.token_contract_call(
        function='name',
        token=token,
        contract=contract,
        block=block,
        **contract_kwargs
    )


@block_utils.parallelize_block_fetching()
def fetch_token_symbol(
    token=None, contract=None, block=None, **contract_kwargs
):
    return token_calls.token_contract_call(
        function='symbol',
        token=token,
        contract=contract,
        block=block,
        **contract_kwargs
    )

