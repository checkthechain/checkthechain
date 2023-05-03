from __future__ import annotations

import typing

from ctc import spec
from .. import abi_utils
from .. import binary_utils

if typing.TYPE_CHECKING:
    from typing_extensions import Literal
    import polars as pl


def get_event_df_columns(
    binary_format: Literal['binary', 'prefix_hex']
) -> typing.Sequence[tuple[str, pl.datatypes.DataTypeClass]]:
    import polars as pl

    if binary_format == 'binary':
        binary: pl.datatypes.DataTypeClass = pl.datatypes.Binary
    elif binary_format in ['prefix_hex', 'raw_hex']:
        binary = pl.datatypes.Utf8
    else:
        raise Exception('unknown binary format: ' + str(binary_format))

    return [
        ('block_number', pl.datatypes.Int64),
        ('transaction_index', pl.datatypes.Int64),
        ('log_index', pl.datatypes.Int64),
        ('transaction_hash', binary),
        ('contract_address', binary),
        ('event_hash', binary),
        ('topic1', binary),
        ('topic2', binary),
        ('topic3', binary),
        ('unindexed', binary),
    ]


def _parse_event_query_type(
    *,
    contract_address: spec.Address | None = None,
    event_hash: typing.Any | None = None,
    topic1: typing.Any | None = None,
    topic2: typing.Any | None = None,
    topic3: typing.Any | None = None,
) -> int:

    # parse input flags
    has_contract = contract_address is not None
    has_event_type = event_hash is not None
    has_other_topics = (
        topic1 is not None or topic2 is not None or topic3 is not None
    )

    # return type based on input flags
    if has_contract and has_event_type and not has_other_topics:
        return 1
    elif not has_contract and has_event_type and not has_other_topics:
        return 2
    elif has_contract and not has_event_type and not has_other_topics:
        return 3
    elif not has_contract and not has_event_type and not has_other_topics:
        return 4
    elif has_contract and has_event_type and has_other_topics:
        return 5
    elif not has_contract and has_event_type and has_other_topics:
        return 6
    elif has_contract and not has_event_type and has_other_topics:
        return 7
    elif not has_contract and not has_event_type and has_other_topics:
        return 8
    else:
        raise Exception('could not parse query type')


def _is_topic_binary(topic: typing.Any) -> bool:
    return isinstance(topic, bytes) or spec.is_hex_data(topic)


async def _async_parse_event_query_args(
    contract_address: spec.Address | None,
    *,
    event_name: str | None,
    event_abi: spec.EventABI | None,
    event_hash: str | None,
    named_topics: typing.Mapping[str, typing.Any] | None,
    topic1: typing.Any | None = None,
    topic2: typing.Any | None = None,
    topic3: typing.Any | None = None,
    topic1_is_binary: bool | None = None,
    topic2_is_binary: bool | None = None,
    topic3_is_binary: bool | None = None,
    context: spec.Context,
) -> tuple[typing.Sequence[bytes | None], spec.EventABI | None]:
    """compute encoded topics and event abi of query as needed"""

    # obtain event abi if needed
    if event_hash is not None and event_abi is not None:
        if event_hash != abi_utils.get_event_hash(event_abi):
            raise Exception('conflicting event hashes for given inputs')
    if topic1_is_binary is None:
        topic1_is_binary = _is_topic_binary(topic1)
    if topic2_is_binary is None:
        topic2_is_binary = _is_topic_binary(topic2)
    if topic3_is_binary is None:
        topic3_is_binary = _is_topic_binary(topic3)
    topics_decoded = (
        (topic1 is not None and not topic1_is_binary)
        or (topic2 is not None and not topic1_is_binary)
        or (topic3 is not None and not topic1_is_binary)
    )
    using_event_name = event_hash is None and event_name is not None
    if event_abi is None:
        if named_topics is not None or topics_decoded or using_event_name:
            event_abi = await abi_utils.async_get_event_abi(
                contract_address=contract_address,
                event_name=event_name,
                event_hash=event_hash,
                context=context,
            )

    # get encoded event_abi_hash
    if event_abi is not None:
        event_hash = abi_utils.get_event_hash(event_abi)
    if event_hash is not None:
        encoded_event_hash = binary_utils.to_binary(event_hash)
    else:
        encoded_event_hash = None

    # parse named event topics
    if named_topics is not None:
        if event_abi is None:
            raise Exception('could not obtain event_abi')
        names = abi_utils.get_event_indexed_names(event_abi)
        if len(names) >= 1 and names[0] in named_topics:
            topic1 = named_topics[names[0]]
            topic1_is_binary = False
        if len(names) >= 2 and names[1] in named_topics:
            topic2 = named_topics[names[1]]
            topic2_is_binary = False
        if len(names) >= 3 and names[2] in named_topics:
            topic3 = named_topics[names[2]]
            topic3_is_binary = False
        for name in named_topics.keys():
            if name not in names:
                raise Exception('unknown topic name: ' + str(name))

    # encode events
    if event_abi is not None:
        indexed_types = abi_utils.get_event_indexed_types(event_abi)
    if topic1 is not None:
        if not topic1_is_binary:
            topic1 = abi_utils.abi_encode(topic1, indexed_types[0])
        else:
            topic1 = binary_utils.to_binary(topic1, n_bytes=32)
    if topic2 is not None:
        if not topic2_is_binary:
            topic2 = abi_utils.abi_encode(topic2, indexed_types[1])
        else:
            topic2 = binary_utils.to_binary(topic2, n_bytes=32)
    if topic3 is not None:
        if not topic3_is_binary:
            topic3 = abi_utils.abi_encode(topic3, indexed_types[2])
        else:
            topic3 = binary_utils.to_binary(topic3, n_bytes=32)

    # return result
    return (encoded_event_hash, topic1, topic2, topic3), event_abi


async def async_scrub_db_queries(
    *,
    contract_address: spec.Address | None,
    event_hash: str | None = None,
    encoded_topic1: spec.BinaryData | None = None,
    encoded_topic2: spec.BinaryData | None = None,
    encoded_topic3: spec.BinaryData | None = None,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    context: spec.Context,
) -> None:
    """join contiguous and overlapping event query records together"""

    import toolsql

    from ctc import config
    from ctc import db
    from ctc.toolbox import range_utils

    # query queries
    queries = await db.async_query_event_queries(
        contract_address=contract_address,
        event_hash=event_hash,
        topic1=encoded_topic1,
        topic2=encoded_topic2,
        topic3=encoded_topic3,
        start_block=start_block,
        end_block=end_block,
        context=context,
    )
    if queries is None:
        queries = []

    # sort queries into groups
    if typing.TYPE_CHECKING:
        QueryTuple = typing.Tuple[
            int,
            typing.Union[spec.Address, None],
            typing.Union[spec.BinaryData, None],
            typing.Union[spec.BinaryData, None],
            typing.Union[spec.BinaryData, None],
            typing.Union[spec.BinaryData, None],
        ]
    query_sets: typing.MutableMapping[
        QueryTuple, typing.MutableSequence[tuple[int, int]]
    ]
    query_sets = {}
    query_ids: typing.MutableMapping[
        QueryTuple, typing.MutableMapping[tuple[int, int], int]
    ]
    query_ids = {}
    for query in queries:
        if query is None:
            continue
        query_set: QueryTuple = (
            query['query_type'],
            query['contract_address'],
            query['event_hash'],
            query['topic1'],
            query['topic2'],
            query['topic3'],
        )
        query_range = (query['start_block'], query['end_block'])
        query_sets.setdefault(query_set, [])
        query_sets[query_set].append(query_range)
        query_ids.setdefault(query_set, {})
        query_ids[query_set][query_range] = query['query_id']

    # join contiguous and overlapping queries
    to_delete: typing.MutableSequence[int] = []
    to_insert: typing.MutableSequence[spec.EventQuery] = []
    for query_set, query_ranges in query_sets.items():
        scrubbed_lists = range_utils.combine_overlapping_ranges(query_ranges)
        scrubbed = [(qr[0], qr[1]) for qr in scrubbed_lists]
        if len(scrubbed) != len(query_ranges):
            for query_range in query_ranges:
                if query_range not in scrubbed:
                    to_delete.append(query_ids[query_set][query_range])
            for query_range in scrubbed:
                if query_range not in query_ranges:
                    new_query: spec.DBEventQuery = {
                        'query_type': query_set[0],
                        'contract_address': query_set[1],
                        'event_hash': query_set[2],
                        'topic1': query_set[3],
                        'topic2': query_set[4],
                        'topic3': query_set[5],
                        'start_block': query_range[0],
                        'end_block': query_range[1],
                    }
                    to_insert.append(new_query)

    # perform db operations
    db_config = config.get_context_db_config(
        schema_name='events',
        context=context,
    )
    async with toolsql.async_connect(db_config) as conn:
        await db.async_delete_event_queries(
            query_ids=to_delete,
            context=context,
            conn=conn,
        )
        await db.async_upsert_event_queries(
            event_queries=to_insert,
            context=context,
            conn=conn,
        )


def print_event_query_summary(
    *,
    contract_address: spec.Address | None,
    event_hash: typing.Any | None,
    topic1: typing.Any | None,
    topic2: typing.Any | None,
    topic3: typing.Any | None,
    start_block: int,
    end_block: int,
) -> None:

    from ctc import cli

    cli.print_bullet(key='contract_address', value=contract_address)
    if event_hash is not None:
        event_hash = binary_utils.to_hex(event_hash)
    cli.print_bullet(key='event_hash', value=event_hash)
    cli.print_bullet(key='topic1', value=topic1)
    cli.print_bullet(key='topic2', value=topic2)
    cli.print_bullet(key='topic3', value=topic3)
    cli.print_bullet(key='start_block', value=start_block)
    cli.print_bullet(key='end_block', value=end_block)

