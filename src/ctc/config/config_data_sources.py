from __future__ import annotations

import typing

from ctc import spec
from . import config_values


def get_data_source(**tags: typing.Any) -> spec.DataSource:
    """get data source for a given type of data

    format is WIP and subject to change
    """
    if tags.get('datatype') == 'schema_versions':

        db_config = config_values.get_db_config(schema_name=tags['datatype'])
        if db_config is None:
            raise Exception('db_config not properly set')

        return {
            'backend': 'db',
            'db_config': db_config,
        }
    elif tags.get('datatype') in [
        #
        # # evm
        'erc20_metadata',
        'block_timestamps',
        'block_gas',
        'blocks',
        'contract_abis',
        'contract_creation_blocks',
        'events',
        'transactions',
        #
        # # protocols
        'chainlink',
        '4byte',
        'dex_pools',
        'coingecko',
    ]:

        db_config = config_values.get_db_config(schema_name=tags['datatype'])
        if db_config is None:
            raise Exception('db_config not properly set')

        return {
            'backend': 'hybrid',
            'hybrid_order': [
                {'backend': 'db', 'db_config': db_config},
                {'backend': 'rpc'},
            ],
        }
    elif tags.get('datatype') == 'function_selector':
        return {
            'backend': 'hybrid',
            'hybrid_order': [
                {'backend': 'filesystem'},
                {'backend': 'rest', 'rest_endpoint': '4byte.directory'},
            ],
        }
    elif tags.get('datatype') == 'contract_abis':
        return {
            'backend': 'hybrid',
            'hybrid_order': [
                {'backend': 'filesystem'},
                {
                    'backend': 'rest',
                    'rest_endpoint': 'etherscan',
                },
            ],
            'hybrid_backfill': True,
        }
    else:
        return {'backend': 'rpc'}

