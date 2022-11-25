from __future__ import annotations

import typing

import toolsql

from ctc import config
from ctc import evm
from ctc import spec
from ... import schema_utils
from . import events_schema_defs

from typing_extensions import Literal


async def async_upsert_events(
    *,
    encoded_events: typing.Sequence[spec.EncodedEvent] | spec.DataFrame,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
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
    table = schema_utils.get_table_name('events', network=network)
    toolsql.insert(
        conn=conn,
        table=table,
        rows=as_binary,
        upsert='do_update',
    )


async def async_upsert_event_query(
    *,
    event_query: spec.EventQuery,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
) -> None:

    # convert to binary as needed
    as_binary = evm.binarize_fields(
        event_query,
        events_schema_defs._event_query_binary_fields,
    )

    table = schema_utils.get_table_name('event_queries', network=network)
    toolsql.insert(
        conn=conn,
        table=table,
        row=as_binary,
        upsert='do_update',
    )


async def async_upsert_event_queries(
    *,
    event_queries: typing.Sequence[spec.EventQuery],
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
) -> None:

    as_binary = [
        evm.binarize_fields(
            event_query,
            events_schema_defs._event_query_binary_fields,
        )
        for event_query in event_queries
    ]

    table = schema_utils.get_table_name('event_queries', network=network)
    toolsql.insert(
        conn=conn,
        table=table,
        rows=as_binary,
        upsert='do_update',
    )


async def async_select_events(
    *,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference | None = None,
    contract_address: spec.Address | None = None,
    event_hash: typing.Any | None = None,
    topic1: typing.Any | None = None,
    topic2: typing.Any | None = None,
    topic3: typing.Any | None = None,
    start_block: int | None = None,
    end_block: int | None = None,
    only_columns: typing.Sequence[str] | None = None,
    backend: Literal['sqlalchemy', 'connectorx'] = 'connectorx',
) -> typing.Sequence[spec.EncodedEvent] | spec.DataFrame:

    # get table
    if network is None:
        network = config.get_default_network()
    table = schema_utils.get_table_name('events', network=network)

    if backend == 'sqlalchemy':

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

        # dispatch query
        results: typing.Sequence[spec.EncodedEvent] = toolsql.select(
            conn=conn,
            table=table,
            where_equals=where_equals,
            where_lte=where_lte,
            where_gte=where_gte,
            only_columns=only_columns,
            raise_if_table_dne=False,
        )

        if results is None:
            return []
        else:
            return results

    elif backend == 'connectorx':
        # assert that all values are properly typed
        if contract_address is not None:
            contract_address = evm.binary_convert(contract_address, 'raw_hex')
        if event_hash is not None:
            event_hash = evm.binary_convert(event_hash, 'raw_hex')
        if topic1 is not None:
            topic1 = evm.binary_convert(topic1, 'raw_hex')
        if topic2 is not None:
            topic2 = evm.binary_convert(topic2, 'raw_hex')
        if topic3 is not None:
            topic3 = evm.binary_convert(topic3, 'raw_hex')
        if start_block is not None and not isinstance(start_block, int):
            raise Exception('start_block must be an integer')
        if end_block is not None and not isinstance(end_block, int):
            raise Exception('end_block must be an integer')

        # need to be careful to prevent sql injections from user input here
        assert ';' not in table
        # raw_sql = """SELECT * FROM """ + table
        raw_sql = (
            """SELECT
            block_number,
            transaction_index,
            log_index,
            '0x' || lower(hex(transaction_hash)) as transaction_hash,
            '0x' || lower(hex(contract_address)) as contract_address,
            '0x' || lower(hex(event_hash)) as event_hash,
            topic1,
            topic2,
            topic3,
            unindexed
        FROM """
            + table
        )
        where_equals_params = {
            'contract_address': contract_address,
            'event_hash': event_hash,
            'topic1': topic1,
            'topic2': topic2,
            'topic3': topic3,
        }
        where_equals_params = {
            k: v for k, v in where_equals_params.items() if v is not None
        }
        where_equals_params = {
            k: ("X'" + v + "'") if v is not None else v
            for k, v in where_equals_params.items()
        }

        # add sql clauses
        clauses = []
        for param_name, param_value in where_equals_params.items():
            if param_value is None:
                param_value = 'NULL'
            clauses.append(param_name + '=' + str(param_value))
        if start_block is not None:
            clauses.append(' block_number>=' + str(start_block))
        if end_block is not None:
            clauses.append(' block_number<=' + str(end_block))
        if len(clauses) > 0:
            raw_sql += ' WHERE ' + ' AND '.join(clauses)

        import connectorx  # type: ignore

        result: spec.DataFrame = connectorx.read_sql(
            str(conn.engine.url), raw_sql
        )
        return result

    else:
        raise Exception('unknown backend: ' + str(backend))


async def async_select_event_queries(
    *,
    conn: toolsql.SAConnection,
    query_type: int | None,
    network: spec.NetworkReference | None = None,
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
    if network is None:
        network = config.get_default_network()
    table = schema_utils.get_table_name('event_queries', network=network)

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
    results: typing.Sequence[spec.DBEventQuery] = toolsql.select(
        conn=conn,
        table=table,
        where_equals=where_equals,
        where_lte=where_lte,
        where_gte=where_gte,
        raise_if_table_dne=False,
    )

    if results is None:
        return None
    else:
        return results


async def async_delete_event_query(
    *,
    query_id: int,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference | None = None,
) -> None:

    table = schema_utils.get_table_name('event_queries', network=network)

    toolsql.delete(
        conn=conn,
        table=table,
        where_equals={'query_id': query_id},
    )


async def async_delete_event_queries(
    *,
    query_ids: typing.Sequence[int],
    conn: toolsql.SAConnection,
    network: spec.NetworkReference | None = None,
) -> None:

    table = schema_utils.get_table_name('event_queries', network=network)

    toolsql.delete(
        conn=conn,
        table=table,
        where_in={'query_id': query_ids},
    )
