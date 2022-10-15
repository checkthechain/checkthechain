# TODO: balanceOf, totalSupply
# by_block
# erc4626s
# ? / s / s_of_addresses / None

from __future__ import annotations

import typing

from ctc import rpc
from ctc import spec
from . import erc4626_normalize
from . import erc4626_spec


#
# # conversions
#


async def async_convert_to_erc4626_assets(
    token: spec.Address,
    shares: float | int,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> int:
    assets: int = await rpc.async_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['convertToAssets'],
        function_parameters=[int(shares)],
        block_number=block,
        provider=provider,
    )
    return assets


async def async_convert_to_erc4626_assets_by_block(
    token: spec.Address,
    shares: float | int,
    *,
    provider: spec.ProviderReference = None,
    blocks: typing.Sequence[spec.BlockNumberReference],
) -> typing.Sequence[int]:
    assets: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['convertToAssets'],
        function_parameters=[int(shares)],
        block_numbers=blocks,
        provider=provider,
    )
    return assets


async def async_convert_to_erc4626s_assets(
    tokens: typing.Sequence[spec.Address],
    shares: float | int,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> typing.Sequence[int]:
    assets: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_addresses=tokens,
        function_abi=erc4626_spec.erc4626_function_abis['convertToAssets'],
        function_parameters=[int(shares)],
        block_number=block,
        provider=provider,
    )
    return assets


async def async_convert_to_erc4626_shares(
    token: spec.Address,
    assets: float | int,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> int:
    shares: int = await rpc.async_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['convertToShares'],
        function_parameters=[int(assets)],
        block_number=block,
        provider=provider,
    )
    return shares


async def async_convert_to_erc4626_shares_by_block(
    token: spec.Address,
    assets: float | int,
    *,
    provider: spec.ProviderReference = None,
    blocks: typing.Sequence[spec.BlockNumberReference],
) -> typing.Sequence[int]:
    shares: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['convertToShares'],
        function_parameters=[int(assets)],
        block_numbers=blocks,
        provider=provider,
    )
    return shares


async def async_convert_to_erc4626s_shares(
    tokens: typing.Sequence[spec.Address],
    assets: float | int,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> typing.Sequence[int]:
    shares: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_addresses=tokens,
        function_abi=erc4626_spec.erc4626_function_abis['convertToShares'],
        function_parameters=[int(assets)],
        block_number=block,
        provider=provider,
    )
    return shares


#
# # max deposits, max mints, max redeems, max withdrawals
#


async def async_get_erc4626_max_deposit(
    token: spec.Address,
    receiver: spec.Address,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> int:
    max_deposit: int = await rpc.async_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['maxDeposit'],
        function_parameters=[receiver],
        block_number=block,
        provider=provider,
    )
    return max_deposit


async def async_get_erc4626_max_deposit_by_block(
    token: spec.Address,
    receiver: spec.Address,
    *,
    provider: spec.ProviderReference = None,
    blocks: typing.Sequence[spec.BlockNumberReference],
) -> typing.Sequence[int]:
    max_deposits: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['maxDeposit'],
        function_parameters=[receiver],
        block_numbers=blocks,
        provider=provider,
    )
    return max_deposits


async def async_get_erc4626s_max_deposits(
    tokens: typing.Sequence[spec.Address],
    receiver: spec.Address,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> typing.Sequence[int]:
    max_deposits: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_addresses=tokens,
        function_abi=erc4626_spec.erc4626_function_abis['maxDeposit'],
        function_parameters=[receiver],
        block_number=block,
        provider=provider,
    )
    return max_deposits


async def async_get_erc4626_max_mint(
    token: spec.Address,
    receiver: spec.Address,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> int:
    max_mint: int = await rpc.async_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['maxMint'],
        function_parameters=[receiver],
        block_number=block,
        provider=provider,
    )
    return max_mint


async def async_get_erc4626_max_mint_by_block(
    token: spec.Address,
    receiver: spec.Address,
    *,
    provider: spec.ProviderReference = None,
    blocks: typing.Sequence[spec.BlockNumberReference],
) -> typing.Sequence[int]:
    max_mints: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['maxMint'],
        function_parameters=[receiver],
        block_numbers=blocks,
        provider=provider,
    )
    return max_mints


async def async_get_erc4626s_max_mints(
    tokens: typing.Sequence[spec.Address],
    receiver: spec.Address,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> typing.Sequence[int]:
    max_mints: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_addresses=tokens,
        function_abi=erc4626_spec.erc4626_function_abis['maxMint'],
        function_parameters=[receiver],
        block_number=block,
        provider=provider,
    )
    return max_mints


async def async_get_erc4626_max_redeem(
    token: spec.Address,
    owner: spec.Address,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> int:
    max_redeem: int = await rpc.async_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['maxRedeem'],
        function_parameters=[owner],
        block_number=block,
        provider=provider,
    )
    return max_redeem


async def async_get_erc4626_max_redeem_by_block(
    token: spec.Address,
    owner: spec.Address,
    *,
    provider: spec.ProviderReference = None,
    blocks: typing.Sequence[spec.BlockNumberReference],
) -> typing.Sequence[int]:
    max_redeems: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['maxRedeem'],
        function_parameters=[owner],
        block_numbers=blocks,
        provider=provider,
    )
    return max_redeems


async def async_get_erc4626s_max_redeems(
    tokens: typing.Sequence[spec.Address],
    owner: spec.Address,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> typing.Sequence[int]:
    max_redeems: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_addresses=tokens,
        function_abi=erc4626_spec.erc4626_function_abis['maxRedem'],
        function_parameters=[owner],
        block_number=block,
        provider=provider,
    )
    return max_redeems


async def async_get_erc4626_max_withdraw(
    token: spec.Address,
    owner: spec.Address,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> int:
    max_withdraw: int = await rpc.async_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['maxWithdraw'],
        function_parameters=[owner],
        block_number=block,
        provider=provider,
    )
    return max_withdraw


async def async_get_erc4626_max_withdraw_by_block(
    token: spec.Address,
    owner: spec.Address,
    *,
    provider: spec.ProviderReference = None,
    blocks: typing.Sequence[spec.BlockNumberReference],
) -> typing.Sequence[int]:
    max_withdraws: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['maxWithdraw'],
        function_parameters=[owner],
        block_numbers=blocks,
        provider=provider,
    )
    return max_withdraws


async def async_get_erc4626s_max_withdraws(
    tokens: typing.Sequence[spec.Address],
    owner: spec.Address,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> typing.Sequence[int]:
    max_redeems: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_addresses=tokens,
        function_abi=erc4626_spec.erc4626_function_abis['maxWithdraw'],
        function_parameters=[owner],
        block_number=block,
        provider=provider,
    )
    return max_redeems


#
# # previews of deposits, mints, redeems, and withdrawals
#


async def async_preview_erc4626_deposit(
    token: spec.Address,
    assets: float | int,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> int:
    deposit: int = await rpc.async_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['previewDeposit'],
        function_parameters=[assets],
        block_number=block,
        provider=provider,
    )
    return deposit


async def async_preview_erc4626_deposit_by_block(
    token: spec.Address,
    assets: float | int,
    *,
    provider: spec.ProviderReference = None,
    blocks: typing.Sequence[spec.BlockNumberReference],
) -> typing.Sequence[int]:
    deposit: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['previewDeposit'],
        function_parameters=[assets],
        block_numbers=blocks,
        provider=provider,
    )
    return deposit


async def async_preview_erc4626s_deposits(
    tokens: typing.Sequence[spec.Address],
    assets: float | int,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> typing.Sequence[int]:
    deposits: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_addresses=tokens,
        function_abi=erc4626_spec.erc4626_function_abis['previewDeposit'],
        function_parameters=[assets],
        block_number=block,
        provider=provider,
    )
    return deposits


async def async_preview_erc4626_mint(
    token: spec.Address,
    shares: float | int,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> int:
    mint: int = await rpc.async_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['previewMint'],
        function_parameters=[shares],
        block_number=block,
        provider=provider,
    )
    return mint


async def async_preview_erc4626_mint_by_block(
    token: spec.Address,
    shares: float | int,
    *,
    provider: spec.ProviderReference = None,
    blocks: typing.Sequence[spec.BlockNumberReference],
) -> typing.Sequence[int]:
    mint: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['previewMint'],
        function_parameters=[shares],
        block_numbers=blocks,
        provider=provider,
    )
    return mint


async def async_preview_erc4626s_mints(
    tokens: typing.Sequence[spec.Address],
    shares: float | int,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> typing.Sequence[int]:
    mints: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_addresses=tokens,
        function_abi=erc4626_spec.erc4626_function_abis['previewMint'],
        function_parameters=[shares],
        block_number=block,
        provider=provider,
    )
    return mints


async def async_preview_erc4626_redeem(
    token: spec.Address,
    shares: float | int,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> int:
    redeem: int = await rpc.async_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['previewMint'],
        function_parameters=[shares],
        block_number=block,
        provider=provider,
    )
    return redeem


async def async_preview_erc4626_redeem_by_block(
    token: spec.Address,
    shares: float | int,
    *,
    provider: spec.ProviderReference = None,
    blocks: typing.Sequence[spec.BlockNumberReference],
) -> typing.Sequence[int]:
    redeem: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['previewMint'],
        function_parameters=[shares],
        block_numbers=blocks,
        provider=provider,
    )
    return redeem


async def async_preview_erc4626s_redeems(
    tokens: typing.Sequence[spec.Address],
    shares: float | int,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> typing.Sequence[int]:
    redeems: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_addresses=tokens,
        function_abi=erc4626_spec.erc4626_function_abis['previewMint'],
        function_parameters=[shares],
        block_number=block,
        provider=provider,
    )
    return redeems


async def async_preview_erc4626_withdraw(
    token: spec.Address,
    assets: float | int,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> int:
    withdraw: int = await rpc.async_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['previewDeposit'],
        function_parameters=[assets],
        block_number=block,
        provider=provider,
    )
    return withdraw


async def async_preview_erc4626_withdraw_by_block(
    token: spec.Address,
    assets: float | int,
    *,
    provider: spec.ProviderReference = None,
    blocks: typing.Sequence[spec.BlockNumberReference],
) -> typing.Sequence[int]:
    withdraw: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['previewDeposit'],
        function_parameters=[assets],
        block_numbers=blocks,
        provider=provider,
    )
    return withdraw


async def async_preview_erc4626s_withdraws(
    tokens: typing.Sequence[spec.Address],
    assets: float | int,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> typing.Sequence[int]:
    withdraws: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_addresses=tokens,
        function_abi=erc4626_spec.erc4626_function_abis['previewDeposit'],
        function_parameters=[assets],
        block_number=block,
        provider=provider,
    )
    return withdraws


#
# # total assets
#


async def async_get_erc4626_total_assets(
    token: spec.Address,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
    normalize: bool = True,
) -> int | float:
    assets: int = await rpc.async_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['totalAssets'],
        block_number=block,
        provider=provider,
    )
    if normalize:
        return await erc4626_normalize.async_normalize_erc4626_assets(
            token=token,
            assets=assets,
            provider=provider,
            block=block,
        )
    return assets


async def async_get_erc4626_total_assets_by_block(
    token: spec.Address,
    *,
    provider: spec.ProviderReference = None,
    blocks: typing.Sequence[spec.BlockNumberReference],
    normalize: bool = True,
) -> typing.Sequence[int | float]:
    assets: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_address=token,
        function_abi=erc4626_spec.erc4626_function_abis['totalAssets'],
        block_numbers=blocks,
        provider=provider,
    )
    if normalize:
        return await erc4626_normalize.async_normalize_erc4626_assets_by_block(
            token=token,
            assets=assets,
            provider=provider,
            blocks=blocks,
        )
    return assets


async def async_get_erc4626s_total_assets(
    tokens: typing.Sequence[spec.Address],
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
    normalize: bool = True,
) -> typing.Sequence[int | float]:
    assets: typing.Sequence[int] = await rpc.async_batch_eth_call(
        to_addresses=tokens,
        function_abi=erc4626_spec.erc4626_function_abis['totalAssets'],
        block_number=block,
        provider=provider,
    )
    if normalize:
        return await erc4626_normalize.async_normalize_erc4626s_assets(
            tokens=tokens,
            assets=assets,
            provider=provider,
            block=block,
        )
    return assets
