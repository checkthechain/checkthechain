import numpy as np
import pandas as pd

import tooltime

from ctc import evm
from ctc import rpc
from ctc import spec

from ctc.cli import cli_utils


def get_command_spec():
    return {
        'f': async_block_command,
        'args': [
            {'name': 'blocks', 'kwargs': {'nargs': '+'}},
            {'name': '--attributes', 'kwargs': {'nargs': '+'}},
            {'name': '--output', 'kwargs': {'default': 'stdout'}},
            {'name': '--overwrite', 'kwargs': {'action': 'store_true'}},
            {'name': '--provider', 'kwargs': {}},
        ],
    }


async def async_block_command(
    attributes,
    blocks,
    output,
    provider,
    overwrite,
):

    if attributes is None:
        # gas stats as well
        attributes = [
            'number',
            'timestamp',
            'time',
            'min_gas_price',
            'median_gas_price',
            'mean_gas_price',
            'max_gas_price',
        ]
    elif attributes == ['all']:
        attributes = list(spec.Block.__annotations__.keys())
    else:
        attributes = [
            attribute for token in attributes for attribute in token.split(',')
        ]

    # determine blocks
    export_blocks = await cli_utils.async_resolve_blocks(blocks)

    # print summary
    print('exporting from', len(export_blocks), 'blocks')
    print('- min:', min(export_blocks))
    print('- max:', max(export_blocks))
    print('- attributes:', attributes)
    print()

    # obtain data
    gas_attrs = [
        'min_gas_price',
        'median_gas_price',
        'mean_gas_price',
        'max_gas_price',
    ]
    compute_gas = any(attr in attributes for attr in gas_attrs)
    blocks_data = await rpc.async_batch_eth_get_block_by_number(
        block_numbers=export_blocks,
        include_full_transactions=compute_gas,
        overwrite=overwrite,
        provider=provider,
    )

    # format as dataframe
    df = pd.DataFrame(blocks_data)

    # special attribute: gas stats
    if compute_gas:
        gas_stats = pd.DataFrame(
            evm.get_block_gas_stats(block_data)
            for block_data in blocks_data
        )
        for gas_attr in gas_attrs:
            if gas_attr in attributes:
                df[gas_attr] = gas_stats[gas_attr]

    # special attribute: base_fee_per_gas
    if 'base_fee_per_gas' in attributes and 'base_fee_per_gas' not in df:
        df['base_fee_per_gas'] = np.nan
    if 'base_fee_per_gas' in df:
        df['base_fee_per_gas'] /= 1e9

    # special attribute: time
    if 'time' in attributes:
        df['time'] = df['timestamp'].map(tooltime.timestamp_to_iso)

    # trim attributes
    if len(attributes) > 0:
        df = df[attributes]

    # output data
    if 'number' in df:
        df = df.set_index('number')
    cli_utils.output_data(df=df, output=output, overwrite=overwrite)

    # cleanup
    await rpc.async_close_http_session()

