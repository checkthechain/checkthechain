from __future__ import annotations

import os
import typing

if typing.TYPE_CHECKING:
    import toolsql

from typing_extensions import Literal
from typing_extensions import TypedDict

from ctc import spec


BackendType = Literal['filesystem', 'rpc', 'db', 'rest', 'hybrid']
Datatype = str


class DataSource(TypedDict, total=False):
    """specifies a location to use for retrieving data

    - if source parameters are missing, system defaults are used
    - for hybrid sources, will try sources in order until one succeeds
        - will insert result into earlier source if hybrid_backfill=True
    """

    import toolsql

    # backend type
    backend: BackendType

    # source parameters
    db_config: toolsql.DBConfig
    rest_endpoint: dict[str, typing.Any]
    filesystem_root: str
    provider: spec.ProviderSpec

    # hybrid parameters
    hybrid_order: typing.Sequence[BackendType]
    hybrid_backfill: bool


def get_data_source(tags: dict[str, typing.Any]) -> DataSource:
    """get data source for a given type of data

    format is WIP and subject to change
    """
    if tags.get('datatype') in [
        'erc20_metadata',
        'block_timestamps',
        'contract_creation',
    ]:
        datatype = tags['datatype']
        return {
            'backend': 'hybrid',
            'hybrid_order': [
                {'backend': 'db', 'db_config': get_db_config(datatype)},
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
    elif tags.get('datatype') == 'contract_abi':
        return {
            'backend': 'hybrid',
            'hybrid_order': [
                {'backend': 'filesystem'},
                {
                    'backend': 'rest',
                    'rest_endpoint': {'name': 'etherscan'},
                },
            ],
            'hybrid_backfill': True,
        }
    else:
        return {'backend': 'rpc'}


def get_db_config(
    datatype: Datatype = None,
    network: spec.NetworkReference = None,
) -> 'toolsql.DBConfig':

    # for now, use same database for all datatypes and networks

    from .. import config_values

    data_root = config_values.get_data_dir()
    return {
        'dbms': 'sqlite',
        'path': os.path.join(data_root),
    }

