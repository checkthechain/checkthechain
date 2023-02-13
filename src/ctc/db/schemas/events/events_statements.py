from __future__ import annotations

import typing

import toolsql

from ctc import evm
from ctc import spec
from ... import schema_utils
from . import events_schema_defs

from typing_extensions import Literal


async def async_upsert_events(
    *,
    encoded_events: typing.Sequence[spec.EncodedEvent] | spec.DataFrame,
    conn: toolsql.AsyncConnection,
    context: spec.Context,
) -> None:

    if spec.is_dataframe(encoded_events):
        encoded_events = encoded_events.to_dict('records')  # type: ignore
    if typing.TYPE_CHECKING:
        encoded_events = typing.cast(
            typing.Sequence[spec.EncodedEvent],
            encoded_events,
        )

    # fill missing rows
    for event in encoded_events:
        event.setdefault('topic1', None)
        event.setdefault('topic2', None)
        event.setdefault('topic3', None)
        event.setdefault('unindexed', None)

        if (
            event.get('block_number') is None
            or event.get('transaction_index') is None
            or event.get('log_index') is None
        ):
            raise Exception('must specify full index for event')

    as_binary = [
        evm.binarize_fields(
            encoded_event,
            events_schema_defs._event_binary_fields,
        )
        for encoded_event in encoded_events
    ]
    table = schema_utils.get_table_schema('events', context=context)
    await toolsql.async_insert(
        conn=conn,
        table=table,
        rows=as_binary,
        upsert=True,
    )


async def async_upsert_event_query(
    *,
    event_query: spec.EventQuery,
    conn: toolsql.AsyncConnection,
    context: spec.Context,
) -> None:

    # convert to binary as needed
    as_binary = evm.binarize_fields(
        event_query,
        events_schema_defs._event_query_binary_fields,
    )

    table = schema_utils.get_table_schema('event_queries', context=context)
    await toolsql.async_insert(
        conn=conn,
        table=table,
        row=as_binary,
        upsert=True,
    )


async def async_upsert_event_queries(
    *,
    event_queries: typing.Sequence[spec.EventQuery],
    conn: toolsql.AsyncConnection,
    context: spec.Context,
) -> None:

    as_binary = [
        evm.binarize_fields(
            event_query,
            events_schema_defs._event_query_binary_fields,
        )
        for event_query in event_queries
    ]

    table = schema_utils.get_table_schema('event_queries', context=context)
    await toolsql.async_insert(
        conn=conn,
        table=table,
        rows=as_binary,
        upsert=True,
    )


async def async_select_events(
    *,
    conn: toolsql.AsyncConnection,
    context: spec.Context = None,
    contract_address: spec.Address | None = None,
    event_hash: typing.Any | None = None,
    topic1: typing.Any | None = None,
    topic2: typing.Any | None = None,
    topic3: typing.Any | None = None,
    start_block: int | None = None,
    end_block: int | None = None,
    columns: typing.Sequence[str] | None = None,
    backend: Literal['sqlalchemy', 'connectorx'] = 'connectorx',
    binary_output_format: Literal['binary', 'prefix_hex'] = 'prefix_hex',
    topic_output_format: Literal['binary', 'prefix_hex'] = 'prefix_hex',
) -> typing.Sequence[spec.EncodedEvent] | spec.DataFrame:

    # get table
    table = schema_utils.get_table_schema('events', context=context)
    # create filters
    where_equals: typing.Mapping[str, typing.Any] | None
    where_equals = {
        'contract_address': contract_address,
        'event_hash': event_hash,
        'topic1': topic1,
        'topic2': topic2,
        'topic3': topic3,
    }
    where_equals = {
        k: evm.binary_convert(v, 'binary')
        for k, v in where_equals.items()
        if v is not None
    }
    if len(where_equals) == 0:
        where_equals = None
    if start_block is not None:
        where_gte: typing.Mapping[str, typing.Any] | None = {
            'block_number': start_block
        }
    else:
        where_gte = None
    if end_block is not None:
        where_lte: typing.Mapping[str, typing.Any] | None = {
            'block_number': end_block
        }
    else:
        where_lte = None

    if columns is None:
        columns = [column['name'] for column in table['columns']]
    column_exprs: toolsql.ColumnsExpression = columns
    if binary_output_format != 'binary' or topic_output_format != 'binary':
        column_types = {
            column['name']: column['type'] for column in table['columns']
        }
        new_column: toolsql.ColumnExpression
        new_columns = []
        for column in columns:
            if column_types[column] == 'BLOB':
                if column.startswith('topic'):
                    if topic_output_format == 'prefix_hex':
                        new_column = {'column': column, 'encode': 'prefix_hex'}
                    else:
                        new_column = column
                else:
                    if binary_output_format == 'prefix_hex':
                        new_column = {'column': column, 'encode': 'prefix_hex'}
                    else:
                        new_column = column
            else:
                new_column = column
            new_columns.append(new_column)
        column_exprs = new_columns

    # dispatch query
    results: typing.Sequence[spec.EncodedEvent] = await toolsql.async_select(  # type: ignore
        conn=conn,
        table=table,
        where_equals=where_equals,
        where_lte=where_lte,
        where_gte=where_gte,
        columns=column_exprs,
        order_by=['block_number', 'transaction_index', 'log_index'],
    )

    if results is None:
        return []
    else:
        return results

    ##
    ## # old
    ##

    #if backend == 'sqlalchemy':

    #    raise NotImplementedError(
    #        'deprecating soon, binary format args unsupported'
    #    )

    #    # create filters
    #    where_equals: typing.Mapping[str, typing.Any] | None
    #    where_equals = {
    #        'contract_address': contract_address,
    #        'event_hash': event_hash,
    #        'topic1': topic1,
    #        'topic2': topic2,
    #        'topic3': topic3,
    #    }
    #    where_equals = {
    #        k: evm.binary_convert(v, 'binary')
    #        for k, v in where_equals.items()
    #        if v is not None
    #    }
    #    if len(where_equals) == 0:
    #        where_equals = None
    #    if start_block is not None:
    #        where_gte: typing.Mapping[str, typing.Any] | None = {
    #            'block_number': start_block
    #        }
    #    else:
    #        where_gte = None
    #    if end_block is not None:
    #        where_lte: typing.Mapping[str, typing.Any] | None = {
    #            'block_number': end_block
    #        }
    #    else:
    #        where_lte = None

    #    # dispatch query
    #    results: typing.Sequence[
    #        spec.EncodedEvent
    #    ] = await toolsql.async_select(
    #        conn=conn,
    #        table=table,
    #        where_equals=where_equals,
    #        where_lte=where_lte,
    #        where_gte=where_gte,
    #        columns=only_columns,
    #    )

    #    if results is None:
    #        return []
    #    else:
    #        return results

    #elif backend == 'connectorx':
    #    # assert that all values are properly typed
    #    if contract_address is not None:
    #        contract_address = evm.binary_convert(contract_address, 'raw_hex')
    #    if event_hash is not None:
    #        event_hash = evm.binary_convert(event_hash, 'raw_hex')
    #    if topic1 is not None:
    #        topic1 = evm.binary_convert(topic1, 'raw_hex')
    #    if topic2 is not None:
    #        topic2 = evm.binary_convert(topic2, 'raw_hex')
    #    if topic3 is not None:
    #        topic3 = evm.binary_convert(topic3, 'raw_hex')
    #    if start_block is not None and not isinstance(start_block, int):
    #        raise Exception('start_block must be an integer')
    #    if end_block is not None and not isinstance(end_block, int):
    #        raise Exception('end_block must be an integer')

    #    if only_columns is None:
    #        if binary_output_format == 'binary':
    #            raw_sql = """SELECT
    #                block_number,
    #                transaction_index,
    #                log_index,
    #                '0x' || lower(hex(transaction_hash)) as transaction_hash,
    #                '0x' || lower(hex(contract_address)) as contract_address,
    #                '0x' || lower(hex(event_hash)) as event_hash,
    #                topic1,
    #                topic2,
    #                topic3,
    #                unindexed"""
    #        elif binary_output_format == 'prefix_hex':
    #            raw_sql = """SELECT
    #                block_number,
    #                transaction_index,
    #                log_index,
    #                '0x' || lower(hex(transaction_hash)) as transaction_hash,
    #                '0x' || lower(hex(contract_address)) as contract_address,
    #                '0x' || lower(hex(event_hash)) as event_hash,
    #                '0x' || lower(hex(topic1)) as topic1,
    #                '0x' || lower(hex(topic2)) as topic2,
    #                '0x' || lower(hex(topic3)) as topic3,
    #                '0x' || lower(hex(unindexed)) as unindexed"""
    #        else:
    #            raise Exception(
    #                'unknown binary_output_format: ' + str(binary_output_format)
    #            )
    #    else:
    #        raw_sql = """SELECT block_number"""

    #        # index columns
    #        if 'transaction_index' in only_columns:
    #            raw_sql += ', transaction_index'
    #        if 'log_index' in only_columns:
    #            raw_sql += ', log_index'

    #        # standard columns
    #        if 'transaction_hash' in only_columns:
    #            raw_sql += (
    #                ", '0x' || lower(hex(transaction_hash)) as transaction_hash"
    #            )
    #        if 'contract_address' in only_columns:
    #            raw_sql += (
    #                ", '0x' || lower(hex(contract_address)) as contract_address"
    #            )
    #        if 'event_hash' in only_columns:
    #            raw_sql += ", '0x' || lower(hex(event_hash)) as event_hash"

    #        # arg columns
    #        if binary_output_format == 'binary':
    #            if 'topic1' in only_columns:
    #                raw_sql += ", topic1"
    #            if 'topic2' in only_columns:
    #                raw_sql += ", topic2"
    #            if 'topic3' in only_columns:
    #                raw_sql += ", topic3"
    #            if 'unindexed' in only_columns:
    #                raw_sql += ", unindexed"
    #        elif binary_output_format == 'prefix_hex':
    #            if 'topic1' in only_columns:
    #                raw_sql += ", '0x' || lower(hex(topic1)) as topic1"
    #            if 'topic2' in only_columns:
    #                raw_sql += ", '0x' || lower(hex(topic2)) as topic2"
    #            if 'topic3' in only_columns:
    #                raw_sql += ", '0x' || lower(hex(topic3)) as topic3"
    #            if 'unindexed' in only_columns:
    #                raw_sql += ", '0x' || lower(hex(unindexed)) as unindexed"
    #        else:
    #            raise Exception(
    #                'unknown binary_output_format: ' + str(binary_output_format)
    #            )

    #    # add table
    #    raw_sql += ' FROM ' + table

    #    where_equals_params = {
    #        'contract_address': contract_address,
    #        'event_hash': event_hash,
    #        'topic1': topic1,
    #        'topic2': topic2,
    #        'topic3': topic3,
    #    }
    #    where_equals_params = {
    #        k: v for k, v in where_equals_params.items() if v is not None
    #    }
    #    where_equals_params = {
    #        k: ("X'" + v + "'") if v is not None else v
    #        for k, v in where_equals_params.items()
    #    }

    #    # add sql clauses
    #    clauses = []
    #    for param_name, param_value in where_equals_params.items():
    #        if param_value is None:
    #            param_value = 'NULL'
    #        clauses.append(param_name + '=' + str(param_value))
    #    if start_block is not None:
    #        clauses.append(' block_number>=' + str(start_block))
    #    if end_block is not None:
    #        clauses.append(' block_number<=' + str(end_block))
    #    if len(clauses) > 0:
    #        raw_sql += ' WHERE ' + ' AND '.join(clauses)

    #    raw_sql += " ORDER BY block_number, transaction_index, log_index"

    #    import connectorx  # type: ignore

    #    # need to be careful to prevent sql injections from user input here
    #    if ';' in raw_sql:
    #        raise Exception('invalid inputs, possible sql injection detected')

    #    result: spec.DataFrame = connectorx.read_sql(
    #        str(conn.engine.url), raw_sql
    #    )
    #    return result

    #else:
    #    raise Exception('unknown backend: ' + str(backend))


async def async_select_event_queries(
    *,
    conn: toolsql.AsyncConnection,
    query_type: int | None,
    context: spec.Context = None,
    contract_address: spec.Address | spec.BinaryData | None = None,
    event_hash: typing.Any | None = None,
    topic1: typing.Any | None = None,
    topic2: typing.Any | None = None,
    topic3: typing.Any | None = None,
    start_block: int | None = None,
    end_block: int | None = None,
    none_means_null: bool = True,
    blocks_mean_bounds: bool = True,
) -> typing.Sequence[spec.DBEventQuery]:
    """return queries that match given parameters

    if start_block specified, return queries s.t. end_block >= input.start_block
    if end_block specified, return queries s.t. start_block <= input.end_block
    """

    # get table
    table = schema_utils.get_table_schema('event_queries', context=context)

    # encode inputs
    if contract_address is not None:
        contract_address = evm.binary_convert(contract_address, 'binary')
    if event_hash is not None:
        event_hash = evm.binary_convert(event_hash, 'binary')
    if topic1 is not None:
        topic1 = evm.binary_convert(topic1, 'binary')
    if topic2 is not None:
        topic2 = evm.binary_convert(topic2, 'binary')
    if topic3 is not None:
        topic3 = evm.binary_convert(topic3, 'binary')

    # create equality filters
    where_equals: typing.Mapping[str, typing.Any] | None
    where_equals = {
        'contract_address': contract_address,
        'event_hash': event_hash,
        'topic1': topic1,
        'topic2': topic2,
        'topic3': topic3,
    }
    if not none_means_null:
        where_equals = {k: v for k, v in where_equals.items() if v is not None}
    if query_type is not None:
        where_equals['query_type'] = query_type
    if len(where_equals) == 0:
        where_equals = None

    # create block number filters
    where_gte = None
    where_lte = None
    if start_block is not None:
        if blocks_mean_bounds:
            where_gte = {'end_block': start_block}
        else:
            where_equals = {'start_block': start_block}
    if end_block is not None:
        if blocks_mean_bounds:
            where_lte = {'start_block': end_block}
        else:
            where_equals = {'end_block': end_block}

    # dispatch query
    results: typing.Sequence[spec.DBEventQuery] = await toolsql.async_select(  # type: ignore
        conn=conn,
        table=table,
        where_equals=where_equals,
        where_lte=where_lte,
        where_gte=where_gte,
    )

    if results is None:
        return None
    else:
        return results


async def async_delete_event_query(
    *,
    query_id: int,
    conn: toolsql.AsyncConnection,
    context: spec.Context = None,
) -> None:

    table = schema_utils.get_table_schema('event_queries', context=context)

    await toolsql.async_delete(
        conn=conn,
        table=table,
        where_equals={'query_id': query_id},
    )


async def async_delete_event_queries(
    *,
    query_ids: typing.Sequence[int],
    conn: toolsql.AsyncConnection,
    context: spec.Context = None,
) -> None:

    table = schema_utils.get_table_schema('event_queries', context=context)

    await toolsql.async_delete(
        conn=conn,
        table=table,
        where_in={'query_id': query_ids},
    )

