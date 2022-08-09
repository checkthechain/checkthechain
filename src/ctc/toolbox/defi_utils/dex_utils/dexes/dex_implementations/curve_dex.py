from __future__ import annotations

import asyncio
import typing

from ctc import evm
from ctc import rpc
from ctc import spec
from ctc.protocols import curve_utils
from .. import dex_class

if typing.TYPE_CHECKING:
    import tooltime


class CurveDEX(dex_class.DEX):

    _pool_factories = {
        1: [
            '0xb9fc157394af804a3578134a6585c0dc9cc990d4',
            '0x90e00ace148ca3b23ac1bc8c240c2a7dd9c2d7f5',
            '0x0959158b6040d32d04c301a72cbfd6b39e21c9ae',
            '0x8f942c20d02befc377d41445793068908e2250d0',
            '0xf18056bbd320e96a48e3fbf8bc061322531aac99',
            '0xbabe61887f1de2713c6f97e567623453d3c79f67',
        ],
    }

    @classmethod
    async def async_get_new_pools(
        cls,
        *,
        factory: spec.Address,
        start_block: spec.BlockNumberReference | None = None,
        end_block: spec.BlockNumberReference | None = None,
        start_time: tooltime.Timestamp | None = None,
        end_time: tooltime.Timestamp | None = None,
    ) -> typing.Sequence[spec.DexPool]:

        start_block, end_block = await evm.async_parse_block_range(
            start_block=start_block,
            end_block=end_block,
            start_time=start_time,
            end_time=end_time,
            allow_none=False,
        )

        start_block, end_block = await evm.async_block_numbers_to_int(
            [start_block, end_block]
        )

        if factory == curve_utils.curve_deployer_eoa:
            unfiltered_pools = curve_utils.get_non_factory_pools()
            pools = []
            for pool, creation_block in unfiltered_pools.items():
                if start_block is not None and creation_block < start_block:
                    continue
                if end_block is not None and creation_block > end_block:
                    continue
                pools.append(pool)

        else:
            start_pool_count, end_pool_count = await rpc.async_batch_eth_call(
                to_address=factory,
                function_abi=curve_utils.function_abis['pool_count'],
                block_numbers=[start_block, end_block],
            )

            pools = await rpc.async_batch_eth_call(
                to_address=factory,
                function_abi=curve_utils.function_abis['pool_list'],
                function_parameter_list=[
                    [index] for index in range(start_pool_count, end_pool_count)
                ],
            )

            creation_blocks_coroutine = asyncio.create_task(
                evm.async_get_contracts_creation_blocks(pools)
            )

        coroutines = [curve_utils.async_get_pool_tokens(pool) for pool in pools]
        pools_tokens = await asyncio.gather(*coroutines)

        if factory == curve_utils.curve_deployer_eoa:
            creation_blocks = [unfiltered_pools[pool] for pool in pools]
        else:
            creation_blocks_fetched = await creation_blocks_coroutine
            if any(block is None for block in creation_blocks_fetched):
                raise Exception('could not find creation block for pool')
            else:
                creation_blocks = typing.cast(
                    typing.List[int], creation_blocks_fetched
                )

        dex_pools = []
        for pool, pool_tokens, creation_block in zip(
            pools, pools_tokens, creation_blocks
        ):

            if len(pool_tokens) < 4:
                pool_tokens = pool_tokens + [None] * (4 - len(pool_tokens))
            if creation_block is None:
                raise Exception('could not determine creation block of pool')

            asset0 = pool_tokens[0]
            asset1 = pool_tokens[1]
            asset2 = pool_tokens[2]
            asset3 = pool_tokens[3]

            dex_pool: spec.DexPool = {
                'address': pool,
                'factory': factory,
                'asset0': asset0,
                'asset1': asset1,
                'asset2': asset2,
                'asset3': asset3,
                'fee': None,
                'creation_block': creation_block,
                'additional_data': {},
            }
            dex_pools.append(dex_pool)

        return dex_pools
