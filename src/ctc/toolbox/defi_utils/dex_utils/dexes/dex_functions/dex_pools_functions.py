from __future__ import annotations

import typing

from ctc import spec

from .. import dex_class
from .. import dex_class_utils

if typing.TYPE_CHECKING:
    import tooltime


async def async_get_pools(
    *,
    dex: typing.Type[dex_class.DEX] | str | None = None,
    factory: spec.Address | None = None,
    network: spec.NetworkReference | None = None,
    assets: typing.Sequence[spec.Address] | None = None,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    update: bool = False,
    provider: spec.ProviderReference | None = None,
) -> typing.Sequence[spec.DexPool]:
    """get DEX pools matching given inputs"""

    # get dex
    all_dex_factories = dex is not None and factory is None
    if factory is None and dex is None:
        dex = dex_class.DEX

        if update:
            await async_update_all_dexes(
                network=network,
                provider=provider,
            )
            update = False

    else:
        dex = dex_class_utils.get_dex_class(
            dex=dex,
            factory=factory,
            network=network,
        )

    return await dex.async_get_pools(
        factory=factory,
        all_dex_factories=all_dex_factories,
        assets=assets,
        start_block=start_block,
        end_block=end_block,
        start_time=start_time,
        end_time=end_time,
        update=update,
        provider=provider,
    )


async def async_update_all_dexes(
    network: spec.NetworkReference | None = None,
    provider: spec.ProviderReference | None = None,
) -> typing.Mapping[str, typing.Mapping[str, typing.Any]]:
    """update local DEX database with latest on-chain entries"""

    import asyncio

    all_dexes = dex_class_utils.get_all_dex_classes()

    coroutines = []
    for dex in all_dexes.values():
        coroutine = dex.async_update_pools(network=network, provider=provider)
        coroutines.append(coroutine)

    results = await asyncio.gather(*coroutines)

    updates = {}
    for dex_name, result in zip(all_dexes.keys(), results):
        updates[dex_name] = {'new_pools': result}

    return updates
