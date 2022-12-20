from __future__ import annotations

import typing
from typing_extensions import Literal


# admin schemas = those related to managing ctc
AdminSchemaName = Literal['schema_versions']

# generic schemas = those agnostic to network
GenericSchemaName = Literal[
    '4byte',
    'coingecko',
]

# network schemas = those that have unique data on each network
NetworkSchemaName = Literal[
    # 'block_gas_stats',
    'block_timestamps',
    'block_gas',
    'blocks',
    'contract_abis',
    'contract_creation_blocks',
    'dex_pools',
    'erc20_metadata',
    'events',
    'transactions',
    # 'erc20_state',
    # 'events',
    #
    # protocols
    'chainlink',
]

SchemaName = typing.Union[NetworkSchemaName, GenericSchemaName, AdminSchemaName]

