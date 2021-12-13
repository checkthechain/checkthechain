import asyncio
import typing

from ctc import evm
from ctc import spec
from ctc import rpc
from . import coracle_spec


#
# # oracle getters
#


async def async_get_token_oracle(
    token: spec.TokenAddress,
    block: spec.BlockNumberReference = 'latest',
    provider: spec.ProviderSpec = None,
) -> spec.ContractAddress:
    return await rpc.async_eth_call(
        to_address=coracle_spec.get_coracle_address(block=block),
        function_name='tokenToOracle',
        function_parameters=[token],
        block_number=block,
        provider=provider,
    )


async def async_get_token_oracle_by_block(
    token: spec.TokenAddress,
    blocks: typing.Sequence[spec.BlockNumberReference],
    provider: spec.ProviderSpec = None,
) -> list[spec.ContractAddress]:

    coroutines = []
    for block in blocks:
        coroutine = async_get_token_oracle(
            token=token,
            block=block,
            provider=provider,
        )
        coroutines.append(coroutine)
    return await asyncio.gather(*coroutines)


async def async_get_tokens_oracles(
    tokens: typing.Sequence[spec.TokenAddress],
    block: spec.BlockNumberReference = 'latest',
    provider: spec.ProviderSpec = None,
) -> list[spec.ContractAddress]:

    block = await evm.async_block_number_to_int(block, provider=provider)
    return await rpc.async_batch_eth_call(
        to_address=coracle_spec.get_coracle_address(block=block),
        function_name='tokenToOracle',
        function_parameter_list=[[token] for token in tokens],
        block_number=block,
        provider=provider,
    )


#
# # price getters
#


async def async_get_token_price(
    token: spec.TokenAddress,
    block: spec.BlockReference = 'latest',
    provider: spec.ProviderSpec = None,
    normalize: bool = True,
) -> typing.Union[int, float]:

    # get oracle
    block = await evm.async_block_number_to_int(block, provider=provider)
    oracle = await async_get_token_oracle(
        token=token, block=block, provider=provider
    )

    # get price
    result = await rpc.async_eth_call(
        to_address=oracle,
        function_name='read',
        block_number=block,
        provider=provider,
    )
    price = result[0][0]

    if normalize:
        price /= 1e18

    return price


async def async_get_token_price_by_block(
    token: spec.TokenAddress,
    blocks: typing.Sequence[spec.BlockNumberReference],
    provider: spec.ProviderSpec = None,
    normalize: bool = True,
) -> typing.Union[list[int], list[float]]:

    # need to use c
    coroutines = []
    for block in blocks:
        coroutine = async_get_token_price(
            token=token,
            block=block,
            provider=provider,
            normalize=normalize,
        )
        coroutines.append(coroutine)
    return await asyncio.gather(*coroutines)


async def async_get_tokens_prices(
    tokens: typing.Sequence[spec.TokenAddress],
    block: spec.BlockReference = 'latest',
    provider: spec.ProviderSpec = None,
    normalize: bool = True,
) -> typing.Union[list[int], list[float]]:

    block = await evm.async_block_number_to_int(block, provider=provider)
    oracles = await async_get_tokens_oracles(
        tokens=tokens,
        block=block,
        provider=provider,
    )
    results = await rpc.async_batch_eth_call(
        to_addresses=oracles,
        function_name='read',
        block_number=block,
        provider=provider,
    )
    prices = [result[0][0] for result in results]

    if normalize:
        prices = [price / 1e18 for price in prices]

    return prices

