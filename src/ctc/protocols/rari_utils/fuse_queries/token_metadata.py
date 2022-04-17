from __future__ import annotations

from ctc import rpc
from ctc import spec

from .. import rari_abis


async def async_get_ctoken_comptroller(
    ctoken: spec.Address,
    block: spec.BlockNumberReference = 'latest',
) -> spec.Address:
    return await rpc.async_eth_call(
        to_address=ctoken,
        block_number=block,
        function_abi=rari_abis.ctoken_function_abis['comptroller'],
    )


async def async_get_ctoken_underlying(
    ctoken: spec.Address,
    block: spec.BlockNumberReference = 'latest',
) -> spec.Address:
    return await rpc.async_eth_call(
        to_address=ctoken,
        block_number=block,
        function_abi=rari_abis.ctoken_function_abis['underlying'],
    )


async def async_get_ctoken_irm(
    ctoken: spec.Address,
    block: spec.BlockNumberReference = 'latest',
) -> spec.Address:
    return await rpc.async_eth_call(
        to_address=ctoken,
        block_number=block,
        function_abi=rari_abis.ctoken_function_abis['interestRateModel'],
    )

