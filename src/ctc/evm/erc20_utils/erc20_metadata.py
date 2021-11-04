from ctc import directory
from .. import address_utils
from .. import block_utils
from .. import rpc_utils


#
# # token metadata functions
#


def get_token_address(token):
    if address_utils.is_address_str(token):
        return token
    elif isinstance(token, str):
        return directory.token_addresses[token]
    else:
        raise Exception('could not get token address')


#
# # erc20 token functions
#


@block_utils.parallelize_block_fetching()
def fetch_token_decimals(token=None, block=None, **eth_call_kwargs):
    return rpc_utils.eth_call(
        to_address=get_token_address(token),
        function_name='decimals',
        block_number=block,
        **eth_call_kwargs
    )


@block_utils.parallelize_block_fetching()
def fetch_token_name(token=None, block=None, **eth_call_kwargs):
    return rpc_utils.eth_call(
        to_address=get_token_address(token),
        function_name='name',
        block_number=block,
        **eth_call_kwargs
    )


@block_utils.parallelize_block_fetching()
def fetch_token_symbol(token=None, block=None, **eth_call_kwargs):
    return rpc_utils.eth_call(
        to_address=get_token_address(token),
        function_name='symbol',
        block_number=block,
        **eth_call_kwargs
    )

