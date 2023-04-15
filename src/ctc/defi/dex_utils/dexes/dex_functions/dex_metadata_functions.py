from __future__ import annotations

import typing

from ctc import spec

from .. import dex_class_utils
from .. import dex_directory


async def async_get_pool_assets(
    pool: spec.Address,
    *,
    context: spec.Context = None,
    factory: spec.Address | None = None,
) -> typing.Sequence[spec.Address]:
    """get assets of a given DEX pool"""

    from ctc import config

    read_cache, write_cache = config.get_context_cache_read_write(
        schema_name='dex_pools', context=context
    )

    # try obtaining pool from db
    if read_cache:
        from ctc import db

        pool_data = await db.async_query_dex_pool(address=pool, context=context)
        if pool_data is not None:
            assets: typing.MutableSequence[spec.Address] = []
            asset0 = pool_data['asset0']
            if asset0 is not None:
                assets.append(asset0)
            asset1 = pool_data['asset1']
            if asset1 is not None:
                assets.append(asset1)
            asset2 = pool_data['asset2']
            if asset2 is not None:
                assets.append(asset2)
            asset3 = pool_data['asset3']
            if asset3 is not None:
                assets.append(asset3)
            return assets

    # if not in db, acquire using RPC
    if factory is None:
        raise Exception('must specify factory if pool not in db')
    dex_name = dex_directory.get_dex_name_of_factory(
        factory=factory,
        context=context,
    )
    dex = dex_class_utils.get_dex_class(dex_name)
    return await dex.async_get_pool_assets(pool=pool, context=context)

