from __future__ import annotations

import typing
import warnings

from ctc import rpc
from ctc import spec
from ... import rari_abis
from .. import pool_metadata
from .. import token_metadata


async def async_get_ctoken_exchange_rate(
    ctoken: spec.Address,
    block: spec.BlockNumberReference = 'latest',
) -> int:
    return await rpc.async_eth_call(
        to_address=ctoken,
        function_abi=rari_abis.ctoken_function_abis['exchangeRateCurrent'],
        block_number=block,
        empty_token=None,
    )


async def async_get_ctoken_exchange_rate_by_block(
    ctoken: spec.Address,
    blocks: typing.Sequence[spec.BlockNumberReference],
) -> list[int]:
    return await rpc.async_batch_eth_call(
        to_address=ctoken,
        function_abi=rari_abis.ctoken_function_abis['exchangeRateCurrent'],
        block_numbers=blocks,
        empty_token=None,
    )


async def async_get_ctoken_price(
    ctoken: spec.Address,
    oracle: spec.Address | None = None,
    block: spec.BlockNumberReference = 'latest',
    normalize: bool = True,
    raise_on_revert: bool = False,
) -> int | float:

    if oracle is None:
        oracle = await _async_get_ctoken_oracle(ctoken=ctoken)

    try:
        price = await rpc.async_eth_call(
            to_address=oracle,
            block_number=block,
            function_abi=rari_abis.oracle_abis['getUnderlyingPrice'],
            function_parameters=[ctoken],
        )
        if normalize:
            price /= 1e18
    except spec.RpcException as e:
        if raise_on_revert:
            raise e
        warnings.warn('price query failed for ctoken ' + str(ctoken))
        price = 0

    return price


async def _async_get_ctoken_oracle(ctoken: spec.Address) -> spec.Address:
    comptroller = await token_metadata.async_get_ctoken_comptroller(ctoken)
    oracle = await pool_metadata.async_get_pool_oracle(comptroller)
    return oracle

