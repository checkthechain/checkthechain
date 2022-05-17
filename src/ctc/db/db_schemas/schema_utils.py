from __future__ import annotations

import copy
import typing

import toolsql

from ctc import config
from ctc import directory
from ctc import spec
from .. import db_spec


def get_raw_schema(datatype: db_spec.DBDatatype) -> toolsql.DBSchema:
    if datatype == 'block_gas_stats':
        from .schemas import block_gas_stats_schema_defs

        return block_gas_stats_schema_defs.block_gas_stats_schema
    elif datatype == 'block_timestamps':
        from .schemas import block_timestamps_schema_defs

        return block_timestamps_schema_defs.block_timestamps_schema
    elif datatype == 'blocks':
        from .schemas import blocks_schema_defs

        return blocks_schema_defs.blocks_schema
    elif datatype == 'contract_abis':
        from .schemas import contract_abis_schema_defs

        return contract_abis_schema_defs.contract_abis_schema
    elif datatype == 'contract_creation_blocks':
        from .schemas import contract_creation_blocks_schema_defs

        return (
            contract_creation_blocks_schema_defs.contract_creation_blocks_schema
        )
    elif datatype == 'erc20_metadata':
        from .schemas import erc20_metadata_schema_defs

        return erc20_metadata_schema_defs.erc20_metadata_schema
    elif datatype == 'erc20_state':
        from .schemas import erc20_state_schema_defs

        return erc20_state_schema_defs.erc20_state_schema
    else:
        raise Exception('unknown datatype: ' + str(datatype))


def get_prepared_schema(
    datatype: db_spec.DBDatatype,
    network: spec.NetworkReference | None = None,
) -> toolsql.DBSchema:

    # get schema
    schema = get_raw_schema(datatype)
    schema = copy.deepcopy(schema)

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


def get_complete_raw_schema() -> toolsql.DBSchema:
    datatypes = db_spec.get_all_datatypes()
    datatype_schemas = [
        get_raw_schema(datatype=datatype) for datatype in datatypes
    ]
    return _combine_db_schemas(datatype_schemas)


def get_complete_prepared_schema(
    networks: typing.Sequence[spec.NetworkReference] | None = None,
) -> toolsql.DBSchema:

    if networks is None:
        networks = config.get_used_networks()

    all_schemas = []
    for network in networks:
        for datatype in db_spec.get_all_datatypes():
            schema = get_prepared_schema(network=network, datatype=datatype)
            all_schemas.append(schema)

    return _combine_db_schemas(all_schemas)


def _combine_db_schemas(
    db_schemas: typing.Sequence[toolsql.DBSchema],
) -> toolsql.DBSchema:
    tables: typing.MutableMapping[str, toolsql.TableSpec] = {}
    for db_schema in db_schemas:
        for table_name, table_spec in db_schema.get('tables', {}).items():
            if table_name in tables:
                raise Exception('table name collision')
            tables[table_name] = table_spec
    combined_schema: toolsql.DBSchema = {'tables': tables}
    return combined_schema
