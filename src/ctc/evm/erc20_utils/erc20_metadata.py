import typing

from ctc import directory
from ctc import rpc
from ctc import spec
from .. import address_utils
from .. import block_utils
from .. import rpc_utils


#
# # token metadata functions
#


def get_erc20_address(token):
    if address_utils.is_address_str(token):
        return token
    elif isinstance(token, str):
        return directory.token_addresses[token]
    else:
        raise Exception('could not get token address')


#
# # async queries
#


async def async_erc20_eth_call(
    function_name: str,
    token: typing.Optional[spec.TokenReference] = None,
    tokens: typing.Optional[list[spec.TokenReference]] = None,
    block: typing.Optional[int] = None,
    blocks: typing.Optional[int] = None,
    **rpc_kwargs
):
    if tokens is not None and blocks is not None:
        raise NotImplementedError('specify one batch parameter at a time')

    if blocks is not None:
        return await rpc.async_batch_eth_call(
            to_addresses=get_erc20_address(token),
            function_name=function_name,
            block_numbers=blocks,
            **rpc_kwargs
        )

    elif tokens is not None:
        return await rpc.async_batch_eth_call(
            to_addresses=[get_erc20_address(token) for token in tokens],
            function_name=function_name,
            block_number=block,
            **rpc_kwargs
        )

    elif token is not None:
        return await rpc.async_eth_call(
            to_address=get_erc20_address(token),
            function_name=function_name,
            block_number=block,
            **rpc_kwargs
        )

    else:
        raise Exception('could not process inputs')


async def async_get_erc20_decimals(
    token=None, *, tokens=None, block=None, blocks=None, **rpc_kwargs
):
    return await async_erc20_eth_call(
        function_name='decimals',
        token=token,
        tokens=tokens,
        block=block,
        blocks=blocks,
        **rpc_kwargs
    )


async def async_get_erc20_name(
    token=None, *, tokens=None, block=None, blocks=None, **rpc_kwargs
):
    return await async_erc20_eth_call(
        function_name='name',
        token=token,
        tokens=tokens,
        block=block,
        blocks=blocks,
        **rpc_kwargs
    )


async def async_get_erc20_symbol(
    token=None, *, tokens=None, block=None, blocks=None, **rpc_kwargs
):
    return await async_erc20_eth_call(
        function_name='symbol',
        token=token,
        tokens=tokens,
        block=block,
        blocks=blocks,
        **rpc_kwargs
    )


#
# # old sync versions
#


@block_utils.parallelize_block_fetching()
def get_erc20_decimals(token=None, block=None, **eth_call_kwargs):
    return rpc_utils.eth_call(
        to_address=get_erc20_address(token),
        function_name='decimals',
        block_number=block,
        **eth_call_kwargs
    )


@block_utils.parallelize_block_fetching()
def get_erc20_name(token=None, block=None, **eth_call_kwargs):
    return rpc_utils.eth_call(
        to_address=get_erc20_address(token),
        function_name='name',
        block_number=block,
        **eth_call_kwargs
    )


@block_utils.parallelize_block_fetching()
def get_erc20_symbol(token=None, block=None, **eth_call_kwargs):
    return rpc_utils.eth_call(
        to_address=get_erc20_address(token),
        function_name='symbol',
        block_number=block,
        **eth_call_kwargs
    )

