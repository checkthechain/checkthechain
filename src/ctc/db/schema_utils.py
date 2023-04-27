from __future__ import annotations

import copy
import typing

import toolsql

from ctc import config
from ctc import spec
from ctc.spec.typedefs import db_types

from . import schemas

#
# # schema lists
#


def get_admin_schema_names() -> tuple[db_types.AdminSchemaName]:
    return db_types.AdminSchemaName.__args__  # type: ignore


def get_generic_schema_names() -> tuple[db_types.GenericSchemaName]:
    return db_types.GenericSchemaName.__args__  # type: ignore


def get_network_schema_names() -> tuple[db_types.NetworkSchemaName]:
    return db_types.NetworkSchemaName.__args__  # type: ignore


def get_all_schema_names() -> typing.Sequence[db_types.SchemaName]:
    schema_names = (
        get_admin_schema_names()
        + get_generic_schema_names()
        + get_network_schema_names()
    )
    return typing.cast(typing.Sequence[db_types.SchemaName], schema_names)


#
# # raw schemas
#


def get_raw_schema(schema_name: str) -> toolsql.DBSchema:
    """get raw schema, a set of tables not customized for any network"""
    schema: toolsql.DBSchemaShorthand
    if schema_name == 'block_timestamps':
        schema = schemas.block_timestamps_schema
    elif schema_name == 'block_gas':
        schema = schemas.block_gas_schema
    elif schema_name == 'blocks':
        schema = schemas.blocks_schema
    elif schema_name == 'contract_abis':
        schema = schemas.contract_abis_schema
    elif schema_name == 'contract_creation_blocks':
        schema = schemas.contract_creation_blocks_schema
    elif schema_name == 'dex_pools':
        schema = schemas.dex_pools_schema
    elif schema_name == 'erc20_metadata':
        schema = schemas.erc20_metadata_schema
    elif schema_name == 'events':
        schema = schemas.events_schema
    # elif schema_name == 'erc20_state':
    #     schema = schemas.erc20_state_schema
    elif schema_name == 'schema_versions':
        schema = schemas.schema_versions_schema
    elif schema_name == 'transactions':
        schema = schemas.transactions_schema
    #
    # # protocols
    #
    elif schema_name == '4byte':
        from ctc.protocols import fourbyte_utils

        schema = fourbyte_utils.fourbyte_schema
    elif schema_name == 'chainlink':
        from ctc.protocols.chainlink_utils import chainlink_db

        schema = chainlink_db.chainlink_schema
    elif schema_name == 'coingecko':
        from ctc.protocols.coingecko_utils import coingecko_db

        schema = coingecko_db.coingecko_schema
    else:
        raise Exception('unknown schema: ' + str(schema_name))

    return toolsql.normalize_shorthand_db_schema(schema)


#
# # prepared schemas
#


def get_prepared_schema(
    schema_name: str,
    context: spec.Context = None,
) -> toolsql.DBSchema:
    """get prepared schema, a set of tables customized for a specific network"""

    # get schema
    schema = get_raw_schema(schema_name)
    schema = copy.deepcopy(schema)

    # add network to table name
    for table_name, table in list(schema['tables'].items()):
        full_name = get_prepared_table_name(
            context=context, table_name=table_name
        )
        if table.get('name') is not None:
            table['name'] = full_name
        schema['tables'][full_name] = schema['tables'].pop(table_name)  # type: ignore

    return schema


def get_table_schema(
    table_name: str,
    context: spec.Context = None,
) -> toolsql.TableSchema:
    schema_name = _get_schema_of_raw_table(table_name)
    if schema_name in get_generic_schema_names():
        schema = get_raw_schema(schema_name=schema_name)
        return schema['tables'][table_name]
    else:
        schema = get_prepared_schema(schema_name=schema_name, context=context)
        prepared_name = get_prepared_table_name(
            context=context, table_name=table_name
        )
        return schema['tables'][prepared_name]


def get_prepared_table_name(
    table_name: str,
    context: spec.Context = None,
) -> str:
    """get full table name, incorporating chain information"""
    chain_id = config.get_context_chain_id(context)
    return 'network_' + str(chain_id) + '__' + table_name


def _get_schema_of_raw_table(table: str) -> spec.SchemaName:
    candidates = []
    for schema_name in get_all_schema_names():
        raw_schema = get_raw_schema(schema_name)
        for schema_table in raw_schema['tables'].keys():
            if table == schema_table:
                candidates.append(schema_name)

    if len(candidates) == 1:
        return candidates[0]
    elif len(candidates) == 0:
        raise Exception(
            'could not find any schema containing table ' + str(table)
        )
    else:
        raise Exception('found multiple schemas containing table ' + str(table))

