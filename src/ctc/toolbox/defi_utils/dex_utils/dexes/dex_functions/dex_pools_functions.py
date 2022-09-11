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

    # get dex
    all_dex_factories = dex is not None and factory is None
    if factory is None and dex is None:
        dex = dex_class.DEX
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
