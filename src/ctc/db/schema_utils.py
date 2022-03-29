from __future__ import annotations

import typing

import toolsql

from ctc import directory
from ctc import spec


def get_all_datatypes() -> typing.Sequence[str]:
    return [
        'erc20_metadata',
        'block_timestamps',
    ]


def get_prepared_schema(
    datatype: str,
    network: spec.NetworkReference,
) -> toolsql.DBSchema:

    # get schema
    schema = get_raw_schema(datatype)

    # add network to table name
    for table_name, table in list(schema['tables'].items()):
        full_name = get_network_table_name(network=network, datatype=datatype)
        if table.get('name') is not None:
            table['name'] = full_name
        schema['tables'][full_name] = schema['tables'].pop(table_name)

    return schema


def get_raw_schema(datatype: str) -> toolsql.DBSchema:
    if datatype == 'erc20_metadata':
        from .datatypes import erc20_metadata

        return erc20_metadata.get_schema()
    else:
        raise Exception('unknown datatype: ' + str(datatype))


def get_network_table_name(
    table_name: str,
    network: spec.NetworkReference,
) -> str:
    chain_id = directory.get_network_chain_id(network)
    return table_name + '__network_' + str(chain_id)

