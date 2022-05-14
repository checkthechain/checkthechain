from __future__ import annotations

import toolsql

from ctc import config
from ctc import directory
from ctc import spec
from .. import db_spec


def get_raw_schema(datatype: db_spec.DBDatatype) -> toolsql.DBSchema:
    if datatype == 'erc20_metadata':
        from .schemas import erc20_metadata_schema_defs

        return erc20_metadata_schema_defs.erc20_metadata_schema
    elif datatype == 'block_timestamps':
        from .schemas import block_timestamps_schema_defs

        return block_timestamps_schema_defs.block_timestamps_schema
    elif datatype == 'contract_creation_blocks':
        from .schemas import contract_creation_blocks_schema_defs

        return (
            contract_creation_blocks_schema_defs.contract_creation_blocks_schema
        )
    elif datatype == 'contract_abis':
        from .schemas import contract_abis_schema_defs

        return (
            contract_abis_schema_defs.contract_abis_schema
        )
    else:
        raise Exception('unknown datatype: ' + str(datatype))


def get_prepared_schema(
    datatype: db_spec.DBDatatype,
    network: spec.NetworkReference | None = None,
) -> toolsql.DBSchema:

    # get schema
    schema = get_raw_schema(datatype)

    if network is None:
        network = config.get_default_network()

    # add network to table name
    for table_name, table in list(schema['tables'].items()):
        full_name = get_table_name(network=network, table_name=datatype)
        if table.get('name') is not None:
            table['name'] = full_name
        schema['tables'][full_name] = schema['tables'].pop(table_name)  # type: ignore

    return schema


def get_table_name(
    table_name: str,
    network: spec.NetworkReference | None = None,
) -> str:
    """get full table name, incorporating chain information"""
    if network is None:
        network = config.get_default_network()
    chain_id = directory.get_network_chain_id(network)
    return table_name + '__network_' + str(chain_id)
