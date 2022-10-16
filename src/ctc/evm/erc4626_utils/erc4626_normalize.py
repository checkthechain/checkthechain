from __future__ import annotations

import typing

from ctc import spec
from .. import erc20_utils
from . import erc4626_metadata

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
    provider: spec.ProviderReference = None,
) -> float:
    ...


@typing.overload
async def async_normalize_erc4626_shares(
    token: spec.Address,
    shares: spec.Series,
    *,
    block: spec.BlockNumberReference | None = None,
    decimals: typing.SupportsInt | None = None,
    provider: spec.ProviderReference = None,
) -> spec.Series:
    ...


@typing.overload
async def async_normalize_erc4626_shares(
    token: spec.Address,
    shares: spec.NumpyArray,
    *,
    block: spec.BlockNumberReference | None = None,
    decimals: typing.SupportsInt | None = None,
    provider: spec.ProviderReference = None,
) -> spec.NumpyArray:
    ...


@typing.overload
async def async_normalize_erc4626_shares(
    token: spec.Address,
    shares: typing.Sequence[int],
    *,
    block: spec.BlockNumberReference | None = None,
    decimals: typing.SupportsInt | None = None,
    provider: spec.ProviderReference = None,
) -> typing.Sequence[float]:
    ...


async def async_normalize_erc4626_shares(
    token: spec.Address,
    shares: int | typing.Sequence[int] | spec.Series | spec.NumpyArray,
    *,
    block: spec.BlockNumberReference | None = None,
    decimals: typing.SupportsInt | None = None,
    provider: spec.ProviderReference = None,
) -> float | typing.Sequence[float] | spec.Series | spec.NumpyArray:
    """normalize ERC-4626 vault shares (divide by 10 ** decimals)"""

    if hasattr(shares, '__iter__'):
        return await erc20_utils.async_normalize_erc20_quantities(
            quantities=typing.cast(typing.Sequence[int], shares),
            token=token,
            block=block,
            decimals=decimals,
            provider=provider,
        )

    else:
        return await erc20_utils.async_normalize_erc20_quantity(
            quantity=typing.cast(int, shares),
            token=token,
            block=block,
            decimals=decimals,
            provider=provider,
        )


async def async_normalize_erc4626s_shares(
    tokens: typing.Sequence[spec.Address],
    shares: typing.Sequence[int],
    *,
    block: spec.BlockNumberReference | None = None,
    provider: spec.ProviderReference = None,
    decimals: typing.Optional[typing.Sequence[typing.SupportsInt]] = None,
) -> typing.Sequence[float]:
    """normalize ERC-4626 vaults shares (divide by 10 ** decimals)"""

    return await erc20_utils.async_normalize_erc20s_quantities(
        quantities=shares,
        tokens=tokens,
        block=block,
        decimals=decimals,
        provider=provider,
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
    provider: spec.ProviderReference = None,
) -> float:
    ...


@typing.overload
async def async_normalize_erc4626_assets(
    token: spec.Address,
    assets: spec.Series,
    *,
    block: spec.BlockNumberReference | None = None,
    decimals: typing.SupportsInt | None = None,
    provider: spec.ProviderReference = None,
) -> spec.Series:
    ...


@typing.overload
async def async_normalize_erc4626_assets(
    token: spec.Address,
    assets: spec.NumpyArray,
    *,
    block: spec.BlockNumberReference | None = None,
    decimals: typing.SupportsInt | None = None,
    provider: spec.ProviderReference = None,
) -> spec.NumpyArray:
    ...


@typing.overload
async def async_normalize_erc4626_assets(
    token: spec.Address,
    assets: typing.Sequence[int],
    *,
    block: spec.BlockNumberReference | None = None,
    decimals: typing.SupportsInt | None = None,
    provider: spec.ProviderReference = None,
) -> typing.Sequence[float]:
    ...


async def async_normalize_erc4626_assets(
    token: spec.Address,
    assets: int | typing.Sequence[int] | spec.Series | spec.NumpyArray,
    *,
    block: spec.BlockNumberReference | None = None,
    decimals: typing.SupportsInt | None = None,
    provider: spec.ProviderReference = None,
) -> float | typing.Sequence[float] | spec.Series | spec.NumpyArray:
    """normalize ERC-4626 vault assets (divide by 10 ** decimals)"""

    asset = await erc4626_metadata.async_get_erc4626_asset(
        token=token,
        block=block,
        provider=provider,
    )

    if hasattr(assets, '__iter__'):
        return await erc20_utils.async_normalize_erc20_quantities(
            quantities=typing.cast(typing.Sequence[int], assets),
            token=asset,
            block=block,
            decimals=decimals,
            provider=provider,
        )
    else:
        return await erc20_utils.async_normalize_erc20_quantity(
            quantity=typing.cast(int, assets),
            token=asset,
            block=block,
            decimals=decimals,
            provider=provider,
        )


async def async_normalize_erc4626s_assets(
    tokens: typing.Sequence[spec.Address],
    assets: typing.Sequence[int],
    *,
    block: spec.BlockNumberReference | None = None,
    provider: spec.ProviderReference = None,
    decimals: typing.Optional[typing.Sequence[typing.SupportsInt]] = None,
) -> typing.Sequence[float]:
    """normalize ERC-4626 vaults assets (divide by 10 ** decimals)"""

    asset_addresses = await erc4626_metadata.async_get_erc4626s_assets(
        tokens=tokens,
        block=block,
        provider=provider,
    )

    return await erc20_utils.async_normalize_erc20s_quantities(
        quantities=assets,
        tokens=asset_addresses,
        block=block,
        decimals=decimals,
        provider=provider,
    )
