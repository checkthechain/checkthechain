import asyncio

from ctc import rpc

from .. import rari_abis
from . import directory_metadata
from . import token_metadata


async def async_get_pool_ctoken(comptroller, underlying, block='latest'):
    return await rpc.async_eth_call(
        to_address=comptroller,
        block_number=block,
        function_abi=rari_abis.comptroller_abis['cTokensByUnderlying'],
        function_parameters=[underlying],
    )


async def async_get_pool_ctokens(comptroller, block='latest'):
    return await rpc.async_eth_call(
        to_address=comptroller,
        block_number=block,
        function_abi=rari_abis.comptroller_abis['getAllMarkets'],
    )


async def async_get_pool_underlying_tokens(
    *, ctokens=None, comptroller=None, block='latest'
):
    if ctokens is None:
        if comptroller is None:
            raise Exception('specify comptroller')
        ctokens = await async_get_pool_ctokens(comptroller, block=block)

    coroutines = [
        token_metadata.async_get_ctoken_underlying(ctoken=ctoken)
        for ctoken in ctokens
    ]
    underlyings = await asyncio.gather(*coroutines)
    return dict(zip(ctokens, underlyings))


async def async_get_pool_oracle(comptroller, block='latest'):
    return await rpc.async_eth_call(
        to_address=comptroller,
        block_number=block,
        function_abi=rari_abis.comptroller_abis['oracle'],
    )


async def async_get_pool_name(comptroller, all_pools=None, block='latest'):
    comptroller = comptroller.lower()
    if all_pools is None:
        all_pools = await directory_metadata.async_get_all_pools(block=block)
    for pool in all_pools:
        if pool[2] == comptroller:
            return pool[0]
    else:
        raise Exception('could not find pool')

