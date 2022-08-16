from __future__ import annotations

import asyncio
import typing

from ctc import evm
from ctc import rpc
from ctc import spec

from . import aave_oracle
from . import aave_spec


async def async_get_unclaimed_rewards(
    wallet: spec.Address,
    *,
    block: spec.BlockNumberReference | None = None,
    provider: spec.ProviderReference = None,
) -> int:
    aave_incentives_controller = aave_spec.get_aave_address(
        'IncentivesController',
        network=rpc.get_provider_network(provider),
    )

    result = await rpc.async_eth_call(
        to_address=aave_incentives_controller,
        function_name='getUserUnclaimedRewards',
        function_parameters=[wallet],
        block_number=block,
        provider=provider,
    )

    if not isinstance(result, int):
        raise Exception('invalid rpc result')

    return result


async def async_get_unclaimed_rewards_by_block(
    wallet: spec.Address,
    blocks: typing.Sequence[spec.BlockNumberReference],
    *,
    provider: spec.ProviderReference = None,
) -> typing.Sequence[int]:
    coroutines = [
        async_get_unclaimed_rewards(
            wallet=wallet,
            block=block,
            provider=provider,
        )
        for block in blocks
    ]
    return await asyncio.gather(*coroutines)


async def async_compute_wallet_rewards(
    wallet: spec.Address,
    blocks: typing.Sequence[spec.BlockNumberReference],
    *,
    provider: spec.ProviderReference = None,
    replace_symbol: bool = True,
) -> typing.Mapping[str, spec.NumpyArray]:

    import numpy as np

    # add reward token
    reward_token = '0x4da27a545c0c5b758a6ba100e3a049001de870f5'
    reward_token_unstaked = '0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9'

    reward_unclaimed_coroutine = async_get_unclaimed_rewards_by_block(
        wallet=wallet,
        blocks=blocks,
        provider=provider,
    )
    reward_in_wallet_coroutine = evm.async_get_erc20_balance_by_block(
        wallet=wallet,
        token=reward_token,
        blocks=blocks,
        provider=provider,
    )
    reward_price_coroutine = aave_oracle.async_get_asset_price_by_block(
        asset=reward_token_unstaked,
        blocks=blocks,
        provider=provider,
    )

    (reward_unclaimed, reward_in_wallet, reward_price,) = await asyncio.gather(
        reward_unclaimed_coroutine,
        reward_in_wallet_coroutine,
        reward_price_coroutine,
    )

    reward_unclaimed_array = np.array(reward_unclaimed) / 1e18
    reward_in_wallet_array = np.array(reward_in_wallet)
    reward_balance = reward_unclaimed_array + reward_in_wallet_array
    reward_balance_usd = reward_balance * reward_price

    if replace_symbol:
        return {
            'stkAAVE_unclaimed': reward_unclaimed_array,
            'stkAAVE_in_wallet': reward_in_wallet_array,
            'stkAAVE_balance': reward_balance,
            'stkAAVE_balance_usd': reward_balance_usd,
        }
    else:
        return {
            'reward_unclaimed': reward_unclaimed_array,
            'reward_in_wallet': reward_in_wallet_array,
            'reward_balance': reward_balance,
            'reward_balance_usd': reward_balance_usd,
        }
