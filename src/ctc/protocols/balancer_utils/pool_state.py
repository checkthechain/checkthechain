from __future__ import annotations

import asyncio
import typing

from ctc import directory
from ctc import evm
from ctc import rpc
from ctc import spec

from . import pool_metadata


#
# # weights
#


async def async_get_pool_weights_raw(
    pool_address: spec.ContractAddress,
    block: spec.BlockNumberReference = 'latest',
) -> typing.Union[list[int], list[float]]:

    return await rpc.async_eth_call(
        to_address=pool_address,
        function_name='getNormalizedWeights',
        block_number=block,
    )


async def async_get_pool_weights(
    pool_address: spec.ContractAddress,
    block: spec.BlockNumberReference = 'latest',
    normalize: bool = True,
) -> typing.Union[
    dict[spec.ContractAddress, int],
    dict[spec.ContractAddress, float],
]:

    tokens_coroutine = pool_metadata.async_get_pool_tokens(
        pool_address=pool_address, block=block
    )
    weights_coroutine = async_get_pool_weights_raw(
        pool_address=pool_address, block=block
    )

    tokens, weights = await asyncio.gather(tokens_coroutine, weights_coroutine)

    if normalize:
        weights = [weight / 1e18 for weight in weights]

    return dict(zip(tokens, weights))


async def async_get_pool_weights_by_block(
    pool_address: spec.ContractAddress,
    blocks: typing.Sequence[spec.BlockNumberReference],
    normalize: bool = True,
) -> typing.Union[
    dict[spec.BlockNumberReference, int],
    dict[spec.BlockNumberReference, float],
]:

    weights = await rpc.async_batch_eth_call(
        to_address=pool_address,
        function_name='getNormalizedWeights',
        block_numbers=blocks,
        provider={'chunk_size': 100},
    )

    if normalize:
        weights = [
            [block_weight / 1e18 for block_weight in block_weights]
            for block_weights in weights
        ]

    return dict(zip(blocks, weights))


#
# # fees
#


async def async_get_pool_fees(
    pool_address: spec.ContractAddress,
    block: spec.BlockNumberReference = 'latest',
    normalize: bool = True,
):

    fees = await rpc.async_eth_call(
        to_address=pool_address,
        function_name='getSwapFeePercentage',
        block_number=block,
    )

    if normalize:
        fees /= 1e18

    return fees


#
# # balances
#


async def async_get_pool_balances(
    *,
    pool_address: typing.Optional[spec.ContractAddress] = None,
    pool_id: typing.Optional[spec.HexData] = None,
    block: spec.BlockNumberReference = 'latest',
    vault: typing.Optional[spec.ContractAddress] = None,
    normalize: bool = True,
) -> typing.Union[
    dict[spec.Address, int],
    dict[spec.Address, float],
]:

    if vault is None:
        vault = directory.get_address(name='Vault', label='balancer')
    if pool_id is None:
        pool_id = await pool_metadata.async_get_pool_id(
            pool_address, block=block
        )

    pool_tokens = await rpc.async_eth_call(
        to_address=vault,
        function_name='getPoolTokens',
        function_parameters=[pool_id],
        block_number=block,
        package_named_outputs=True,
    )

    pool_balances = dict(zip(pool_tokens['tokens'], pool_tokens['balances']))

    if normalize:
        tokens = pool_balances.keys()
        decimals = await evm.async_get_erc20s_decimals(
            tokens=tokens,
            block=block,
        )
        for token, decimal in zip(tokens, decimals):
            pool_balances[token] /= 10 ** decimal

    return pool_balances

