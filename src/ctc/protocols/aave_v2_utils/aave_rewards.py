import asyncio

import numpy as np

from ctc import evm
from ctc import rpc

from . import aave_oracle
from . import aave_spec


async def async_get_unclaimed_rewards(wallet, block=None, provider=None):
    aave_incentives_controller = aave_spec.get_aave_address(
        'IncentivesController',
        network=rpc.get_provider_network(provider),
    )

    return await rpc.async_eth_call(
        to_address=aave_incentives_controller,
        function_name='getUserUnclaimedRewards',
        function_parameters=[wallet],
        block_number=block,
        provider=provider,
    )


async def async_get_unclaimed_rewards_by_block(wallet, blocks, provider=None):
    coroutines = [
        async_get_unclaimed_rewards(
            wallet=wallet,
            block=block,
            provider=provider,
        )
        for block in blocks
    ]
    return await asyncio.gather(*coroutines)


async def async_compute_wallet_rewards(wallet, blocks, provider=None, replace_symbol=True):

    # add reward token
    reward_token = '0x4da27a545c0c5b758a6ba100e3a049001de870f5'
    reward_token_unstaked = '0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9'

    reward_unclaimed_coroutine = async_get_unclaimed_rewards_by_block(
        wallet=wallet,
        blocks=blocks,
        provider=provider,
    )
    reward_in_wallet_coroutine = evm.async_get_erc20_balance_of_by_block(
        address=wallet,
        token=reward_token,
        blocks=blocks,
        provider=provider,
    )
    reward_price_coroutine = aave_oracle.async_get_asset_price_by_block(
        asset=reward_token_unstaked,
        blocks=blocks,
        provider=provider,
    )

    (
        reward_unclaimed,
        reward_in_wallet,
        reward_price,
    ) = await asyncio.gather(
        reward_unclaimed_coroutine,
        reward_in_wallet_coroutine,
        reward_price_coroutine,
    )

    reward_unclaimed = np.array(reward_unclaimed) / 1e18
    reward_balance = reward_unclaimed + reward_in_wallet
    reward_balance_usd = reward_balance * reward_price

    if replace_symbol:
        return {
            'stkAAVE_unclaimed': reward_unclaimed,
            'stkAAVE_in_wallet': reward_in_wallet,
            'stkAAVE_balance': reward_balance,
            'stkAAVE_balance_usd': reward_balance_usd,
        }
    else:
        return {
            'reward_unclaimed': reward_unclaimed,
            'reward_in_wallet': reward_in_wallet,
            'reward_balance': reward_balance,
            'reward_balance_usd': reward_balance_usd,
        }

