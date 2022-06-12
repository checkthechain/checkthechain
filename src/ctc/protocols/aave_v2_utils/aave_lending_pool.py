from __future__ import annotations

from ctc import evm
from ctc import rpc
from ctc import spec

from . import aave_spec


async def async_get_deposits(
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    provider: spec.ProviderSpec = None,
) -> spec.DataFrame:

    provider = rpc.get_provider(provider)
    network = provider['network']
    if network is None:
        raise Exception('could not determine network')

    if start_block is None:
        if network == 'mainnet':
            start_block = 11362579
        else:
            start_block = 0
    if end_block is None:
        end_block = 'latest'

    aave_lending_pool = aave_spec.get_aave_address(
        name='LendingPool',
        network=network,
    )
    events = await evm.async_get_events(
        contract_address=aave_lending_pool,
        event_name='Withdraw',
        start_block=start_block,
        end_block=end_block,
        verbose=False,
    )
    events['arg__amount'] = events['arg__amount'].map(int)

    return events


async def async_get_withdrawals(
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    provider: spec.ProviderSpec = None,
) -> spec.DataFrame:

    provider = rpc.get_provider(provider)
    network = provider['network']
    if network is None:
        raise Exception('could not determine network')

    if start_block is None:
        if network == 'mainnet':
            start_block = 11362579
        else:
            start_block = 0
    if end_block is None:
        end_block = 'latest'

    aave_lending_pool = aave_spec.get_aave_address(
        name='LendingPool',
        network=network,
    )
    events = await evm.async_get_events(
        contract_address=aave_lending_pool,
        event_name='Deposit',
        start_block=start_block,
        end_block=end_block,
        verbose=False,
    )
    events['arg__amount'] = events['arg__amount'].map(int)

    return events

