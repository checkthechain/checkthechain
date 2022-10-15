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
    shares: typing.Sequence[int],
    *,
    block: spec.BlockNumberReference | None = None,
    decimals: typing.SupportsInt | None = None,
    provider: spec.ProviderReference = None,
) -> typing.Sequence[float]:
    ...


async def async_normalize_erc4626_shares(
    token: spec.Address,
    shares: int | typing.Sequence[int],
    *,
    block: spec.BlockNumberReference | None = None,
    decimals: typing.SupportsInt | None = None,
    provider: spec.ProviderReference = None,
) -> float | typing.Sequence[float]:

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


async def async_normalize_erc4626_shares_by_block(
    token: spec.Address,
    shares: typing.Sequence[int],
    *,
    blocks: typing.Sequence[spec.BlockNumberReference],
    provider: spec.ProviderReference,
    decimals: typing.Optional[typing.Sequence[typing.SupportsInt]] = None,
) -> typing.Sequence[float]:

    return await erc20_utils.async_normalize_erc20_quantities_by_block(
        quantities=shares,
        token=token,
        blocks=blocks,
        decimals=decimals,
        provider=provider,
    )


async def async_normalize_erc4626s_shares(
    tokens: typing.Sequence[spec.Address],
    shares: typing.Sequence[int],
    *,
    block: spec.BlockNumberReference | None = None,
    provider: spec.ProviderReference,
    decimals: typing.Optional[typing.Sequence[typing.SupportsInt]] = None,
) -> typing.Sequence[float]:

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
    assets: typing.Sequence[int],
    *,
    block: spec.BlockNumberReference | None = None,
    decimals: typing.SupportsInt | None = None,
    provider: spec.ProviderReference = None,
) -> typing.Sequence[float]:
    ...


async def async_normalize_erc4626_assets(
    token: spec.Address,
    assets: int | typing.Sequence[int],
    *,
    block: spec.BlockNumberReference | None = None,
    decimals: typing.SupportsInt | None = None,
    provider: spec.ProviderReference = None,
) -> float | typing.Sequence[float]:

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


async def async_normalize_erc4626_assets_by_block(
    token: spec.Address,
    assets: typing.Sequence[int],
    *,
    blocks: typing.Sequence[spec.BlockNumberReference],
    provider: spec.ProviderReference,
    decimals: typing.Optional[typing.Sequence[typing.SupportsInt]] = None,
) -> typing.Sequence[float]:

    asset = await erc4626_metadata.async_get_erc4626_asset(
        token=token,
        block=blocks[-1],
        provider=provider,
    )

    return await erc20_utils.async_normalize_erc20_quantities_by_block(
        quantities=assets,
        token=asset,
        blocks=blocks,
        decimals=decimals,
        provider=provider,
    )


async def async_normalize_erc4626s_assets(
    tokens: typing.Sequence[spec.Address],
    assets: typing.Sequence[int],
    *,
    block: spec.BlockNumberReference | None = None,
    provider: spec.ProviderReference,
    decimals: typing.Optional[typing.Sequence[typing.SupportsInt]] = None,
) -> typing.Sequence[float]:

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
