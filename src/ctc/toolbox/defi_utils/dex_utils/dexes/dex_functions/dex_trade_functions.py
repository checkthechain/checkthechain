from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    from typing_extensions import Literal

    import tooltime

from ctc import spec
from .. import dex_class
from .. import dex_class_utils


async def async_get_pool_trades(
    pool: spec.Address,
    *,
    dex: typing.Type[dex_class.DEX] | str | None = None,
    factory: spec.Address | None = None,
    normalize: bool = False,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    network: spec.NetworkReference | None = None,
    label: Literal['index', 'symbol', 'address'] = 'index',
    provider: spec.ProviderReference = None,
    include_timestamps: bool = False,
    remove_missing_fields: bool = True,
    include_prices: bool = False,
    include_volumes: bool = False,
) -> spec.DataFrame:
    """get trades of a DEX pool"""

    dex = await dex_class_utils.async_get_dex_class(
        dex=dex,
        factory=factory,
        pool=pool,
        network=network,
        provider=provider,
    )

    return await dex.async_get_pool_trades(
        pool=pool,
        normalize=normalize,
        start_block=start_block,
        end_block=end_block,
        start_time=start_time,
        end_time=end_time,
        label=label,
        network=network,
        provider=provider,
        include_timestamps=include_timestamps,
        remove_missing_fields=remove_missing_fields,
        include_prices=include_prices,
        include_volumes=include_volumes,
    )
