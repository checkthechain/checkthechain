from __future__ import annotations

import typing

from ctc import evm
from ctc import spec
from ctc import rpc
from . import coracle_spec


#
# # oracle getters
#


async def async_get_token_oracle(
    token: spec.Address,
    *,
    block: spec.BlockNumberReference = 'latest',
    context: spec.Context = None,
    replace_missing: bool = True,
    raise_if_missing: bool = True,
) -> spec.ContractAddress:

    coracle = coracle_spec.get_coracle_address(block=block)
    oracle = await rpc.async_eth_call(
        to_address=coracle,
        function_name='tokenToOracle',
        function_parameters=[token],
        block_number=block,
        context=context,
    )
    if not isinstance(oracle, str):
        raise Exception('invalid rpc result')

    if replace_missing:
        oracle = await _async_replace_missing_oracle(
            token=token,
            oracle=oracle,
            context=context,
            replacement_block='latest',
        )

    if raise_if_missing:
        _ensure_oracle_valid(oracle=oracle, token=token, block=block)

    return oracle


async def async_get_tokens_oracles(
    tokens: typing.Sequence[spec.Address],
    *,
    block: spec.BlockNumberReference = 'latest',
    context: spec.Context = None,
    replace_missing: bool = True,
    raise_if_missing: bool = True,
) -> list[spec.ContractAddress]:

    block = await evm.async_block_number_to_int(block, context=context)
    oracles: typing.Sequence[
        spec.ContractAddress
    ] = await rpc.async_batch_eth_call(
        to_address=coracle_spec.get_coracle_address(block=block),
        function_name='tokenToOracle',
        function_parameter_list=[[token] for token in tokens],
        block_number=block,
        context=context,
    )

    if replace_missing:
        oracles = await _async_replace_missing_oracles(
            oracles=oracles,
            tokens=tokens,
            context=context,
            replacement_block=block,
        )

    if raise_if_missing:
        for oracle, token in zip(oracles, tokens):
            _ensure_oracle_valid(oracle=oracle, token=token, block=block)

    return list(oracles)


async def async_get_token_oracle_by_block(
    token: spec.Address,
    *,
    blocks: typing.Sequence[spec.BlockNumberReference],
    context: spec.Context = None,
) -> list[spec.ContractAddress]:

    import asyncio

    coroutines = []
    for block in blocks:
        coroutine = async_get_token_oracle(
            token=token,
            block=block,
            context=context,
        )
        coroutines.append(coroutine)
    return await asyncio.gather(*coroutines)


#
# # price getters
#


async def async_get_token_price(
    token: spec.Address,
    *,
    block: spec.BlockReference = 'latest',
    context: spec.Context = None,
    normalize: bool = True,
) -> typing.Union[int, float]:

    # get oracle
    block = await evm.async_block_number_to_int(block, context=context)
    oracle = await async_get_token_oracle(
        token=token, block=block, context=context
    )

    # get price
    result = await rpc.async_eth_call(
        to_address=oracle,
        function_name='read',
        block_number=block,
        context=context,
    )
    subresult = result[0][0]
    if not isinstance(subresult, int):
        raise Exception('invalid rpc result')
    price: int | float = subresult

    if normalize:
        price /= 1e18

    return price


async def async_get_token_price_by_block(
    token: spec.Address,
    *,
    blocks: typing.Sequence[spec.BlockNumberReference],
    context: spec.Context = None,
    normalize: bool = True,
) -> typing.Union[list[int], list[float]]:
    import asyncio

    # need to use c
    coroutines = []
    for block in blocks:
        coroutine = async_get_token_price(
            token=token,
            block=block,
            context=context,
            normalize=normalize,
        )
        coroutines.append(coroutine)
    return await asyncio.gather(*coroutines)


async def async_get_tokens_prices(
    tokens: typing.Sequence[spec.Address],
    *,
    block: typing.Optional[spec.BlockReference] = None,
    context: spec.Context = None,
    normalize: bool = True,
) -> typing.Union[list[int], list[float]]:

    if block is None:
        block = 'latest'

    block = await evm.async_block_number_to_int(block, context=context)
    oracles = await async_get_tokens_oracles(
        tokens=tokens,
        block=block,
        context=context,
    )
    results = await rpc.async_batch_eth_call(
        to_addresses=oracles,
        function_name='read',
        block_number=block,
        context=context,
    )
    prices = [result[0][0] for result in results]

    if normalize:
        prices = [price / 1e18 for price in prices]

    return prices


#
# # fix broken onchain data
#


def _ensure_oracle_valid(
    *,
    oracle: spec.ContractAddress,
    token: spec.Address,
    block: spec.BlockNumberReference,
) -> None:
    if oracle == '0x0000000000000000000000000000000000000000':
        raise spec.MissingOracleException(
            'invalid oracle '
            + str(oracle)
            + ' for token '
            + str(token)
            + ' at block '
            + str(block)
        )


async def _async_replace_missing_oracle(
    *,
    oracle: spec.ContractAddress,
    token: spec.Address,
    context: spec.Context,
    replacement_block: spec.BlockNumberReference,
) -> spec.Address:

    if oracle == '0x0000000000000000000000000000000000000000':
        return await async_get_token_oracle(
            token=token,
            block=replacement_block,
            context=context,
            replace_missing=False,
            raise_if_missing=False,
        )
    else:
        return oracle


async def _async_replace_missing_oracles(
    *,
    oracles: typing.Sequence[spec.ContractAddress],
    tokens: typing.Sequence[spec.Address],
    context: spec.Context,
    replacement_block: spec.BlockNumberReference,
) -> typing.Sequence[spec.Address]:
    missing = [
        [oracle, token]
        for oracle, token in zip(oracles, tokens)
        if oracle == '0x0000000000000000000000000000000000000000'
    ]
    if len(missing) > 0:
        missing_oracles, missing_tokens = zip(*missing)
        results = await async_get_tokens_oracles(
            tokens=tokens,
            block=replacement_block,
            context=context,
            replace_missing=False,
            raise_if_missing=False,
        )
        result_iter = iter(results)
        replaced = []
        for oracle in oracles:
            if oracle == '0x0000000000000000000000000000000000000000':
                replaced.append(next(result_iter))
            else:
                replaced.append(oracle)
        return replaced

    else:
        return oracles

