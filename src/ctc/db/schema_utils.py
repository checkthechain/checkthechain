from __future__ import annotations

import copy
import typing
from typing_extensions import Literal

import toolsql

from ctc import config
from ctc import directory
from ctc import spec

from . import schemas


EVMSchemaName = Literal[
    'block_gas_stats',
    'block_timestamps',
    'blocks',
    'contract_abis',
    'contract_creation_blocks',
    'erc20_metadata',
    'erc20_state',
    # 'events',
]

AdminSchemaName = Literal['schema_updates']

SchemaName = typing.Union[EVMSchemaName, AdminSchemaName]


def get_admin_schema_names() -> tuple[AdminSchemaName]:
    return AdminSchemaName.__args__  # type: ignore


def get_evm_schema_names() -> tuple[EVMSchemaName]:
    return EVMSchemaName.__args__  # type: ignore


def get_raw_schema(schema_name: SchemaName) -> toolsql.DBSchema:
    if schema_name == 'block_gas_stats':
        return schemas.block_gas_stats_schema
    elif schema_name == 'block_timestamps':
        return schemas.block_timestamps_schema
    elif schema_name == 'blocks':
        return schemas.blocks_schema
    elif schema_name == 'contract_abis':
        return schemas.contract_abis_schema
    elif schema_name == 'contract_creation_blocks':
        return schemas.contract_creation_blocks_schema
    elif schema_name == 'erc20_metadata':
        return schemas.erc20_metadata_schema
    elif schema_name == 'erc20_state':
        return schemas.erc20_state_schema
    elif schema_name == 'schema_updates':
        return schemas.schema_updates_schema
    else:
        raise Exception('unknown schema: ' + str(schema_name))


def get_prepared_schema(
    schema_name: EVMSchemaName,
    network: spec.NetworkReference | None = None,
) -> toolsql.DBSchema:

    # get schema
    schema = get_raw_schema(schema_name)
    schema = copy.deepcopy(schema)

    if network is None:
        network = config.get_default_network()

    # add network to table name
    for table_name, table in list(schema['tables'].items()):
        full_name = get_table_name(network=network, table_name=table_name)
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
    schema_names = get_evm_schema_names()
    schemas = [
        get_raw_schema(schema_name=schema_name) for schema_name in schema_names
    ]
    return _combine_db_schemas(schemas)


def get_complete_prepared_schema(
    networks: typing.Sequence[spec.NetworkReference] | None = None,
) -> toolsql.DBSchema:

    if networks is None:
        networks = config.get_used_networks()

    all_schemas = []
    for network in networks:
        for schema_name in get_evm_schema_names():
            schema = get_prepared_schema(
                network=network, schema_name=schema_name
            )
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
