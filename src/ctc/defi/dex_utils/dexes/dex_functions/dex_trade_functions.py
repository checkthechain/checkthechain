from __future__ import annotations

import typing

from ctc import spec
from .. import dex_class
from .. import dex_class_utils

if typing.TYPE_CHECKING:
    from typing_extensions import Literal

    import tooltime


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
    label: Literal['index', 'symbol', 'address'] = 'index',
    include_timestamps: bool = False,
    remove_missing_fields: bool = True,
    include_prices: bool = False,
    include_volumes: bool = False,
    context: spec.Context = None,
) -> spec.DataFrame:
    """get trades of a DEX pool"""

    dex = await dex_class_utils.async_get_dex_class(
        dex=dex,
        factory=factory,
        pool=pool,
        context=context,
    )

    return await dex.async_get_pool_trades(
        pool=pool,
        normalize=normalize,
        start_block=start_block,
        end_block=end_block,
        start_time=start_time,
        end_time=end_time,
        label=label,
        context=context,
        include_timestamps=include_timestamps,
        remove_missing_fields=remove_missing_fields,
        include_prices=include_prices,
        include_volumes=include_volumes,
    )
