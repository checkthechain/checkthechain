from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import toolsql

from typing_extensions import Literal
from typing_extensions import TypedDict

from ctc import spec
from . import config_values


BackendType = Literal['filesystem', 'rpc', 'db', 'rest', 'hybrid']


class DataSource(TypedDict, total=False):
    """specifies a location to use for retrieving data

    - if source parameters are missing, system defaults are used
    - for hybrid sources, will try sources in order until one succeeds
        - will insert result into earlier source if hybrid_backfill=True
    """

    # backend type
    backend: BackendType

    # source parameters
    db_config: toolsql.DBConfig
    rest_endpoint: dict[str, typing.Any]
    filesystem_root: str
    provider: spec.ProviderReference

    # hybrid parameters
    hybrid_order: typing.Sequence['LeafDataSource']
    hybrid_backfill: bool


class LeafDataSource(TypedDict, total=False):

    # backend type
    backend: BackendType

    # source parameters
    db_config: toolsql.DBConfig
    rest_endpoint: str
    filesystem_root: str
    provider: spec.ProviderReference


def get_data_source(**tags: typing.Any) -> DataSource:
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
        'erc20_metadata',
        'block_timestamps',
        'block_gas',
        'blocks',
        'contract_abis',
        'contract_creation_blocks',
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
    elif tags.get('datatype') == 'events':
        return {
            'backend': 'hybrid',
            'hybrid_order': [
                {'backend': 'filesystem'},
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
