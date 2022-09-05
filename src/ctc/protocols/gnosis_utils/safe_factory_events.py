from __future__ import annotations

import asyncio
import typing

from ctc import config
from ctc import evm
from ctc import spec
from . import safe_spec


async def async_get_all_safes(
    *,
    start_block: spec.BlockReference | None = None,
    end_block: spec.BlockReference | None = None,
) -> typing.Sequence[safe_spec.GnosisSafeCreation]:

    safes__1_1, safes__1_3 = await asyncio.gather(
        async_get_all_safes__1_1(start_block=start_block, end_block=end_block),
        async_get_all_safes__1_3(start_block=start_block, end_block=end_block),
    )

    return [
        item
        for safes in [safes__1_1, safes__1_3]
        for item in safes
    ]


async def async_get_all_safes__1_1(
    factory: spec.Address | None = None,
    *,
    start_block: spec.BlockReference | None = None,
    end_block: spec.BlockReference | None = None,
) -> typing.Sequence[safe_spec.GnosisSafeCreation]:

    if factory is None:
        chain_id = config.get_default_network()
        if (
            chain_id not in safe_spec.deployments
            or 'factory__1.1.1' not in safe_spec.deployments[chain_id]
        ):
            raise NotImplementedError(
                'must manually specify factory addresses, see '
                + safe_spec.safe_deployments_repository
            )
        else:
            factory = safe_spec.deployments[chain_id]['factory__1.1.1']

    df = await evm.async_get_events(
        factory,
        event_name='ProxyCreation',
        start_block=start_block,
        end_block=end_block,
        keep_multiindex=False,
    )
    df = df.reset_index()
    old_columns = [
        'arg__proxy',
        'contract_address',
        'transaction_hash',
        'block_number',
    ]
    df = df[old_columns]

    chain_id = config.get_default_network()
    if chain_id not in safe_spec.deployments:
        raise Exception('safe 1.1.1 deployment unknown for ' + str(chain_id))
    df['implementation'] = safe_spec.deployments[chain_id]['safe__1.1.1']

    df['version'] = '1.1'
    new_columns = {
        'arg__proxy': 'address',
        'contract_address': 'factory',
        'block_number': 'creation_block',
        'transaction_hash': 'creation_transaction',
    }
    df = df.rename(columns=new_columns)
    return df.to_dict(orient='records')  # type: ignore


async def async_get_all_safes__1_3(
    factory: spec.Address | None = None,
    *,
    start_block: spec.BlockReference | None = None,
    end_block: spec.BlockReference | None = None,
) -> typing.Sequence[safe_spec.GnosisSafeCreation]:

    if factory is None:
        chain_id = config.get_default_network()
        if (
            chain_id not in safe_spec.deployments
            or 'factory__1.3.0' not in safe_spec.deployments[chain_id]
        ):
            raise NotImplementedError(
                'must manually specify factory addresses, see '
                + safe_spec.safe_deployments_repository
            )
        else:
            factory = safe_spec.deployments[chain_id]['factory__1.3.0']

    df = await evm.async_get_events(
        factory,
        event_name='ProxyCreation',
        start_block=start_block,
        end_block=end_block,
        keep_multiindex=False,
    )
    df = df.reset_index()
    old_columns = [
        'arg__proxy',
        'contract_address',
        'transaction_hash',
        'block_number',
        'arg__singleton',
    ]
    df = df[old_columns]
    df['version'] = '1.3'
    new_columns = {
        'arg__proxy': 'address',
        'contract_address': 'factory',
        'block_number': 'creation_block',
        'transaction_hash': 'creation_transaction',
        'arg__singleton': 'implementation',
    }
    df = df.rename(columns=new_columns)
    return df.to_dict(orient='records')  # type: ignore
