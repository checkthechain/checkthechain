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
    """Curve DEX"""

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
        network: spec.NetworkReference | None = None,
        provider: spec.ProviderReference | None = None,
    ) -> typing.Sequence[spec.DexPool]:

        network, provider = evm.get_network_and_provider(network, provider)

        start_block, end_block = await evm.async_resolve_block_range(
            start_block=start_block,
            end_block=end_block,
            start_time=start_time,
            end_time=end_time,
            allow_none=False,
            provider=provider,
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
                provider=provider,
            )

            pools = await rpc.async_batch_eth_call(
                to_address=factory,
                function_abi=curve_utils.function_abis['pool_list'],
                function_parameter_list=[
                    [index] for index in range(start_pool_count, end_pool_count)
                ],
                provider=provider,
            )

            creation_blocks_coroutine = asyncio.create_task(
                evm.async_get_contracts_creation_blocks(
                    pools, provider=provider
                )
            )

        coroutines = [
            curve_utils.async_get_pool_tokens(pool, provider=provider)
            for pool in pools
        ]
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

    @classmethod
    async def _async_get_pool_assets_from_node(
        cls,
        pool: spec.Address,
        *,
        network: spec.NetworkReference | None = None,
        provider: spec.ProviderReference | None = None,
        block: spec.BlockNumberReference | None = None,
    ) -> typing.Sequence[spec.Address]:
        network, provider = evm.get_network_and_provider(network, provider)
        return await curve_utils.async_get_pool_tokens(
            pool=pool,
            provider=provider,
        )

    @classmethod
    async def _async_get_pool_raw_trades(
        cls,
        pool: spec.Address,
        *,
        start_block: spec.BlockNumberReference | None = None,
        end_block: spec.BlockNumberReference | None = None,
        start_time: tooltime.Timestamp | None = None,
        end_time: tooltime.Timestamp | None = None,
        include_timestamps: bool = False,
        network: spec.NetworkReference | None = None,
        provider: spec.ProviderReference | None = None,
        verbose: bool = False,
    ) -> spec.RawDexTrades:

        import pandas as pd

        network, provider = evm.get_network_and_provider(network, provider)

        # get data
        trades = await evm.async_get_events(
            contract_address=pool,
            event_abi=curve_utils.pool_event_abis['TokenExchange'],
            start_block=start_block,
            end_block=end_block,
            start_time=start_time,
            end_time=end_time,
            verbose=verbose,
            include_timestamps=include_timestamps,
        )

        # check factory for whether TokenExchangeUnderlying is present
        contract_abi = await evm.async_get_contract_abi(pool, network=network)
        try:
            await evm.async_get_event_abi(
                contract_abi=contract_abi,
                event_name='TokenExchangeUnderlying',
            )
            has_token_exchange_underlying = True
        except LookupError:
            has_token_exchange_underlying = False

        if has_token_exchange_underlying:
            token_exchange_underlyings = await evm.async_get_events(
                pool,
                event_abi=curve_utils.pool_event_abis[
                    'TokenExchangeUnderlying'
                ],
                start_block=start_block,
                end_block=end_block,
                start_time=start_time,
                end_time=end_time,
                verbose=verbose,
                include_timestamps=include_timestamps,
            )
            trades = pd.concat([trades, token_exchange_underlyings])
            trades = trades.sort_index()

        # gather relevatn subset of data
        output: spec.RawDexTrades = {
            'transaction_hash': trades['transaction_hash'],
            'recipient': trades['arg__buyer'],
            'sold_id': trades['arg__sold_id'],
            'bought_id': trades['arg__bought_id'],
            'sold_amount': trades['arg__tokens_sold'].map(int),
            'bought_amount': trades['arg__tokens_bought'].map(int),
        }

        if include_timestamps:
            output['timestamp'] = trades['timestamp']

        return output
