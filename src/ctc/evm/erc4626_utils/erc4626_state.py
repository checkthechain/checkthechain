
from __future__ import annotations

import typing

from ctc import spec
from . import erc4626_normalize
from . import erc4626_spec


#
# # conversions
#


async def async_convert_to_erc4626_assets(
    token: spec.Address,
    shares: typing.SupportsInt,
    *,
    context: spec.Context = None,
    block: spec.BlockNumberReference | None = None,
) -> int:
    """convert ERC-4626 vault shares to assets"""
    from ctc import rpc

    assets: int = await rpc.async_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['convertToAssets'],
        function_parameters=[int(shares)],
        block_number=block,
        context=context,
    )
    return assets


async def async_convert_to_erc4626_assets_by_block(
    token: spec.Address,
    shares: typing.SupportsInt,
    *,
    context: spec.Context = None,
    blocks: typing.Sequence[spec.BlockNumberReference],
) -> typing.Sequence[int]:
    """convert ERC-4626 vault shares to assets"""
    from ctc import rpc

    assets: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['convertToAssets'],
        function_parameters=[int(shares)],
        block_numbers=blocks,
        context=context,
    )
    return assets


async def async_convert_to_erc4626s_assets(
    tokens: typing.Sequence[spec.Address],
    shares: typing.Sequence[typing.SupportsInt],
    *,
    context: spec.Context = None,
    block: spec.BlockNumberReference | None = None,
) -> typing.Sequence[int]:
    """convert ERC-4626 vault shares to assets"""

    import asyncio

    coroutines = [
        async_convert_to_erc4626_assets(
            token=token, shares=subshares, context=context, block=block
        )
        for token, subshares in zip(tokens, shares)
    ]
    return await asyncio.gather(*coroutines)


async def async_convert_to_erc4626_shares(
    token: spec.Address,
    assets: typing.SupportsInt,
    *,
    context: spec.Context = None,
    block: spec.BlockNumberReference | None = None,
) -> int:
    """convert ERC-4626 vault assets to shares"""

    from ctc import rpc

    shares: int = await rpc.async_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['convertToShares'],
        function_parameters=[int(assets)],
        block_number=block,
        context=context,
    )
    return shares


async def async_convert_to_erc4626_shares_by_block(
    token: spec.Address,
    assets: typing.SupportsInt,
    *,
    context: spec.Context = None,
    blocks: typing.Sequence[spec.BlockNumberReference],
) -> typing.Sequence[int]:
    """convert ERC-4626 vault assets to shares"""

    from ctc import rpc

    shares: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['convertToShares'],
        function_parameters=[int(assets)],
        block_numbers=blocks,
        context=context,
    )
    return shares


async def async_convert_to_erc4626s_shares(
    tokens: typing.Sequence[spec.Address],
    assets: typing.Sequence[typing.SupportsInt],
    *,
    context: spec.Context = None,
    block: spec.BlockNumberReference | None = None,
) -> typing.Sequence[int]:
    """convert ERC-4626 vault assets to shares"""

    import asyncio

    coroutines = [
        async_convert_to_erc4626_shares(
            token=token, assets=subassets, context=context, block=block
        )
        for token, subassets in zip(tokens, assets)
    ]
    return await asyncio.gather(*coroutines)


#
# # max deposits, max mints, max redeems, max withdrawals
#


async def async_get_erc4626_max_deposit(
    token: spec.Address,
    receiver: spec.Address,
    *,
    context: spec.Context = None,
    block: spec.BlockNumberReference | None = None,
    normalize: bool = True,
) -> int | float:
    """get max amount of assets that receiver can deposit in ERC-4626 vault"""

    from ctc import rpc

    max_deposit: int = await rpc.async_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['maxDeposit'],
        function_parameters=[receiver],
        block_number=block,
        context=context,
    )
    if normalize:
        return await erc4626_normalize.async_normalize_erc4626_assets(
            token=token,
            assets=max_deposit,
            context=context,
            block=block,
        )
    else:
        return max_deposit


async def async_get_erc4626_max_deposit_by_block(
    token: spec.Address,
    receiver: spec.Address,
    *,
    context: spec.Context = None,
    blocks: typing.Sequence[spec.BlockNumberReference],
    normalize: bool = True,
) -> typing.Sequence[int | float]:
    """get max amount of assets that receiver can deposit in ERC-4626 vault"""

    from ctc import rpc

    max_deposits: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['maxDeposit'],
        function_parameters=[receiver],
        block_numbers=blocks,
        context=context,
    )
    if normalize:
        return await erc4626_normalize.async_normalize_erc4626_assets(
            token=token,
            assets=max_deposits,
            context=context,
            block=blocks[-1],
        )
    else:
        return max_deposits


async def async_get_erc4626s_max_deposits(
    tokens: typing.Sequence[spec.Address],
    receiver: spec.Address,
    *,
    context: spec.Context = None,
    block: spec.BlockNumberReference | None = None,
    normalize: bool = True,
) -> typing.Sequence[int | float]:
    """get max amount of assets that receiver can deposit in ERC-4626 vaults"""

    from ctc import rpc

    max_deposits: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_addresses=tokens,
        function_abi=erc4626_spec.erc4626_function_abis['maxDeposit'],
        function_parameters=[receiver],
        block_number=block,
        context=context,
    )
    if normalize:
        return await erc4626_normalize.async_normalize_erc4626s_assets(
            tokens=tokens,
            assets=max_deposits,
            context=context,
            block=block,
        )
    else:
        return max_deposits


async def async_get_erc4626_max_mint(
    token: spec.Address,
    receiver: spec.Address,
    *,
    context: spec.Context = None,
    block: spec.BlockNumberReference | None = None,
    normalize: bool = True,
) -> int | float:
    """get max amount of shares that receiver can mint in ERC-4626 vault"""

    from ctc import rpc

    max_mint: int = await rpc.async_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['maxMint'],
        function_parameters=[receiver],
        block_number=block,
        context=context,
    )
    if normalize:
        return await erc4626_normalize.async_normalize_erc4626_shares(
            token=token,
            shares=max_mint,
            context=context,
            block=block,
        )
    else:
        return max_mint


async def async_get_erc4626_max_mint_by_block(
    token: spec.Address,
    receiver: spec.Address,
    *,
    context: spec.Context = None,
    blocks: typing.Sequence[spec.BlockNumberReference],
    normalize: bool = True,
) -> typing.Sequence[int | float]:
    """get max amount of shares that receiver can mint in ERC-4626 vault"""

    from ctc import rpc

    max_mints: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['maxMint'],
        function_parameters=[receiver],
        block_numbers=blocks,
        context=context,
    )
    if normalize:
        return await erc4626_normalize.async_normalize_erc4626_shares(
            token=token,
            shares=max_mints,
            context=context,
            block=blocks[-1],
        )
    else:
        return max_mints


async def async_get_erc4626s_max_mints(
    tokens: typing.Sequence[spec.Address],
    receiver: spec.Address,
    *,
    context: spec.Context = None,
    block: spec.BlockNumberReference | None = None,
    normalize: bool = True,
) -> typing.Sequence[int | float]:
    """get max amount of shares that receiver can mint in ERC-4626 vaults"""

    from ctc import rpc

    max_mints: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_addresses=tokens,
        function_abi=erc4626_spec.erc4626_function_abis['maxMint'],
        function_parameters=[receiver],
        block_number=block,
        context=context,
    )
    if normalize:
        return await erc4626_normalize.async_normalize_erc4626s_shares(
            tokens=tokens,
            shares=max_mints,
            context=context,
            block=block,
        )
    else:
        return max_mints


async def async_get_erc4626_max_redeem(
    token: spec.Address,
    owner: spec.Address,
    *,
    context: spec.Context = None,
    block: spec.BlockNumberReference | None = None,
    normalize: bool = True,
) -> int | float:
    """get max amount of shares that owner can redeem from ERC-4626 vault"""

    from ctc import rpc

    max_redeem: int = await rpc.async_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['maxRedeem'],
        function_parameters=[owner],
        block_number=block,
        context=context,
    )
    if normalize:
        return await erc4626_normalize.async_normalize_erc4626_shares(
            token=token,
            shares=max_redeem,
            context=context,
            block=block,
        )
    else:
        return max_redeem


async def async_get_erc4626_max_redeem_by_block(
    token: spec.Address,
    owner: spec.Address,
    *,
    context: spec.Context = None,
    blocks: typing.Sequence[spec.BlockNumberReference],
    normalize: bool = True,
) -> typing.Sequence[int | float]:
    """get max amount of shares that owner can redeem from ERC-4626 vault"""

    from ctc import rpc

    max_redeems: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['maxRedeem'],
        function_parameters=[owner],
        block_numbers=blocks,
        context=context,
    )
    if normalize:
        return await erc4626_normalize.async_normalize_erc4626_shares(
            token=token,
            shares=max_redeems,
            context=context,
            block=blocks[-1],
        )
    else:
        return max_redeems


async def async_get_erc4626s_max_redeems(
    tokens: typing.Sequence[spec.Address],
    owner: spec.Address,
    *,
    context: spec.Context = None,
    block: spec.BlockNumberReference | None = None,
    normalize: bool = True,
) -> typing.Sequence[int | float]:
    """get max amount of shares that owner can redeem from ERC-4626 vaults"""

    from ctc import rpc

    max_redeems: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_addresses=tokens,
        function_abi=erc4626_spec.erc4626_function_abis['maxRedeem'],
        function_parameters=[owner],
        block_number=block,
        context=context,
    )
    if normalize:
        return await erc4626_normalize.async_normalize_erc4626s_shares(
            tokens=tokens,
            shares=max_redeems,
            context=context,
            block=block,
        )
    else:
        return max_redeems


async def async_get_erc4626_max_withdraw(
    token: spec.Address,
    owner: spec.Address,
    *,
    context: spec.Context = None,
    block: spec.BlockNumberReference | None = None,
    normalize: bool = True,
) -> int | float:
    """get max amount of shares that owner can withdraw from ERC-4626 vault"""

    from ctc import rpc

    max_withdraw: int = await rpc.async_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['maxWithdraw'],
        function_parameters=[owner],
        block_number=block,
        context=context,
    )
    if normalize:
        return await erc4626_normalize.async_normalize_erc4626_assets(
            token=token,
            assets=max_withdraw,
            context=context,
            block=block,
        )
    else:
        return max_withdraw


async def async_get_erc4626_max_withdraw_by_block(
    token: spec.Address,
    owner: spec.Address,
    *,
    context: spec.Context = None,
    blocks: typing.Sequence[spec.BlockNumberReference],
    normalize: bool = True,
) -> typing.Sequence[int | float]:
    """get max amount of shares that owner can withdraw from ERC-4626 vault"""

    from ctc import rpc

    max_withdraws: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['maxWithdraw'],
        function_parameters=[owner],
        block_numbers=blocks,
        context=context,
    )
    if normalize:
        return await erc4626_normalize.async_normalize_erc4626_assets(
            token=token,
            assets=max_withdraws,
            context=context,
            block=blocks[-1],
        )
    else:
        return max_withdraws


async def async_get_erc4626s_max_withdraws(
    tokens: typing.Sequence[spec.Address],
    owner: spec.Address,
    *,
    context: spec.Context = None,
    block: spec.BlockNumberReference | None = None,
    normalize: bool = True,
) -> typing.Sequence[int | float]:
    """get max amount of shares that owner can withdraw from ERC-4626 vaults"""

    from ctc import rpc

    max_withdraws: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_addresses=tokens,
        function_abi=erc4626_spec.erc4626_function_abis['maxWithdraw'],
        function_parameters=[owner],
        block_number=block,
        context=context,
    )
    if normalize:
        return await erc4626_normalize.async_normalize_erc4626s_assets(
            tokens=tokens,
            assets=max_withdraws,
            context=context,
            block=block,
        )
    else:
        return max_withdraws


#
# # previews of deposits, mints, redeems, and withdrawals
#


async def async_preview_erc4626_deposit(
    token: spec.Address,
    assets: float | int,
    *,
    context: spec.Context = None,
    block: spec.BlockNumberReference | None = None,
) -> int:
    """return shares received for assets deposited into ERC-4626 vault"""
    from ctc import rpc

    deposit: int = await rpc.async_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['previewDeposit'],
        function_parameters=[assets],
        block_number=block,
        context=context,
    )
    return deposit


async def async_preview_erc4626_deposit_by_block(
    token: spec.Address,
    assets: float | int,
    *,
    context: spec.Context = None,
    blocks: typing.Sequence[spec.BlockNumberReference],
) -> typing.Sequence[int]:
    """return shares received for assets deposited into ERC-4626 vault"""
    from ctc import rpc

    deposit: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['previewDeposit'],
        function_parameters=[assets],
        block_numbers=blocks,
        context=context,
    )
    return deposit


async def async_preview_erc4626s_deposits(
    tokens: typing.Sequence[spec.Address],
    assets: float | int,
    *,
    context: spec.Context = None,
    block: spec.BlockNumberReference | None = None,
) -> typing.Sequence[int]:
    """return shares received for assets deposited into ERC-4626 vaults"""
    from ctc import rpc

    deposits: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_addresses=tokens,
        function_abi=erc4626_spec.erc4626_function_abis['previewDeposit'],
        function_parameters=[assets],
        block_number=block,
        context=context,
    )
    return deposits


async def async_preview_erc4626_mint(
    token: spec.Address,
    shares: float | int,
    *,
    context: spec.Context = None,
    block: spec.BlockNumberReference | None = None,
) -> int:
    """return assets needed for shared minted from ERC-4626 vault"""
    from ctc import rpc

    mint: int = await rpc.async_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['previewMint'],
        function_parameters=[shares],
        block_number=block,
        context=context,
    )
    return mint


async def async_preview_erc4626_mint_by_block(
    token: spec.Address,
    shares: float | int,
    *,
    context: spec.Context = None,
    blocks: typing.Sequence[spec.BlockNumberReference],
) -> typing.Sequence[int]:
    """return assets needed for shared minted from ERC-4626 vault"""
    from ctc import rpc

    mint: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['previewMint'],
        function_parameters=[shares],
        block_numbers=blocks,
        context=context,
    )
    return mint


async def async_preview_erc4626s_mints(
    tokens: typing.Sequence[spec.Address],
    shares: float | int,
    *,
    context: spec.Context = None,
    block: spec.BlockNumberReference | None = None,
) -> typing.Sequence[int]:
    """return assets needed for shared minted from ERC-4626 vaults"""
    from ctc import rpc

    mints: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_addresses=tokens,
        function_abi=erc4626_spec.erc4626_function_abis['previewMint'],
        function_parameters=[shares],
        block_number=block,
        context=context,
    )
    return mints


async def async_preview_erc4626_redeem(
    token: spec.Address,
    shares: float | int,
    *,
    context: spec.Context = None,
    block: spec.BlockNumberReference | None = None,
) -> int:
    """return assets received for redeeming shares of ERC-4626 vault"""
    from ctc import rpc

    redeem: int = await rpc.async_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['previewRedeem'],
        function_parameters=[shares],
        block_number=block,
        context=context,
    )
    return redeem


async def async_preview_erc4626_redeem_by_block(
    token: spec.Address,
    shares: float | int,
    *,
    context: spec.Context = None,
    blocks: typing.Sequence[spec.BlockNumberReference],
) -> typing.Sequence[int]:
    """return assets received for redeeming shares of ERC-4626 vault"""
    from ctc import rpc

    redeem: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['previewRedeem'],
        function_parameters=[shares],
        block_numbers=blocks,
        context=context,
    )
    return redeem


async def async_preview_erc4626s_redeems(
    tokens: typing.Sequence[spec.Address],
    shares: float | int,
    *,
    context: spec.Context = None,
    block: spec.BlockNumberReference | None = None,
) -> typing.Sequence[int]:
    """return assets received for redeeming shares of ERC-4626 vaults"""
    from ctc import rpc

    redeems: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_addresses=tokens,
        function_abi=erc4626_spec.erc4626_function_abis['previewRedeem'],
        function_parameters=[shares],
        block_number=block,
        context=context,
    )
    return redeems


async def async_preview_erc4626_withdraw(
    token: spec.Address,
    assets: float | int,
    *,
    context: spec.Context = None,
    block: spec.BlockNumberReference | None = None,
) -> int:
    """return shares needed for redeeming assets from ERC-4626 vault"""
    from ctc import rpc

    withdraw: int = await rpc.async_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['previewWithdraw'],
        function_parameters=[assets],
        block_number=block,
        context=context,
    )
    return withdraw


async def async_preview_erc4626_withdraw_by_block(
    token: spec.Address,
    assets: float | int,
    *,
    context: spec.Context = None,
    blocks: typing.Sequence[spec.BlockNumberReference],
) -> typing.Sequence[int]:
    """return shares needed for redeeming assets from ERC-4626 vault"""
    from ctc import rpc

    withdraw: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['previewWithdraw'],
        function_parameters=[assets],
        block_numbers=blocks,
        context=context,
    )
    return withdraw


async def async_preview_erc4626s_withdraws(
    tokens: typing.Sequence[spec.Address],
    assets: float | int,
    *,
    context: spec.Context = None,
    block: spec.BlockNumberReference | None = None,
) -> typing.Sequence[int]:
    """return shares needed for redeeming assets from ERC-4626 vaults"""
    from ctc import rpc

    withdraws: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_addresses=tokens,
        function_abi=erc4626_spec.erc4626_function_abis['previewWithdraw'],
        function_parameters=[assets],
        block_number=block,
        context=context,
    )
    return withdraws


#
# # total assets
#


async def async_get_erc4626_total_assets(
    token: spec.Address,
    *,
    context: spec.Context = None,
    block: spec.BlockNumberReference | None = None,
    normalize: bool = True,
) -> int | float:
    """return total amount of assets in ERC-4626 vault"""
    from ctc import rpc

    assets: int = await rpc.async_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['totalAssets'],
        block_number=block,
        context=context,
    )
    if normalize:
        return await erc4626_normalize.async_normalize_erc4626_assets(
            token=token,
            assets=assets,
            context=context,
            block=block,
        )
    return assets


async def async_get_erc4626_total_assets_by_block(
    token: spec.Address,
    *,
    context: spec.Context = None,
    blocks: typing.Sequence[spec.BlockNumberReference],
    normalize: bool = True,
) -> typing.Sequence[int | float]:
    """return total amount of assets in ERC-4626 vault"""
    from ctc import rpc

    assets: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['totalAssets'],
        block_numbers=blocks,
        context=context,
    )
    if normalize and len(assets) > 0:
        return await erc4626_normalize.async_normalize_erc4626_assets(
            token=token,
            assets=assets,
            context=context,
            block=blocks[-1],
        )
    return assets


async def async_get_erc4626s_total_assets(
    tokens: typing.Sequence[spec.Address],
    *,
    context: spec.Context = None,
    block: spec.BlockNumberReference | None = None,
    normalize: bool = True,
) -> typing.Sequence[int | float]:
    """return total amount of assets in ERC-4626 vaults"""
    from ctc import rpc

    assets: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_addresses=tokens,
        function_abi=erc4626_spec.erc4626_function_abis['totalAssets'],
        block_number=block,
        context=context,
    )
    if normalize:
        return await erc4626_normalize.async_normalize_erc4626s_assets(
            tokens=tokens,
            assets=assets,
            context=context,
            block=block,
        )
    return assets
