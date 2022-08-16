from __future__ import annotations

import asyncio
import typing

if typing.TYPE_CHECKING:
    import tooltime

from ctc import evm
from ctc import spec


class DEX:
    """Standardized interface for DEXes

    - All methods should be classmethods or staticmethods
    - The class should never be instantiated
    - Users do not need to use DEX classes directly
        - Functions in dex_utils will call the appropriate DEX methods

    Subclasses should implement the following methods:
    - async_get_new_pools
    - async_get_pool_assets

    Subclasses should specify the following properties:
    - _pool_factories
    """

    _pool_factories: typing.Mapping[int, typing.Sequence[spec.Address]] = {}

    def __init__(self) -> None:
        raise Exception(
            'this class should never be initialized'
            '\n\nuse functions in dex_utils instead'
        )

    #
    # # dex metadata
    #

    @classmethod
    def get_pool_factories(
        cls,
        network: spec.NetworkReference,
    ) -> typing.Sequence[spec.Address]:
        chain_id = evm.get_network_chain_id(network)
        if chain_id not in cls._pool_factories:
            raise Exception('unknown network: ' + str(chain_id))
        return cls._pool_factories[chain_id]

    #
    # # multiple pool functions
    #

    @classmethod
    async def async_get_pools(
        cls,
        *,
        factory: spec.Address | None = None,
        all_dex_factories: bool = False,
        assets: typing.Sequence[spec.Address] | None = None,
        start_block: spec.BlockNumberReference | None = None,
        end_block: spec.BlockNumberReference | None = None,
        start_time: tooltime.Timestamp | None = None,
        end_time: tooltime.Timestamp | None = None,
        update: bool = False,
        network: spec.NetworkReference | None = None,
        provider: spec.ProviderReference | None = None,
    ) -> typing.Sequence[spec.DexPool]:
        """return pools"""

        network, provider = evm.get_network_and_provider(network, provider)

        factories: typing.Sequence[spec.Address] | None = None
        if all_dex_factories:
            pool_factories = cls.get_pool_factories(network=network)
            if len(pool_factories) == 1:
                factory = pool_factories[0]
                factories = None
            elif len(pool_factories) > 1:
                factory = None
                factories = pool_factories
            else:
                factory = None
                factories = None

        if assets is not None and len(assets) == 0:
            assets = None

        start_block, end_block = await evm.async_parse_block_range(
            start_block=start_block,
            end_block=end_block,
            start_time=start_time,
            end_time=end_time,
            allow_none=True,
            provider=provider,
        )

        if start_block is not None:
            start_block = await evm.async_block_number_to_int(
                start_block,
                provider=provider,
            )
        if end_block is not None:
            end_block = await evm.async_block_number_to_int(
                end_block,
                provider=provider,
            )

        pools = await cls.async_get_stored_dex_pools(
            factory=factory,
            factories=factories,
            assets=assets,
            start_block=start_block,
            end_block=end_block,
            network=network,
        )

        if update:

            if factories is not None:
                coroutines = [
                    cls.async_update_factory_pools(
                        factory=factory,
                        network=network,
                        provider=provider,
                    )
                    for factory in factories
                ]
                results = await asyncio.gather(*coroutines)
                unique_new_pools = {
                    pool['address']: pool
                    for result in results
                    for pool in result
                }
                new_pools: typing.Sequence[spec.DexPool] = list(
                    unique_new_pools.values()
                )
            elif factory is not None:
                new_pools = await cls.async_update_factory_pools(
                    factory=factory,
                    network=network,
                    provider=provider,
                )
            else:
                new_pools = []

            # filter pools according to function inputs
            new_pools = _filter_pools(
                pools=new_pools,
                assets=assets,
                start_block=start_block,
                end_block=end_block,
            )

            pools = list(pools) + list(new_pools)

        return pools

    @classmethod
    async def async_get_stored_dex_pools(
        cls,
        *,
        factory: spec.Address | None = None,
        factories: typing.Sequence[spec.Address] | None = None,
        network: spec.NetworkReference,
        assets: typing.Sequence[spec.Address] | None = None,
        start_block: spec.BlockNumberReference | None = None,
        end_block: spec.BlockNumberReference | None = None,
    ) -> typing.Sequence[spec.DexPool]:
        """return pools"""

        from ctc import db

        pools = await db.async_query_dex_pools(
            factory=factory,
            factories=factories,
            assets=assets,
            network=network,
            start_block=start_block,
            end_block=end_block,
        )
        if pools is None:
            pools = []

        return pools

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
        raise NotImplementedError('async_get_new_pools')

    #
    # # multiple pool updates
    #

    @classmethod
    async def async_update_factory_pools(
        cls,
        factory: spec.Address,
        *,
        network: spec.NetworkReference | None = None,
        provider: spec.ProviderReference = None,
    ) -> typing.Sequence[spec.DexPool]:
        """update latest pools of factory"""

        from ctc import db

        network, provider = evm.get_network_and_provider(network, provider)

        # get new pools
        last_scanned_block = (
            await db.async_query_dex_pool_factory_last_scanned_block(
                factory=factory,
                network=network,
            )
        )
        if last_scanned_block is None:
            from ctc.toolbox import search_utils

            try:
                creation_block = await evm.async_get_contract_creation_block(
                    factory
                )
                if creation_block is None:
                    raise Exception(
                        'could not determine factory creation block'
                    )
                last_scanned_block = creation_block - 1
            except search_utils.NoMatchFound:
                last_scanned_block = -1

        latest_block = await evm.async_get_latest_block_number()

        if last_scanned_block + 1 <= latest_block:

            new_pools = await cls.async_get_new_pools(
                factory=factory,
                start_block=last_scanned_block + 1,
                end_block=latest_block,
            )
            await db.async_intake_dex_pools(
                factory=factory,
                dex_pools=new_pools,
                network=network,
                last_scanned_block=latest_block,
            )

        else:
            new_pools = []

        return new_pools

    @classmethod
    async def async_update_all_dex_factory_pools(
        cls,
        *,
        network: spec.NetworkReference | None = None,
        provider: spec.ProviderReference = None,
    ) -> typing.Sequence[spec.DexPool]:
        """update latest pools from all factories of dex"""

        network, provider = evm.get_network_and_provider(network, provider)

        coroutines = []
        for factory in cls.get_pool_factories(network=network):
            coroutine = cls.async_update_factory_pools(
                factory=factory,
                network=network,
                provider=provider,
            )
            coroutines.append(coroutine)
        results = await asyncio.gather(*coroutines)

        return [dex_pool for result in results for dex_pool in result]

    #
    # # single pool functions
    #

    @classmethod
    async def async_get_pool_assets(
        cls,
        pool: spec.Address,
        *,
        network: spec.NetworkReference | None = None,
        provider: spec.ProviderReference | None = None,
        block: spec.BlockNumberReference | None = None,
    ) -> typing.Sequence[spec.Address]:
        raise NotImplementedError('async_get_pool_assets')

    @classmethod
    async def async_get_pool_balance(
        cls,
        pool: spec.Address,
        asset: spec.Address,
        *,
        factory: spec.Address | None = None,
        normalize: bool = True,
        block: spec.BlockNumberReference | None = None,
        network: spec.NetworkReference | None = None,
        provider: spec.ProviderReference | None = None,
    ) -> int | float:

        network, provider = evm.get_network_and_provider(network, provider)

        return await evm.async_get_erc20_balance(
            wallet=pool,
            token=asset,
            normalize=normalize,
            block=block,
        )

    @classmethod
    async def async_get_pool_balances(
        cls,
        pool: spec.Address,
        *,
        factory: spec.Address | None = None,
        normalize: bool = True,
        block: spec.BlockNumberReference | None = None,
        network: spec.NetworkReference | None = None,
        provider: spec.ProviderReference | None = None,
    ) -> typing.Mapping[spec.Address, int | float]:

        network, provider = evm.get_network_and_provider(network, provider)

        pool_tokens = await cls.async_get_pool_assets(pool=pool)
        balances = await evm.async_get_erc20s_balances(
            wallet=pool,
            tokens=pool_tokens,
            normalize=normalize,
            block=block,
            provider=provider,
        )
        return dict(zip(pool_tokens, balances))

    @classmethod
    async def async_get_pool_balance_by_block(
        cls,
        pool: spec.Address,
        asset: spec.Address,
        *,
        blocks: typing.Sequence[spec.BlockNumberReference],
        factory: spec.Address | None = None,
        normalize: bool = True,
        network: spec.NetworkReference | None = None,
        provider: spec.ProviderReference | None = None,
    ) -> typing.Sequence[int | float]:

        network, provider = evm.get_network_and_provider(network, provider)

        return await evm.async_get_erc20_balance_by_block(
            wallet=pool,
            token=asset,
            normalize=normalize,
            blocks=blocks,
        )

    @classmethod
    async def async_get_pool_balances_by_block(
        cls,
        pool: spec.Address,
        *,
        blocks: typing.Sequence[spec.BlockNumberReference],
        factory: spec.Address | None = None,
        normalize: bool = True,
        network: spec.NetworkReference | None = None,
        provider: spec.ProviderReference | None = None,
    ) -> typing.Mapping[str, typing.Sequence[int | float]]:

        if len(blocks) == 0:
            raise NotImplementedError('must specify blocks')

        coroutines = [
            cls.async_get_pool_balances(
                pool=pool,
                factory=factory,
                normalize=normalize,
                block=block,
                network=network,
                provider=provider,
            )
            for block in blocks
        ]
        results = await asyncio.gather(*coroutines)
        balances_by_block: typing.MutableMapping[
            str, typing.MutableSequence[int | float]
        ] = {}
        for result in results:
            for asset, balance in result.items():
                balances_by_block.setdefault(asset, [])
                balances_by_block[asset].append(balance)

        return balances_by_block


def _filter_pools(
    *,
    pools: typing.Sequence[spec.DexPool],
    assets: typing.Sequence[str] | None = None,
    start_block: int | None = None,
    end_block: int | None = None,
) -> typing.Sequence[spec.DexPool]:

    filtered = []

    # filter the new pools according to input arguments
    for pool in pools:

        # check asset filter
        include = True
        if assets is not None:
            keys = ['asset0', 'asset1', 'asset2', 'asset3']
            for asset in assets:
                asset = asset.lower()
                include = any(pool[key] == asset for key in keys)  # type: ignore
                if not include:
                    break
        if not include:
            continue

        # check block range
        if start_block is not None and (
            pool['creation_block'] is None
            or pool['creation_block'] < start_block
        ):
            continue
        if end_block is not None and (
            pool['creation_block'] is None or pool['creation_block'] > end_block
        ):
            continue

        filtered.append(pool)

    return filtered
