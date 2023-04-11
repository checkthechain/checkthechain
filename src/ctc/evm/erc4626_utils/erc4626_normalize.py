from __future__ import annotations

import typing

from ctc import spec
from .. import erc20_utils
from . import erc4626_metadata

if typing.TYPE_CHECKING:
    import polars as pl


#
# # normalize shares
#


@typing.overload
async def async_normalize_erc4626_shares(
    token: spec.Address,
    shares: int,
    *,
    block: spec.BlockNumberReference | None = None,
    decimals: typing.SupportsInt | None = None,
    context: spec.Context = None,
) -> float:
    ...


@typing.overload
async def async_normalize_erc4626_shares(
    token: spec.Address,
    shares: pl.Series,
    *,
    block: spec.BlockNumberReference | None = None,
    decimals: typing.SupportsInt | None = None,
    context: spec.Context = None,
) -> pl.Series:
    ...


@typing.overload
async def async_normalize_erc4626_shares(
    token: spec.Address,
    shares: spec.NumpyArray,
    *,
    block: spec.BlockNumberReference | None = None,
    decimals: typing.SupportsInt | None = None,
    context: spec.Context = None,
) -> spec.NumpyArray:
    ...


@typing.overload
async def async_normalize_erc4626_shares(
    token: spec.Address,
    shares: typing.Sequence[int],
    *,
    block: spec.BlockNumberReference | None = None,
    decimals: typing.SupportsInt | None = None,
    context: spec.Context = None,
) -> typing.Sequence[float]:
    ...


async def async_normalize_erc4626_shares(
    token: spec.Address,
    shares: int | typing.Sequence[int] | pl.Series | spec.NumpyArray,
    *,
    block: spec.BlockNumberReference | None = None,
    decimals: typing.SupportsInt | None = None,
    context: spec.Context = None,
) -> float | typing.Sequence[float] | pl.Series | spec.NumpyArray:
    """normalize ERC-4626 vault shares (divide by 10 ** decimals)"""

    if hasattr(shares, '__iter__'):
        return await erc20_utils.async_normalize_erc20_quantities(
            quantities=typing.cast(typing.Sequence[int], shares),
            token=token,
            block=block,
            decimals=decimals,
            context=context,
        )

    else:
        return await erc20_utils.async_normalize_erc20_quantity(
            quantity=shares,
            token=token,
            block=block,
            decimals=decimals,
            context=context,
        )


async def async_normalize_erc4626s_shares(
    tokens: typing.Sequence[spec.Address],
    shares: typing.Sequence[int],
    *,
    block: spec.BlockNumberReference | None = None,
    context: spec.Context = None,
    decimals: typing.Optional[typing.Sequence[typing.SupportsInt]] = None,
) -> typing.Sequence[float]:
    """normalize ERC-4626 vaults shares (divide by 10 ** decimals)"""

    return await erc20_utils.async_normalize_erc20s_quantities(
        quantities=shares,
        tokens=tokens,
        block=block,
        decimals=decimals,
        context=context,
    )


#
# # normalize assets
#


@typing.overload
async def async_normalize_erc4626_assets(
    token: spec.Address,
    assets: int,
    *,
    block: spec.BlockNumberReference | None = None,
    decimals: typing.SupportsInt | None = None,
    context: spec.Context = None,
) -> float:
    ...


@typing.overload
async def async_normalize_erc4626_assets(
    token: spec.Address,
    assets: pl.Series,
    *,
    block: spec.BlockNumberReference | None = None,
    decimals: typing.SupportsInt | None = None,
    context: spec.Context = None,
) -> pl.Series:
    ...


@typing.overload
async def async_normalize_erc4626_assets(
    token: spec.Address,
    assets: spec.NumpyArray,
    *,
    block: spec.BlockNumberReference | None = None,
    decimals: typing.SupportsInt | None = None,
    context: spec.Context = None,
) -> spec.NumpyArray:
    ...


@typing.overload
async def async_normalize_erc4626_assets(
    token: spec.Address,
    assets: typing.Sequence[int],
    *,
    block: spec.BlockNumberReference | None = None,
    decimals: typing.SupportsInt | None = None,
    context: spec.Context = None,
) -> typing.Sequence[float]:
    ...


async def async_normalize_erc4626_assets(
    token: spec.Address,
    assets: int | typing.Sequence[int] | pl.Series | spec.NumpyArray,
    *,
    block: spec.BlockNumberReference | None = None,
    decimals: typing.SupportsInt | None = None,
    context: spec.Context = None,
) -> float | typing.Sequence[float] | pl.Series | spec.NumpyArray:
    """normalize ERC-4626 vault assets (divide by 10 ** decimals)"""

    asset = await erc4626_metadata.async_get_erc4626_asset(
        token=token,
        block=block,
        context=context,
    )

    if hasattr(assets, '__iter__'):
        return await erc20_utils.async_normalize_erc20_quantities(
            quantities=typing.cast(typing.Sequence[int], assets),
            token=asset,
            block=block,
            decimals=decimals,
            context=context,
        )
    else:
        return await erc20_utils.async_normalize_erc20_quantity(
            quantity=assets,
            token=asset,
            block=block,
            decimals=decimals,
            context=context,
        )


async def async_normalize_erc4626s_assets(
    tokens: typing.Sequence[spec.Address],
    assets: typing.Sequence[int],
    *,
    block: spec.BlockNumberReference | None = None,
    context: spec.Context = None,
    decimals: typing.Optional[typing.Sequence[typing.SupportsInt]] = None,
) -> typing.Sequence[float]:
    """normalize ERC-4626 vaults assets (divide by 10 ** decimals)"""

    asset_addresses = await erc4626_metadata.async_get_erc4626s_assets(
        tokens=tokens,
        block=block,
        context=context,
    )

    return await erc20_utils.async_normalize_erc20s_quantities(
        quantities=assets,
        tokens=asset_addresses,
        block=block,
        decimals=decimals,
        context=context,
    )
