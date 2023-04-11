from __future__ import annotations

import asyncio

from ctc import config
from ctc import evm
from ctc import spec
from . import safe_spec


async def async_get_all_safes(
    *,
    start_block: spec.BlockReference | None = None,
    end_block: spec.BlockReference | None = None,
    context: spec.Context = None,
) -> spec.DataFrame:

    import polars as pl

    safes__1_1, safes__1_3 = await asyncio.gather(
        async_get_all_safes__1_1(
            start_block=start_block, end_block=end_block, context=context
        ),
        async_get_all_safes__1_3(
            start_block=start_block, end_block=end_block, context=context
        ),
    )

    return pl.concat([safes__1_1, safes__1_3])


async def async_get_all_safes__1_1(
    factory: spec.Address | None = None,
    *,
    start_block: spec.BlockReference | None = None,
    end_block: spec.BlockReference | None = None,
    context: spec.Context | None = None,
) -> spec.DataFrame:

    import polars as pl

    chain_id = config.get_context_chain_id(context)
    if factory is None:
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
        context=context,
    )
    old_columns = [
        'arg__proxy',
        'contract_address',
        'transaction_hash',
        'block_number',
    ]
    df = df[old_columns]

    if chain_id not in safe_spec.deployments:
        raise Exception('safe 1.1.1 deployment unknown for ' + str(chain_id))
    df = df.with_columns(
        pl.lit(safe_spec.deployments[chain_id]['safe__1.1.1']).alias('implementation'),
        pl.lit('1.1').alias('version'),
    )
    new_columns = {
        'arg__proxy': 'address',
        'contract_address': 'factory',
        'block_number': 'creation_block',
        'transaction_hash': 'creation_transaction',
    }
    df = df.rename(new_columns)
    return df


async def async_get_all_safes__1_3(
    factory: spec.Address | None = None,
    *,
    start_block: spec.BlockReference | None = None,
    end_block: spec.BlockReference | None = None,
    context: spec.Context = None,
) -> spec.DataFrame:

    import polars as pl

    if factory is None:
        chain_id = config.get_context_chain_id(context)
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
        context=context,
    )
    old_columns = [
        'arg__proxy',
        'contract_address',
        'transaction_hash',
        'block_number',
        'arg__singleton',
    ]
    df = df[old_columns]
    df = df.with_columns(
        pl.lit('1.3').alias('version'),
    )
    new_columns = {
        'arg__proxy': 'address',
        'contract_address': 'factory',
        'block_number': 'creation_block',
        'transaction_hash': 'creation_transaction',
        'arg__singleton': 'implementation',
    }
    df = df.rename(new_columns)
    return df

