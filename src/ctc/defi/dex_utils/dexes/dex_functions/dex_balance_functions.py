from __future__ import annotations

import typing

from ctc import spec

from .. import dex_class
from .. import dex_class_utils


async def async_get_pool_balance(
    pool: spec.Address,
    asset: spec.Address,
    *,
    dex: typing.Type[dex_class.DEX] | str | None = None,
    factory: spec.Address | None = None,
    block: spec.BlockNumberReference | None = None,
    normalize: bool = True,
    context: spec.Context = None,
) -> int | float:
    """get balance of particular asset in pool"""

    dex = dex_class_utils.get_dex_class(
        dex=dex, factory=factory, context=context,
    )
    return await dex.async_get_pool_balance(
        pool=pool,
        asset=asset,
        block=block,
        normalize=normalize,
        context=context,
    )


async def async_get_pool_balances(
    pool: spec.Address,
    *,
    dex: typing.Type[dex_class.DEX] | str | None = None,
    factory: spec.Address | None = None,
    normalize: bool = True,
    block: spec.BlockNumberReference | None = None,
    context: spec.Context = None,
) -> typing.Mapping[spec.Address, int | float]:
    """get balances of all assets in pool"""

    dex = dex_class_utils.get_dex_class(
        dex=dex, factory=factory, context=context
    )
    return await dex.async_get_pool_balances(
        pool=pool,
        normalize=normalize,
        block=block,
        context=context,
    )


async def async_get_pool_balance_by_block(
    pool: spec.Address,
    asset: spec.Address,
    *,
    blocks: typing.Sequence[spec.BlockNumberReference],
    dex: typing.Type[dex_class.DEX] | str | None = None,
    factory: spec.Address | None = None,
    normalize: bool = True,
    context: spec.Context = None,
) -> typing.Sequence[int | float]:
    """get balances of particular asset in pool at specific blocks"""

    dex = dex_class_utils.get_dex_class(
        dex=dex, factory=factory, context=context,
    )
    return await dex.async_get_pool_balance_by_block(
        pool=pool,
        asset=asset,
        blocks=blocks,
        normalize=normalize,
        context=context,
    )


async def async_get_pool_balances_by_block(
    pool: spec.Address,
    *,
    blocks: typing.Sequence[spec.BlockNumberReference],
    dex: typing.Type[dex_class.DEX] | str | None = None,
    factory: spec.Address | None = None,
    normalize: bool = True,
    context: spec.Context = None,
) -> typing.Mapping[str, typing.Sequence[int | float]]:
    """get balances of all assets in pool at specific blocks"""

    dex = dex_class_utils.get_dex_class(
        dex=dex, factory=factory, context=context
    )
    return await dex.async_get_pool_balances_by_block(
        pool=pool,
        blocks=blocks,
        normalize=normalize,
        context=context,
    )
