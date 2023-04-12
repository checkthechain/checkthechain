from __future__ import annotations

import typing

import toolsql

from ctc import evm
from ctc import spec
from ... import schema_utils
from . import events_schema_defs


if typing.TYPE_CHECKING:
    from typing_extensions import Literal


async def async_upsert_events(
    *,
    encoded_events: typing.Sequence[spec.EncodedEvent],
    conn: toolsql.AsyncConnection,
    context: spec.Context,
) -> None:
    if len(encoded_events) == 0:
        return

    # fill missing rows
    if isinstance(encoded_events[0], dict):
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

    elif isinstance(encoded_events[0], tuple):
        as_binary = [
            event[:3]
            + tuple(
                (bytes.fromhex(value[2:]) if value is not None else None)
                for value in event[3:]
            )
            + (None,)
            for event in encoded_events
        ]

    else:
        raise Exception('invalid format for encoded_events')

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


@typing.overload
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
    binary_output_format: Literal['binary', 'prefix_hex'] = 'prefix_hex',
    topic_output_format: Literal['binary', 'prefix_hex'] = 'prefix_hex',
) -> spec.DataFrame:
    ...


@typing.overload
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
    output_format: Literal['polars'] = 'polars',
    binary_output_format: Literal['binary', 'prefix_hex'] = 'prefix_hex',
    topic_output_format: Literal['binary', 'prefix_hex'] = 'prefix_hex',
) -> spec.DataFrame:
    ...


@typing.overload
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
    output_format: toolsql.QueryOutputFormat = 'polars',
    binary_output_format: Literal['binary', 'prefix_hex'] = 'prefix_hex',
    topic_output_format: Literal['binary', 'prefix_hex'] = 'prefix_hex',
) -> toolsql.SelectOutputData:
    ...


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
    output_format: toolsql.QueryOutputFormat = 'polars',
    binary_output_format: Literal['binary', 'prefix_hex'] = 'prefix_hex',
    topic_output_format: Literal['binary', 'prefix_hex'] = 'prefix_hex',
) -> toolsql.SelectOutputData:
    # get table
    table = schema_utils.get_table_schema('events', context=context)

    # create query attribute filters
    where_equals: typing.Mapping[str, typing.Any] | None
    where_equals = {
        'contract_address': contract_address,
        'event_hash': event_hash,
        'topic1': topic1,
        'topic2': topic2,
        'topic3': topic3,
    }
    where_equals = {
        k: evm.to_binary(v)
        for k, v in where_equals.items()
        if v is not None
    }
    if len(where_equals) == 0:
        where_equals = None

    # create block range filters
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

    column_exprs = _get_columns(
        columns=columns,
        table=table,
        binary_output_format=binary_output_format,
        topic_output_format=topic_output_format,
    )

    # dispatch query
    result = await toolsql.async_select(
        conn=conn,
        table=table,
        where_equals=where_equals,
        where_lte=where_lte,
        where_gte=where_gte,
        columns=column_exprs,
        order_by=['block_number', 'transaction_index', 'log_index'],
        output_format=output_format,
    )

    return result


def _get_columns(
    *,
    columns: typing.Sequence[str] | None,
    table: toolsql.TableSchema,
    binary_output_format: Literal['binary', 'prefix_hex'] = 'prefix_hex',
    topic_output_format: Literal['binary', 'prefix_hex'] = 'prefix_hex',
) -> typing.Sequence[str] | toolsql.ColumnsExpression:
    if columns is None:
        columns = [column['name'] for column in table['columns']]
    column_exprs: toolsql.ColumnsExpression = columns
    # if binary_output_format != 'binary' or topic_output_format != 'binary':
    #     column_types = {
    #         column['name']: column['type'] for column in table['columns']
    #     }
    #     new_column: toolsql.ColumnExpression
    #     new_columns = []
    #     for column in columns:
    #         if column_types[column] == 'BLOB':

    #             if column.startswith('topic'):
    #                 if topic_output_format == 'prefix_hex':
    #                     new_column = {'column': column, 'encode': 'prefix_hex'}
    #                 elif topic_output_format == 'binary':
    #                     new_column = column
    #                 else:
    #                     raise Exception('unknown topic output format')

    #             else:
    #                 if binary_output_format == 'prefix_hex':
    #                     new_column = {'column': column, 'encode': 'prefix_hex'}
    #                 elif binary_output_format == 'binary':
    #                     new_column = column
    #                 else:
    #                     raise Exception('unknown binary output format')

    #         else:
    #             new_column = column
    #         new_columns.append(new_column)
    #     column_exprs = new_columns

    return column_exprs


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
    none_means_null: bool = False,
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
        contract_address = evm.to_binary(contract_address)
    if event_hash is not None:
        event_hash = evm.to_binary(event_hash)
    if topic1 is not None:
        topic1 = evm.to_binary(topic1)
    if topic2 is not None:
        topic2 = evm.to_binary(topic2)
    if topic3 is not None:
        topic3 = evm.to_binary(topic3)

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
            if where_equals is None:
                where_equals = {}
            where_equals['start_block'] = start_block
    if end_block is not None:
        if blocks_mean_bounds:
            where_lte = {'start_block': end_block}
        else:
            if where_equals is None:
                where_equals = {}
            where_equals['end_block'] = end_block

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

